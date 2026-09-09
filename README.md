# LearnSwipe — ML / AI Implementation Guide

## 1. Where ML Actually Shows Up in This Product

The PRD has two ML-touching features, both explicitly flagged as open questions — meaning you have design freedom, but also that you should pick the *simplest viable* approach for a prototype rather than over-engineering:

1. **Fast Track — "important/must-ask" topic curation** (§8, open question 1)
2. **Micro-Learn — AI-generated short-form video content** (§8, open question 2)

For a prototype scoped to **one subject (Operating Systems, Semester 3, AIML)**, you do **not** need a trained model from scratch for either. Both are achievable with a mix of retrieval, prompting existing LLMs, and light heuristics. This keeps the MVP timeline realistic.

---

## 2. Feature 1: Fast Track Topic Importance Ranking

### 2.1 Recommended Approach: **Past-Paper Frequency Analysis + LLM Re-ranking** (hybrid, not pure ML training)

**Why not train a custom model:** you don't have enough labeled exam data for one subject to train anything robust. A hybrid retrieval + LLM approach gets you 90% of the value with a fraction of the effort.

### 2.2 Pipeline

```
[Past question papers, PDFs/scanned]
        │
        ▼
 1. OCR / text extraction  (pytesseract or a PDF text extraction lib)
        │
        ▼
 2. Question segmentation   (split into individual questions/topics)
        │
        ▼
 3. Topic tagging           (map each question to a syllabus topic —
                              use an LLM call with the syllabus as context)
        │
        ▼
 4. Frequency aggregation   (count how often each topic appears across
                              N years of papers → raw importance score)
        │
        ▼
 5. LLM re-rank/summarize   (ask an LLM to produce a ranked "must-ask
                              topics" list + a 1-line justification per topic)
        │
        ▼
 6. Store as ContentItem rows (mode=FAST_TRACK) via backend seed/batch job
```

### 2.3 Implementation Sketch (Python microservice)

```python
# ml-service/app/topic_importance.py
from collections import Counter
import anthropic

client = anthropic.Anthropic()

def tag_question_to_topic(question_text: str, syllabus_topics: list[str]) -> str:
    prompt = f"""
    Given this syllabus topic list: {syllabus_topics}
    Map the following exam question to the SINGLE most relevant topic.
    Return only the topic name, nothing else.

    Question: {question_text}
    """
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=50,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip()

def compute_topic_frequencies(questions: list[str], syllabus_topics: list[str]) -> dict:
    tags = [tag_question_to_topic(q, syllabus_topics) for q in questions]
    return dict(Counter(tags))

def rank_topics(freq_map: dict, top_n: int = 10) -> list[dict]:
    ranked = sorted(freq_map.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"topic": t, "frequency": f} for t, f in ranked]
```

This runs as an **offline batch job**, not a real-time API call — you run it once per subject when you onboard new past papers, and the backend caches the ranked list as `ContentItem` rows. Expose a thin endpoint for the backend to trigger re-computation:

```python
# app/main.py (FastAPI)
from fastapi import FastAPI
app = FastAPI()

@app.post("/ml/important-topics/compute")
def compute_important_topics(subject_id: str):
    questions = fetch_past_paper_questions(subject_id)  # from DB or file store
    syllabus = fetch_syllabus_topics(subject_id)
    freq = compute_topic_frequencies(questions, syllabus)
    ranked = rank_topics(freq)
    save_to_backend(subject_id, ranked)  # POST to main backend's content endpoint
    return {"status": "ok", "topics": ranked}
```

### 2.4 MVP Shortcut

If you don't have digitized past papers in time for the prototype, **skip step 1–4 entirely** and manually curate a "must-ask topics" list for Operating Systems (a professor/TA can do this in under an hour), then use only step 5 (LLM) to generate the accompanying condensed notes/explanations for each topic. This still demonstrates the feature convincingly in a demo.

---

## 3. Feature 2: Micro-Learn Short-Form Video Generation

### 3.1 Recommended Approach for Prototype: **Pre-generated library, not live generation**

The PRD's open question asks "pre-generated vs. on-demand" — for an MVP, **pre-generated is strongly recommended**. On-demand text-to-video generation is expensive, slow (minutes per clip), and quality is inconsistent enough to risk a bad demo. Pre-generating a fixed library for Operating Systems topics de-risks the prototype.

### 3.2 Pipeline (Pre-generation, offline)

```
[Syllabus topic] 
      │
      ▼
1. Script generation (LLM)      — generate a ~45-60 second script,
                                   conversational tone, one core idea
      │
      ▼
2. Voiceover (TTS)               — ElevenLabs / Azure TTS / Google TTS
      │
      ▼
3. Visual assembly               — simple template: animated text +
                                   b-roll/stock icons + captions
                                   (use a tool like Remotion — React-based
                                   programmatic video — for full control,
                                   or a no-code tool like Pictory/Synthesia
                                   if speed matters more than customization)
      │
      ▼
4. Caption burn-in                — Whisper (speech-to-text) to auto-generate
                                    accurate timed captions, then burn in
      │
      ▼
5. Upload to S3 + register in DB  — as ContentItem (mode=MICRO_LEARN,
                                    isAiGenerated=true)
```

**Script generation example:**
```python
def generate_short_script(topic: str, subject: str) -> str:
    prompt = f"""
    Write a 45-second video script explaining "{topic}" from {subject}
    for an engineering student cramming before an exam.
    - Conversational, high-energy tone (like a Shorts/Reels creator)
    - One core concept only, no tangents
    - End with a 1-line memorable takeaway
    Output just the spoken script, no stage directions.
    """
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text
```

**Video assembly with Remotion (recommended if the team is React-comfortable):**
- Define a `<MicroLearnVideo topic={} script={} audioUrl={} />` React component with animated text reveals synced to caption timestamps.
- Render server-side via `@remotion/renderer` in a Node script, output an `.mp4`, push to S3.
- This gives you full brand-consistent styling across all generated clips — important for a polished demo.

### 3.3 On-Demand Generation (Future Scope, not MVP)

If you later want true "generate per topic on-demand":
- Wrap the same script→TTS→Remotion pipeline behind an async job (see Backend README §5 — BullMQ job).
- Cache aggressively: once a topic's video is generated once, store and reuse it for every future user who requests that topic — you're not truly regenerating per-user, you're lazily populating the pre-generated library. This is the realistic middle ground between "fully pre-generated" and "fully on-demand."

---

## 4. Panic Toggle Tier Classification (Optional ML Enhancement, Post-MVP)

The PRD's rule-based tiering (long/medium/short by hour thresholds) is explicitly stated as fine for MVP ("mock/rule-based filtering is fine"). Do not build ML for this in the prototype. A future enhancement could replace fixed thresholds with a lightweight model that also factors in **subject difficulty** and **the user's historical pace** (e.g., "this user typically needs 6 hours per OS module, so 10 hours left behaves like 'medium' not 'long' for them specifically") — but this requires usage data you won't have until post-launch.

---

## 5. ML Service ↔ Backend Contract

Keep the ML service as a **separate internal microservice** (Python/FastAPI is natural given the LLM/TTS/video tooling ecosystem), not merged into the main NestJS backend:

| Endpoint | Direction | Purpose |
|---|---|---|
| `POST /ml/important-topics/compute` | Backend → ML | Trigger batch topic-ranking job for a subject |
| `POST /ml/generate-short` | Backend → ML | Trigger one Micro-Learn video generation (batch, pre-gen phase) |
| `GET /ml/health` | Backend → ML | Health check for job orchestration |
| *(callback)* `POST /content-items/ingest` | ML → Backend | ML pushes finished content (ranked topics, video URLs) back into the main DB via the backend's API, rather than writing to the DB directly — keeps a single source of truth for schema/validation |

This separation means the ML stack (Python, LLM SDKs, video rendering) never needs to touch the main app's request path — it only ever populates content ahead of time, which the backend then serves through the same fast, cached `/content` endpoint described in the Backend README.

---

## 6. Suggested Build Order

1. Manually curate OS topics + get syllabus text digitized (fastest path to a demoable Fast Track feature)
2. Build the LLM script-generation step for 5–10 Micro-Learn topics
3. Wire TTS + Remotion assembly for those same 5–10 topics (this is your full pre-generated Micro-Learn library for the demo)
4. Only after the above works end-to-end, build the past-paper OCR → frequency-analysis pipeline if time allows — it's the most infrastructure-heavy piece and least essential for a compelling first demo
