"""
script_gen.py
-------------
Part C of the AdaptLearn ML microservice: AI-generated short-form video
script creation ("YouTube Short"-style explainers) plus a stubbed
render pipeline.

Design notes
------------
- `call_llm()` is the single seam through which every LLM call in this
  module is routed, so the actual provider (OpenAI, Anthropic, a local
  model) can be swapped later without touching business logic. It tries,
  in order: Anthropic -> OpenAI -> a deterministic template fallback. The
  fallback means the whole service is runnable with zero API keys
  configured, which matters for the prototype.
- `generate_short_script()` does NOT hard-depend on an LLM: it builds the
  key points from `summarizer.condense()` (already implemented against
  ranking's must-ask signal), then uses `call_llm()` only to *polish* the
  hook/recap phrasing. If `call_llm()` fails or isn't configured, the
  template fallback produces a still-usable script.
- `render_video_stub()` never calls a real TTS/video API. It logs the
  intended external call payloads (as if calling ElevenLabs for narration
  audio and Remotion for templated video assembly) and returns a mock
  asset URL, per the product spec's non-functional requirement.
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import List, Optional

from summarizer import condense

logger = logging.getLogger("adaptlearn.script_gen")
logging.basicConfig(level=logging.INFO)

MAX_SCRIPT_DURATION_SEC = 60
HOOK_DURATION_SEC = 5
RECAP_DURATION_SEC = 7
MAX_KEY_POINTS = 4
MAX_WORDS_PER_POINT = 15


# ---------------------------------------------------------------------------
# call_llm abstraction
# ---------------------------------------------------------------------------
def call_llm(prompt: str, max_tokens: int = 200) -> Optional[str]:
    """Single seam for all LLM calls in this service.

    Tries Anthropic, then OpenAI, based on whichever API key is present in
    the environment. Returns None (rather than raising) if no provider is
    configured or the call fails -- callers MUST handle None by falling
    back to a deterministic template, so the service remains runnable
    without any API keys for prototype/demo purposes.
    """
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if anthropic_key:
        try:
            import anthropic  # type: ignore

            client = anthropic.Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(
                block.text for block in response.content if getattr(block, "type", None) == "text"
            ).strip()
        except Exception as exc:  # noqa: BLE001 -- deliberately broad; fallback path handles it
            logger.warning("Anthropic call_llm failed, falling back: %s", exc)

    if openai_key:
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenAI call_llm failed, falling back: %s", exc)

    logger.info("No LLM provider configured; using deterministic template fallback.")
    return None


# ---------------------------------------------------------------------------
# Data structures (plain dataclasses -- mirrored by pydantic models in
# models.py for the HTTP layer; kept dependency-light here for testability)
# ---------------------------------------------------------------------------
@dataclass
class OverlayBeat:
    timestamp_sec: float
    text: str


@dataclass
class ShortScript:
    topic_name: str
    hook_line: str
    key_points: List[str]
    recap_line: str
    narration_script: str
    overlays: List[OverlayBeat] = field(default_factory=list)
    visual_cues: List[str] = field(default_factory=list)
    estimated_duration_sec: float = 0.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _truncate_to_words(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]).rstrip(",;:") + "..."


def _template_hook(topic_name: str) -> str:
    return f"Struggling with {topic_name}? Here's everything you need to know in 60 seconds."


def _template_recap(topic_name: str, first_point: str) -> str:
    return f"Remember: for {topic_name}, the key idea is — {first_point.split('.')[0]}."


def _extract_visual_cue(point: str, topic_name: str) -> str:
    """Very lightweight keyword-based visual cue suggestion -- picks the
    longest capitalized/technical-looking token in the point as the cue
    subject. Not a real vision/LLM call; deterministic and offline-safe.
    """
    candidates = re.findall(r"\b[A-Z][a-zA-Z\-]{3,}\b", point)
    subject = max(candidates, key=len) if candidates else topic_name
    return f"diagram: {subject}"


# ---------------------------------------------------------------------------
# Main generation function
# ---------------------------------------------------------------------------
def generate_short_script(topic_name: str, topic_notes: str) -> ShortScript:
    """Generate a <=60s short-form video script from a topic's raw notes.

    Pipeline:
      1. Extract 3-4 key points via summarizer.condense() (reuses the same
         definition/salience-aware extractive logic as Part B, biased
         toward the topic's own name so points stay on-topic).
      2. Trim each point to a spoken-friendly length.
      3. Try call_llm() to polish the hook + recap into more natural,
         conversational phrasing; fall back to templates on failure/None.
      4. Allocate timestamps across hook / points / recap to build
         timestamped on-screen text overlays.
      5. Derive a simple visual cue per beat.
    """
    # target_ratio is intentionally higher than Part B's default (0.25) --
    # a 60s short needs 3-4 punchy points, so we over-sample candidate
    # sentences here and then cap with MAX_KEY_POINTS below.
    raw_points = condense(topic_notes, target_ratio=0.5, boost_terms=[topic_name])
    key_points = [_truncate_to_words(p, MAX_WORDS_PER_POINT) for p in raw_points[:MAX_KEY_POINTS]]
    if not key_points:
        key_points = [f"{topic_name} is a key topic in this subject."]

    llm_hook = call_llm(
        f"Write ONE short, punchy, conversational spoken hook line (max 15 words) "
        f"for a 60-second exam-revision video about '{topic_name}'. "
        f"Return only the line, no quotes."
    )
    hook_line = llm_hook.strip().strip('"') if llm_hook else _template_hook(topic_name)

    llm_recap = call_llm(
        f"Write ONE short spoken recap/takeaway line (max 15 words) for a "
        f"60-second exam-revision video about '{topic_name}', given this key "
        f"point: '{key_points[0]}'. Return only the line, no quotes."
    )
    recap_line = llm_recap.strip().strip('"') if llm_recap else _template_recap(topic_name, key_points[0])

    # --- Timestamp allocation across a <=60s beat structure ---
    remaining = MAX_SCRIPT_DURATION_SEC - HOOK_DURATION_SEC - RECAP_DURATION_SEC
    per_point_duration = max(6.0, remaining / max(1, len(key_points)))

    overlays: List[OverlayBeat] = [OverlayBeat(timestamp_sec=0.0, text=hook_line)]
    visual_cues: List[str] = [f"diagram: {topic_name} overview"]

    t = float(HOOK_DURATION_SEC)
    for point in key_points:
        overlays.append(OverlayBeat(timestamp_sec=round(t, 1), text=point))
        visual_cues.append(_extract_visual_cue(point, topic_name))
        t += per_point_duration

    recap_timestamp = min(t, MAX_SCRIPT_DURATION_SEC - RECAP_DURATION_SEC)
    overlays.append(OverlayBeat(timestamp_sec=round(recap_timestamp, 1), text=recap_line))
    visual_cues.append(f"text card: key takeaway — {topic_name}")

    narration_script = " ".join([hook_line, *key_points, recap_line])
    estimated_duration_sec = round(recap_timestamp + RECAP_DURATION_SEC, 1)

    return ShortScript(
        topic_name=topic_name,
        hook_line=hook_line,
        key_points=key_points,
        recap_line=recap_line,
        narration_script=narration_script,
        overlays=overlays,
        visual_cues=visual_cues,
        estimated_duration_sec=estimated_duration_sec,
    )


# ---------------------------------------------------------------------------
# Render stub -- logs intended external calls, never actually renders.
# ---------------------------------------------------------------------------
def render_video_stub(script: ShortScript, topic_id: str) -> dict:
    """Stubbed TTS + video assembly step.

    Logs the payloads that WOULD be sent to ElevenLabs (narration TTS) and
    Remotion (templated video assembly) in a production build, and returns
    a mock asset URL. No network calls are made.
    """
    tts_payload = {
        "provider": "ElevenLabs (stubbed)",
        "endpoint": "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        "text": script.narration_script,
        "estimated_duration_sec": script.estimated_duration_sec,
    }
    video_payload = {
        "provider": "Remotion (stubbed)",
        "template": "short_form_explainer_v1",
        "overlays": [{"t": o.timestamp_sec, "text": o.text} for o in script.overlays],
        "visual_cues": script.visual_cues,
    }

    logger.info("[render_video_stub] Would call TTS provider with payload: %s", tts_payload)
    logger.info("[render_video_stub] Would call video assembly provider with payload: %s", video_payload)

    mock_asset_url = f"https://cdn.adaptlearn.mock/shorts/{topic_id}.mp4"

    return {
        "status": "stubbed",
        "asset_url": mock_asset_url,
        "provider_call_log": {"tts_request": tts_payload, "video_request": video_payload},
    }


# ---------------------------------------------------------------------------
# Standalone smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    from pathlib import Path

    fixtures_path = Path(__file__).parent / "fixtures" / "os_topics.json"
    data = json.loads(fixtures_path.read_text())
    topic = next(t for t in data["topics"] if t["topic_id"] == "os-t08")

    script = generate_short_script(topic["topic_name"], topic["raw_notes_text"])

    print("=== ShortScript ===")
    print("Hook:", script.hook_line)
    print("Key points:")
    for p in script.key_points:
        print(" -", p)
    print("Recap:", script.recap_line)
    print(f"Estimated duration: {script.estimated_duration_sec}s")
    print("\nOverlays:")
    for o in script.overlays:
        print(f"  [{o.timestamp_sec:>5.1f}s] {o.text}")
    print("\nVisual cues:", script.visual_cues)

    print("\n=== render_video_stub ===")
    render_result = render_video_stub(script, topic["topic_id"])
    print(json.dumps({k: v for k, v in render_result.items() if k != "provider_call_log"}, indent=2))
