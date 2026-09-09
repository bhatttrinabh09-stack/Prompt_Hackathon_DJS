# AdaptLearn ML Service (Prototype)

Topic importance ranking, content condensation, and AI short-form video
script generation for the AdaptLearn adaptive exam-prep platform.

**Prototype scope:** Branch = AIML, Semester = 3, Subject = Operating Systems
(10 mock topics in `fixtures/os_topics.json`).

This service is designed to run **with zero external API keys or network
access** — every ML/AI step has a deterministic, CPU-only fallback, so it's
demoable out of the box. Real LLM/TTS providers are swappable behind clearly
marked seams (see "Extension points" below).

---

## Setup

```bash
python3 -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive Swagger UI.

Run the standalone module smoke tests (no server needed):
```bash
python3 ranking.py
python3 summarizer.py
python3 script_gen.py
```

---

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check + which subjects are loaded |
| POST | `/rank-topics` | Rank all topics in a subject by importance, flag top 30% as `must_ask` |
| GET | `/topics/{topic_id}/prerequisites` | Infer 2-4 prerequisite concepts for a topic |
| POST | `/condense` | Condense a topic's raw notes into bullet points at a target compression ratio |
| POST | `/generate-short` | Generate a ≤60s short-form video script (+ stubbed render call) for a topic |

### Example requests

```bash
curl -X POST localhost:8000/rank-topics \
  -H "Content-Type: application/json" \
  -d '{"subject_id": "os-sem3-aiml"}'

curl localhost:8000/topics/os-t06/prerequisites

curl -X POST localhost:8000/condense \
  -H "Content-Type: application/json" \
  -d '{"topic_id": "os-t06", "target_ratio": 0.2}'

curl -X POST localhost:8000/generate-short \
  -H "Content-Type: application/json" \
  -d '{"topic_id": "os-t08"}'
```

---

## How this maps to the product's urgency-based filtering

The backend's Recommender/Filter Engine (see the system design doc) owns the
actual urgency-tier decision logic, but it is driven entirely by this
service's outputs:

| Urgency tier (backend) | What it calls here | Behavior |
|---|---|---|
| **Low** (>14 days to exam) | `/rank-topics` (for ordering only) | All topics, full-depth content — condensation and shorts are optional supplements, not the primary path. |
| **Medium** (3–14 days) | `/rank-topics` then `/condense` per topic | All topics returned, but `must_ask=true` topics are surfaced first / highlighted; content served is the condensed bullet form. |
| **High** (<3 days or hours) | `/rank-topics` filtered to `must_ask=true` only, then `/condense` with an aggressive `target_ratio` (e.g. 0.15) or `/generate-short` | Only the highest-importance topics are shown at all, in the shortest available format. |

`must_ask` (from `/rank-topics`) is the single signal that threads through
every downstream call — it's computed once per subject and should be cached
by the backend rather than recomputed on every request.

---

## Module map

| File | Responsibility |
|---|---|
| `main.py` | FastAPI app, routing, in-memory fixture-backed data store |
| `models.py` | Pydantic v2 request/response schemas |
| `ranking.py` | Part A — `compute_importance_scores`, `rank_topics`, `infer_prerequisites` |
| `summarizer.py` | Part B — `condense` (TF-IDF extractive), optional `abstractive_condense` |
| `script_gen.py` | Part C — `call_llm`, `generate_short_script`, `render_video_stub` |
| `fixtures/os_topics.json` | Mock corpus: 10 Operating Systems topics |

---

## Design decisions worth knowing

- **Extractive over abstractive summarization by default.** `condense()`
  uses TF-IDF sentence scoring (scikit-learn only) rather than a
  transformer pipeline, so the service has no model-download step and runs
  identically offline or online. `abstractive_condense()` in
  `summarizer.py` is a drop-in upgrade path once `transformers`/`torch`
  are available.
- **`call_llm()` is the only LLM seam.** It tries Anthropic, then OpenAI,
  based on which API key is present in the environment, and returns `None`
  on failure/absence. Every caller of `call_llm()` handles `None` with a
  deterministic template fallback — the service is fully functional with
  no keys configured.
- **`render_video_stub()` never calls a real API.** It logs the payloads
  that would be sent to ElevenLabs (TTS) and Remotion (video assembly) and
  returns a mock `asset_url`. Swap this function's internals for real SDK
  calls when ready; the response shape (`GenerateShortResponse`) doesn't
  need to change.
- **Duck-typed core functions.** `ranking.py` and `summarizer.py` operate
  on any object with the right attributes, not hard-coded to pydantic —
  this is what let every module be unit-tested standalone (`python3
  ranking.py`, etc.) without needing FastAPI installed at all.

---

## Extension points (post-prototype)

1. Replace `_load_fixtures()` in `main.py` with a call to the Content
   Service (Postgres) described in the system design doc.
2. Set `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` to activate real LLM
   polishing in `script_gen.call_llm()`.
3. Install `transformers`/`torch` and switch `main.py`'s `/condense` route
   to call `summarizer.abstractive_condense()`.
4. Replace `render_video_stub()` with real ElevenLabs + Remotion calls,
   writing rendered assets to S3/CDN and returning the real URL.
5. Move `importance_score` computation from request-time to a periodic
   batch job (as described in the pipeline doc) once `prior_exam_frequency`
   is backed by a real historical-paper dataset instead of mock ints.
