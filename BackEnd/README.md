# AdaptLearn — Backend (Prototype)

FastAPI backend for an adaptive exam-prep platform.
**Prototype scope:** Branch = AIML, Semester = 3, Subject = Operating Systems.

Modular architecture with SQLite / PostgreSQL support, JWT auth, Panic urgency computation, and dynamic content filtering rules.

## Setup & Run

```bash
cd BackEnd
python3 -m pip install -r requirements.txt
python3 -m app.seed
python3 test_backend.py
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation: `http://localhost:8000/docs`

## Business Rules Reference

- `urgency_level` (<72h => `high`, 72h-14d => `medium`, >14d => `low`)
- Content Filtering:
  - **High**: Drops topics with `importance_score < 0.7`; returns only shortest asset per type.
  - **Medium**: Flags `importance_score >= 0.7` as `must_ask: true`; condenses dense text to ~240 chars.
  - **Low**: Unrestricted full depth.
