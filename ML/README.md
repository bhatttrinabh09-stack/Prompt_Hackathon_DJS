# AdaptLearn ML Service (Prototype)

Topic importance ranking, content condensation, and AI short-form video script generation for the AdaptLearn adaptive exam-prep platform.

**Prototype scope:** Branch = AIML, Semester = 3, Subject = Operating Systems (10 mock topics in `fixtures/os_topics.json`).

Runs with zero external API keys or network access — every ML/AI step has a deterministic, CPU-only fallback. Real LLM / TTS providers are swappable behind clearly marked seams.

## Setup & Run

```bash
cd ML
python3 -m pip install -r requirements.txt
python3 test_ml.py
uvicorn main:app --reload --port 8001
```

Visit `http://127.0.0.1:8001/docs` for interactive Swagger UI.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Health check + topic count |
| `POST` | `/rank-topics` | Rank all topics in subject by importance, flag top 30% as `must_ask` |
| `GET` | `/topics/{topic_id}/prerequisites` | Infer 2-4 prerequisite concepts for a topic |
| `POST` | `/condense` | Condense raw notes into bullet points at target compression ratio |
| `POST` | `/generate-short` | Generate ≤60s short-form video script (+ stubbed render call) |
