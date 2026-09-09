import json
import logging
import os
import re
from typing import Any, Dict, Optional
from ranking import OS_TOPICS_FIXTURE, TOPIC_INDEX

logger = logging.getLogger("adaptlearn.ml.script_gen")


def call_llm(prompt: str, system_prompt: str = "") -> Optional[str]:
    """
    Unified LLM seam: checks Anthropic API key, then OpenAI API key.
    If no keys or network fails, returns None.
    Callers always use high-quality deterministic fallback so service never breaks.
    """
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            import anthropic  # type: ignore
            client = anthropic.Anthropic(api_key=anthropic_key)
            msg = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=600,
                system=system_prompt or "You are an expert Computer Science exam tutor.",
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as e:
            logger.warning(f"Anthropic LLM call failed: {e}")

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            import urllib.request
            req_data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt or "You are an expert CS professor."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3,
            }
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=json.dumps(req_data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_key}",
                },
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.warning(f"OpenAI LLM call failed: {e}")

    return None


def generate_short_script(topic_id: str) -> Dict[str, Any]:
    """
    Generates a <=60 second high-retention micro-learning video script:
    - 0-5s: Hook (Grab student attention before exam)
    - 5-20s: Concept Beat 1 (Core definition)
    - 20-40s: Concept Beat 2 (Mechanism / Algorithm step)
    - 40-52s: Exam Trap / Must-know trick
    - 52-60s: Outro / Recap
    """
    topic = TOPIC_INDEX.get(topic_id, OS_TOPICS_FIXTURE[0])
    title = topic["title"]
    notes = topic["raw_notes"]
    keywords = ", ".join(topic.get("keywords", []))

    system_prompt = (
        "You are an elite Computer Science educator who writes viral 60-second educational reels "
        "for university exam preparation."
    )
    prompt = (
        f"Write a tight 50-60 second educational video script explaining '{title}'.\n"
        f"Topic Summary: {notes}\n"
        f"Keywords: {keywords}\n"
        f"Return strict JSON with keys: hook, beat_1, beat_2, exam_trick, outro, visual_cues."
    )

    llm_output = call_llm(prompt, system_prompt)
    if llm_output:
        try:
            parsed = json.loads(re.search(r'\{.*\}', llm_output, re.DOTALL).group(0))
            total_words = sum(len(str(v).split()) for v in parsed.values() if isinstance(v, str))
            est_seconds = round(total_words / 2.5)
            parsed["est_duration_seconds"] = min(60, max(30, est_seconds))
            parsed["word_count"] = total_words
            parsed["topic_id"] = topic["id"]
            return parsed
        except Exception:
            pass

    # Deterministic high-quality template fallback
    hook = f"Stop memorizing {title.split('(')[0].strip()} — here is what actually gets you marks on your exam."
    beat_1 = (
        f"First rule: {title.split('&')[0].strip()} exists because your CPU needs complete control over hardware safety. "
        f"When an operation triggers, hardware toggles execution state."
    )
    beat_2 = (
        f"Here is how it executes: your program traps into the kernel, the OS inspects the descriptor table, "
        f"runs the service routine, and returns before you lose a single CPU cycle."
    )
    exam_trick = (
        f"Professor's favorite exam question: Watch out for edge cases in {keywords.split(',')[0].strip()}! "
        f"Never confuse physical addresses with logical offsets in numerical problems."
    )
    outro = "Hit save to lock in this concept before your semester exam. You've got this!"

    visual_cues = [
        {"timestamp": "0:00", "direction": "Fast zoom-in on stressed student illustration with exam countdown"},
        {"timestamp": "0:06", "direction": "Split screen animated diagram showing state transition"},
        {"timestamp": "0:22", "direction": "Animated memory blocks highlighting step-by-step pointers"},
        {"timestamp": "0:42", "direction": "Flashing amber warning banner: 'MUST-ASK EXAM TRICK'"},
        {"timestamp": "0:54", "direction": "Summary checklist graphics with checkmarks"},
    ]

    total_words = len((hook + " " + beat_1 + " " + beat_2 + " " + exam_trick + " " + outro).split())
    est_seconds = round(total_words / 2.5)

    return {
        "topic_id": topic["id"],
        "title": title,
        "hook": hook,
        "beat_1": beat_1,
        "beat_2": beat_2,
        "exam_trick": exam_trick,
        "outro": outro,
        "visual_cues": visual_cues,
        "word_count": total_words,
        "est_duration_seconds": est_seconds,
        "full_narration": f"{hook} {beat_1} {beat_2} {exam_trick} {outro}",
    }


def render_video_stub(script: Dict[str, Any], topic_id: str) -> Dict[str, Any]:
    """
    Video rendering stub seam:
    Simulates sending narration to ElevenLabs TTS and layout timeline to Remotion.
    Returns rendered mock video asset metadata.
    """
    tts_payload = {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "model_id": "eleven_turbo_v2",
        "text": script.get("full_narration", ""),
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
    }
    remotion_payload = {
        "template": "ExamShortV1",
        "durationInFrames": script.get("est_duration_seconds", 50) * 30,
        "fps": 30,
        "props": {
            "title": script.get("title", ""),
            "cues": script.get("visual_cues", []),
            "subtitles": script.get("full_narration", ""),
        },
    }

    logger.info("ElevenLabs TTS Payload dispatched (stub): %s chars", len(tts_payload['text']))
    logger.info("Remotion Render Payload dispatched (stub): %s frames", remotion_payload['durationInFrames'])

    return {
        "status": "rendered",
        "render_id": f"rnd_{topic_id}_{script.get('word_count', 0)}",
        "asset_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        "thumbnail_url": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&q=80",
        "duration_seconds": script.get("est_duration_seconds", 50),
        "tts_provider": "elevenlabs_stub",
        "video_engine": "remotion_stub",
    }


if __name__ == "__main__":
    print("=== SMOKE TEST: AI Short Video Script Generation ===")
    script = generate_short_script("os-t03")
    print(f"Title: {script['title']}")
    print(f"Estimated Duration: {script['est_duration_seconds']}s ({script['word_count']} words)")
    print(f"Hook: {script['hook']}")
    print(f"Exam Trick: {script['exam_trick']}")
    print(f"Visual Cues: {len(script['visual_cues'])} markers")
    v = render_video_stub(script, "os-t03")
    print(f"Mock Video Asset URL: {v['asset_url']}")
