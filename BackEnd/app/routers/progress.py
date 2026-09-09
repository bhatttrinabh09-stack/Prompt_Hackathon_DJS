from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_optional_user
from app.models import Topic, User, UserProgress
from app.schemas import CompleteTopicIn, SubjectProgressOut, TopicProgressOut

router = APIRouter(prefix="", tags=["Progress"])


@router.get("/progress", response_model=SubjectProgressOut)
def get_progress(
    subject_id: Optional[str] = Query("os-sem3-aiml"),
    subjectId: Optional[str] = Query(None),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    target_sub = subjectId or subject_id or "os-sem3-aiml"
    topics = db.query(Topic).filter(Topic.subject_id == target_sub).all()
    if not topics:
        return SubjectProgressOut(subjectId=target_sub, overallPercentComplete=0.0, topics=[])

    user_id = user.id if user else "usr_demo_aiml"
    progress_map = {}
    records = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.subject_id == target_sub)
        .all()
    )
    for r in records:
        if r.completed:
            progress_map[r.topic_id] = 100.0

    topic_progress_list: List[TopicProgressOut] = []
    completed_count = 0
    for t in topics:
        pct = progress_map.get(t.id, 0.0)
        if pct >= 100.0:
            completed_count += 1
        topic_progress_list.append(TopicProgressOut(topicId=t.id, percentComplete=pct))

    overall = (completed_count / len(topics)) * 100.0 if topics else 0.0

    return SubjectProgressOut(
        subjectId=target_sub,
        overallPercentComplete=round(overall, 1),
        topics=topic_progress_list,
    )


@router.post("/progress/complete")
def mark_topic_complete(
    req: CompleteTopicIn,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    user_id = user.id if user else "usr_demo_aiml"
    t_id = req.get_topic_id()
    topic = db.query(Topic).filter(Topic.id == t_id).first()
    sub_id = topic.subject_id if topic else "os-sem3-aiml"

    rec = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == user_id, UserProgress.topic_id == t_id)
        .first()
    )
    if not rec:
        rec = UserProgress(
            user_id=user_id,
            subject_id=sub_id,
            topic_id=t_id,
            mode=req.mode,
            completed=True,
        )
        db.add(rec)
    else:
        rec.completed = True
        rec.mode = req.mode
        rec.completed_at = datetime.utcnow()

    db.commit()
    return {"status": "success", "topic_id": t_id, "completed": True}
