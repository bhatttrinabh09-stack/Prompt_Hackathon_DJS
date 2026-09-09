from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Subject, Topic
from app.schemas import SubjectOut, TopicOut

router = APIRouter(prefix="", tags=["Catalog"])


@router.get("/branches")
def get_branches():
    return [
        {"id": "AIML", "name": "Artificial Intelligence & Machine Learning", "enabled": True},
        {"id": "CSE", "name": "Computer Science & Engineering", "enabled": False},
        {"id": "ECE", "name": "Electronics & Communication", "enabled": False},
        {"id": "MECH", "name": "Mechanical Engineering", "enabled": False},
    ]


@router.get("/semesters")
def get_semesters():
    return [
        {"semester": 1, "enabled": False},
        {"semester": 2, "enabled": False},
        {"semester": 3, "enabled": True},
        {"semester": 4, "enabled": False},
        {"semester": 5, "enabled": False},
        {"semester": 6, "enabled": False},
        {"semester": 7, "enabled": False},
        {"semester": 8, "enabled": False},
    ]


@router.get("/subjects", response_model=List[SubjectOut])
def get_subjects(
    branch: str = Query("AIML"),
    semester: int = Query(3),
    db: Session = Depends(get_db),
):
    subjects = (
        db.query(Subject)
        .filter(Subject.branch == branch, Subject.semester == semester)
        .all()
    )
    return [
        SubjectOut(
            id=s.id,
            name=s.name,
            branch=s.branch,
            semester=s.semester,
            enabled=s.enabled,
        )
        for s in subjects
    ]


@router.get("/subjects/{subject_id}/topics", response_model=List[TopicOut])
def get_topics(subject_id: str, db: Session = Depends(get_db)):
    topics = (
        db.query(Topic)
        .filter(Topic.subject_id == subject_id)
        .order_by(Topic.order_num)
        .all()
    )
    return [
        TopicOut(
            id=t.id,
            subjectId=t.subject_id,
            title=t.title,
            order=t.order_num,
        )
        for t in topics
    ]
