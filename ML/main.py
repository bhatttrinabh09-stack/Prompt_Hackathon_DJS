from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ranking import OS_TOPICS_FIXTURE, TOPIC_INDEX, rank_topics, infer_prerequisites
from summarizer import condense_topic
from script_gen import generate_short_script, render_video_stub
from models import (
    RankTopicsRequest,
    RankTopicsResponse,
    CondenseRequest,
    CondenseResponse,
    GenerateShortRequest,
    GenerateShortResponse,
    PrerequisiteResponse,
)

app = FastAPI(
    title="AdaptLearn ML & AI Service",
    description="Topic Importance Ranking, TF-IDF Text Condensation, and AI Short-Form Script Engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "online",
        "service": "adaptlearn-ml",
        "topics_loaded": len(OS_TOPICS_FIXTURE),
        "subject": "Operating Systems (AIML Sem 3)",
        "features": ["rank-topics", "prerequisites", "condense", "generate-short"],
    }


@app.post("/rank-topics", response_model=RankTopicsResponse, tags=["Part A - Ranking"])
def api_rank_topics(req: Optional[RankTopicsRequest] = None):
    subject_id = req.subject_id if req and req.subject_id else "os-sem3-aiml"
    ranked = rank_topics(subject_id)
    return {
        "subject_id": subject_id,
        "total_topics": len(ranked),
        "must_ask_count": sum(1 for r in ranked if r["must_ask"]),
        "topics": ranked,
    }


@app.get("/topics/{topic_id}/prerequisites", response_model=PrerequisiteResponse, tags=["Part A - Ranking"])
def api_get_prerequisites(topic_id: str):
    if topic_id not in TOPIC_INDEX:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_id}' not found")
    prereqs = infer_prerequisites(topic_id)
    return {
        "topic_id": topic_id,
        "title": TOPIC_INDEX[topic_id]["title"],
        "prerequisites_count": len(prereqs),
        "prerequisites": prereqs,
    }


@app.post("/condense", response_model=CondenseResponse, tags=["Part B - Condensation"])
def api_condense(req: CondenseRequest):
    target = req.topic_id or req.raw_text
    if not target:
        raise HTTPException(status_code=400, detail="Must provide either topic_id or raw_text")
    ratio = req.target_ratio or 0.25
    return condense_topic(target, target_ratio=ratio)


@app.post("/generate-short", response_model=GenerateShortResponse, tags=["Part C - AI Script Gen"])
def api_generate_short(req: GenerateShortRequest):
    if req.topic_id not in TOPIC_INDEX:
        raise HTTPException(status_code=404, detail=f"Topic '{req.topic_id}' not found")

    script = generate_short_script(req.topic_id)
    render_result = render_video_stub(script, req.topic_id)

    return {
        "topic_id": req.topic_id,
        "script": script,
        "video": render_result,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
