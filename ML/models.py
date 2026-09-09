from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RankTopicsRequest(BaseModel):
    subject_id: Optional[str] = "os-sem3-aiml"


class CondenseRequest(BaseModel):
    topic_id: Optional[str] = Field(None, description="Topic ID (e.g. os-t06)")
    raw_text: Optional[str] = Field(None, description="Optional custom raw text")
    target_ratio: Optional[float] = Field(0.25, ge=0.05, le=0.8, description="Target compression ratio")


class GenerateShortRequest(BaseModel):
    topic_id: str = Field("os-t03", description="Topic ID to turn into a short video")


class RankedTopicItem(BaseModel):
    id: str
    title: str
    order: int
    importance_score: float
    must_ask: bool
    rank: int
    prior_exam_frequency: int


class RankTopicsResponse(BaseModel):
    subject_id: str
    total_topics: int
    must_ask_count: int
    topics: List[RankedTopicItem]


class PrerequisiteItem(BaseModel):
    concept_id: Optional[str] = None
    title: str
    reason: str


class PrerequisiteResponse(BaseModel):
    topic_id: str
    title: str
    prerequisites_count: int
    prerequisites: List[PrerequisiteItem]


class CondenseResponse(BaseModel):
    title: str
    target_ratio: float
    actual_ratio: float
    bullet_count: int
    bullets: List[str]
    condensed_text: str


class GenerateShortResponse(BaseModel):
    topic_id: str
    script: Dict[str, Any]
    video: Dict[str, Any]
