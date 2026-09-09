"""
models.py
---------
Pydantic v2 request/response schemas for the AdaptLearn ML microservice.

`Topic` is the canonical in-memory representation of a syllabus topic
(loaded from fixtures/os_topics.json at startup) and is what gets passed
into ranking.py / summarizer.py / script_gen.py's duck-typed functions.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Core domain model
# ---------------------------------------------------------------------------
class Topic(BaseModel):
    topic_id: str
    topic_name: str
    order: int = Field(description="1-indexed position of this topic within the subject's syllabus")
    prior_exam_frequency: int = Field(ge=0, description="Mock signal: # of times asked in past papers")
    syllabus_weightage: float = Field(ge=0.0, le=1.0)
    raw_notes_text: str


# ---------------------------------------------------------------------------
# Part A: ranking + prerequisites
# ---------------------------------------------------------------------------
class RankedTopic(BaseModel):
    topic_id: str
    topic_name: str
    importance_score: float = Field(ge=0.0, le=1.0)
    must_ask: bool = Field(description="True for the top MUST_ASK_TOP_FRACTION of topics by score")


class RankTopicsRequest(BaseModel):
    subject_id: str


class RankTopicsResponse(BaseModel):
    subject_id: str
    ranked_topics: List[RankedTopic]


class PrerequisitesResponse(BaseModel):
    topic_id: str
    topic_name: str
    prerequisites: List[str]


# ---------------------------------------------------------------------------
# Part B: condensation
# ---------------------------------------------------------------------------
class CondenseRequest(BaseModel):
    topic_id: str
    target_ratio: float = Field(default=0.25, gt=0.0, le=1.0)


class CondenseResponse(BaseModel):
    topic_id: str
    topic_name: str
    must_ask: bool
    condensed_bullets: List[str]


# ---------------------------------------------------------------------------
# Part C: AI short-form script generation
# ---------------------------------------------------------------------------
class OverlayBeat(BaseModel):
    timestamp_sec: float
    text: str


class ShortScript(BaseModel):
    topic_name: str
    hook_line: str
    key_points: List[str]
    recap_line: str
    narration_script: str
    overlays: List[OverlayBeat]
    visual_cues: List[str]
    estimated_duration_sec: float


class GenerateShortRequest(BaseModel):
    topic_id: str


class GenerateShortResponse(BaseModel):
    topic_id: str
    script: ShortScript
    asset_url: str
    status: str
