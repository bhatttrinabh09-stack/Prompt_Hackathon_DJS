from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    branch: Optional[str] = "AIML"
    semester: Optional[int] = 3

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    branch: Optional[str] = "AIML"
    semester: Optional[int] = 3


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class BranchUpdateRequest(BaseModel):
    branch: str


class PanicCreateRequest(BaseModel):
    exam_in: Optional[int] = Field(None, alias="examIn")
    exam_in_alt: Optional[int] = Field(None, alias="exam_in")
    unit: str = "days"  # 'days' or 'hours'

    @property
    def value(self) -> int:
        if self.exam_in is not None:
            return self.exam_in
        if self.exam_in_alt is not None:
            return self.exam_in_alt
        return 3


class PanicSessionOut(BaseModel):
    id: str
    examInValue: int
    examInUnit: str
    urgencyLevel: str
    deadline: str


class SubjectOut(BaseModel):
    id: str
    name: str
    branch: str
    semester: int
    enabled: bool


class TopicOut(BaseModel):
    id: str
    subjectId: str
    title: str
    order: int


class TopicProgressOut(BaseModel):
    topicId: str
    percentComplete: float


class SubjectProgressOut(BaseModel):
    subjectId: str
    overallPercentComplete: float
    topics: List[TopicProgressOut]


class SwipeCardOut(BaseModel):
    id: str
    type: str  # 'dense', 'fast', 'short_video'
    title: str
    preview: str
    thumbnailUrl: Optional[str] = None


class SwipeEventIn(BaseModel):
    topic_id: Optional[str] = Field(None, alias="topicId")
    topic_id_alt: Optional[str] = Field(None, alias="topic_id")
    card_id: Optional[str] = Field(None, alias="cardId")
    card_id_alt: Optional[str] = Field(None, alias="card_id")
    card_type: Optional[str] = Field(None, alias="cardType")
    card_type_alt: Optional[str] = Field(None, alias="card_type")
    direction: str  # 'left' | 'right'

    def get_topic_id(self) -> str:
        return self.topic_id or self.topic_id_alt or ""

    def get_card_id(self) -> str:
        return self.card_id or self.card_id_alt or ""

    def get_card_type(self) -> str:
        return self.card_type or self.card_type_alt or "dense"


class CompleteTopicIn(BaseModel):
    topic_id: Optional[str] = Field(None, alias="topicId")
    topic_id_alt: Optional[str] = Field(None, alias="topic_id")
    mode: str = "dense"

    def get_topic_id(self) -> str:
        return self.topic_id or self.topic_id_alt or ""
