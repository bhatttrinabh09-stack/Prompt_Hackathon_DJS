from datetime import datetime
import json
from typing import Any, Dict, List
import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    branch = Column(String(50), default="AIML")
    semester = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow)

    panic_sessions = relationship("PanicSession", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    swipe_events = relationship("SwipeEvent", back_populates="user", cascade="all, delete-orphan")


class PanicSession(Base):
    __tablename__ = "panic_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    exam_in_val = Column(Integer, nullable=False)
    exam_in_unit = Column(String(20), nullable=False)  # 'days' or 'hours'
    urgency_level = Column(String(20), nullable=False)  # 'low', 'medium', 'high'
    deadline_ts = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="panic_sessions")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    branch = Column(String(50), index=True, nullable=False)
    semester = Column(Integer, index=True, nullable=False)
    enabled = Column(Boolean, default=True)

    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String(50), primary_key=True)
    subject_id = Column(String(50), ForeignKey("subjects.id"), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    order_num = Column(Integer, nullable=False)
    importance_score = Column(Float, default=0.5)
    prereq_ids_json = Column(Text, default="[]")

    subject = relationship("Subject", back_populates="topics")
    assets = relationship("ContentAsset", back_populates="topic", cascade="all, delete-orphan")

    @property
    def prereq_ids(self) -> List[str]:
        try:
            return json.loads(self.prereq_ids_json) if self.prereq_ids_json else []
        except Exception:
            return []

    @prereq_ids.setter
    def prereq_ids(self, val: List[str]):
        self.prereq_ids_json = json.dumps(val)


class ContentAsset(Base):
    __tablename__ = "content_assets"

    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    topic_id = Column(String(50), ForeignKey("topics.id"), index=True, nullable=False)
    asset_type = Column(String(20), nullable=False)  # 'dense', 'fast', 'short_video'
    title = Column(String(255), nullable=False)
    est_minutes = Column(Integer, default=5)
    payload_json = Column(Text, nullable=False)

    topic = relationship("Topic", back_populates="assets")

    @property
    def payload(self) -> Dict[str, Any]:
        try:
            return json.loads(self.payload_json) if self.payload_json else {}
        except Exception:
            return {}

    @payload.setter
    def payload(self, val: Dict[str, Any]):
        self.payload_json = json.dumps(val)


class SwipeEvent(Base):
    __tablename__ = "swipe_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    topic_id = Column(String(50), nullable=False)
    card_id = Column(String(100), nullable=False)
    card_type = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)  # 'left' | 'right'
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="swipe_events")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), index=True, nullable=False)
    subject_id = Column(String(50), nullable=False)
    topic_id = Column(String(50), nullable=False)
    mode = Column(String(20), default="dense")
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="progress_records")
