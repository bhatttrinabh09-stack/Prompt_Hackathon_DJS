from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.deps import get_optional_user
from app.models import Topic, User
from app.services.content_filter import filter_topic_content
from app.services.urgency import get_active_urgency_for_user

router = APIRouter(prefix="", tags=["Content"])


@router.get("/topics/{topic_id}/content")
def get_topic_content(
    topic_id: str,
    mode: Optional[str] = Query(None),
    x_urgency_level: Optional[str] = Header(None),
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Fetches study content strictly governed by live urgency filtering rules.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    urgency = get_active_urgency_for_user(user, x_urgency_level, db)
    filtered = filter_topic_content(topic, urgency_level=urgency, selected_mode=mode)

    if filtered is None:
        raise HTTPException(
            status_code=403,
            detail=f"Topic '{topic.title}' is dropped under high exam urgency (Importance {topic.importance_score} < {settings.IMPORTANCE_THRESHOLD})",
        )

    return filtered
