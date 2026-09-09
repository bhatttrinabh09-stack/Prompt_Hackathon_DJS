"""
main.py
-------
FastAPI entrypoint for the AdaptLearn ML microservice.

Run with:
    uvicorn main:app --reload

Endpoints (see README.md for how each one maps to the product's
urgency-based content filtering):
    GET  /health
    POST /rank-topics
    GET  /topics/{topic_id}/prerequisites
    POST /condense
    POST /generate-short
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException

from models import (
    CondenseRequest,
    CondenseResponse,
    GenerateShortRequest,
    GenerateShortResponse,
    OverlayBeat,
    PrerequisitesResponse,
    RankedTopic,
    RankTopicsRequest,
    RankTopicsResponse,
    ShortScript,
    Topic,
)
from ranking import infer_prerequisites, rank_topics
from script_gen import generate_short_script, render_video_stub
from summarizer import condense

FIXTURES_PATH = Path(__file__).parent / "fixtures" / "os_topics.json"

# ---------------------------------------------------------------------------
# In-memory data store, populated at startup from the fixtures file.
# In a non-prototype build this layer would be replaced by calls to the
# Content Service (Postgres) described in the system design doc; every
# function below only depends on this dict shape, so swapping the loader
# for a DB-backed one later is a localized change.
# ---------------------------------------------------------------------------
_TOPICS_BY_ID: Dict[str, Topic] = {}
_TOPICS_BY_SUBJECT: Dict[str, List[Topic]] = {}
_TOPIC_TO_SUBJECT: Dict[str, str] = {}


def _load_fixtures() -> None:
    data = json.loads(FIXTURES_PATH.read_text())
    subject_id = data["subject_id"]
    topics = [Topic(**t) for t in data["topics"]]

    _TOPICS_BY_SUBJECT[subject_id] = topics
    for topic in topics:
        _TOPICS_BY_ID[topic.topic_id] = topic
        _TOPIC_TO_SUBJECT[topic.topic_id] = subject_id


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_fixtures()
    yield


app = FastAPI(
    title="AdaptLearn ML Service",
    description=(
        "Topic importance ranking, must-ask flagging, content condensation, "
        "and AI short-form video script generation for the AdaptLearn "
        "adaptive exam-prep platform. Prototype scope: AIML / Sem 3 / "
        "Operating Systems."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------
def _get_topic_or_404(topic_id: str) -> Topic:
    topic = _TOPICS_BY_ID.get(topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail=f"Unknown topic_id: {topic_id!r}")
    return topic


def _get_subject_topics_or_404(subject_id: str) -> List[Topic]:
    topics = _TOPICS_BY_SUBJECT.get(subject_id)
    if not topics:
        raise HTTPException(status_code=404, detail=f"Unknown subject_id: {subject_id!r}")
    return topics


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health")
def health() -> dict:
    return {"status": "ok", "loaded_subjects": list(_TOPICS_BY_SUBJECT.keys())}


# ---------------------------------------------------------------------------
# Part A: ranking + prerequisites
# ---------------------------------------------------------------------------
@app.post("/rank-topics", response_model=RankTopicsResponse)
def rank_topics_endpoint(payload: RankTopicsRequest) -> RankTopicsResponse:
    """Returns all topics for a subject, sorted by importance_score desc,
    with a `must_ask` flag on the top 30%. The backend's Recommender/Filter
    Engine calls this (or a cached copy of its output) to decide which
    topics to surface under medium-urgency Panic Mode.
    """
    topics = _get_subject_topics_or_404(payload.subject_id)
    ranked = rank_topics(topics)
    return RankTopicsResponse(
        subject_id=payload.subject_id,
        ranked_topics=[RankedTopic(**r) for r in ranked],
    )


@app.get("/topics/{topic_id}/prerequisites", response_model=PrerequisitesResponse)
def prerequisites_endpoint(topic_id: str) -> PrerequisitesResponse:
    """Feeds the dense-mode content screen's 'Prerequisites' section."""
    topic = _get_topic_or_404(topic_id)
    subject_id = _TOPIC_TO_SUBJECT[topic_id]
    all_topics = _TOPICS_BY_SUBJECT[subject_id]
    prereqs = infer_prerequisites(topic, all_topics)
    return PrerequisitesResponse(
        topic_id=topic.topic_id, topic_name=topic.topic_name, prerequisites=prereqs
    )


# ---------------------------------------------------------------------------
# Part B: condensation
# ---------------------------------------------------------------------------
@app.post("/condense", response_model=CondenseResponse)
def condense_endpoint(payload: CondenseRequest) -> CondenseResponse:
    """Feeds the fast-mode content screen's condensed notes + must-ask
    highlighting. Also the primary lever for high-urgency Panic Mode,
    where the backend should call this with an aggressively low
    `target_ratio` (e.g. 0.15) and filter to must_ask=True topics only.
    """
    topic = _get_topic_or_404(payload.topic_id)
    subject_id = _TOPIC_TO_SUBJECT[payload.topic_id]

    ranked = rank_topics(_TOPICS_BY_SUBJECT[subject_id])
    must_ask_lookup = {r["topic_id"]: r["must_ask"] for r in ranked}

    bullets = condense(
        topic.raw_notes_text,
        target_ratio=payload.target_ratio,
        boost_terms=[topic.topic_name],
    )

    return CondenseResponse(
        topic_id=topic.topic_id,
        topic_name=topic.topic_name,
        must_ask=must_ask_lookup.get(topic.topic_id, False),
        condensed_bullets=bullets,
    )


# ---------------------------------------------------------------------------
# Part C: AI short-form script generation
# ---------------------------------------------------------------------------
@app.post("/generate-short", response_model=GenerateShortResponse)
def generate_short_endpoint(payload: GenerateShortRequest) -> GenerateShortResponse:
    """Feeds the short-video-mode content screen. Video/audio rendering is
    stubbed (see script_gen.render_video_stub) -- this returns a script
    plus a mock asset_url, ready to swap for a real TTS/render pipeline.
    """
    topic = _get_topic_or_404(payload.topic_id)

    script = generate_short_script(topic.topic_name, topic.raw_notes_text)
    render_result = render_video_stub(script, topic.topic_id)

    script_model = ShortScript(
        topic_name=script.topic_name,
        hook_line=script.hook_line,
        key_points=script.key_points,
        recap_line=script.recap_line,
        narration_script=script.narration_script,
        overlays=[
            OverlayBeat(timestamp_sec=o.timestamp_sec, text=o.text) for o in script.overlays
        ],
        visual_cues=script.visual_cues,
        estimated_duration_sec=script.estimated_duration_sec,
    )

    return GenerateShortResponse(
        topic_id=topic.topic_id,
        script=script_model,
        asset_url=render_result["asset_url"],
        status=render_result["status"],
    )
