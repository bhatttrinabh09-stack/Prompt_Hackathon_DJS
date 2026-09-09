from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_optional_user
from app.models import SwipeEvent, User
from app.schemas import SwipeEventIn

router = APIRouter(prefix="", tags=["Telemetry"])


@router.post("/swipe-event")
def record_swipe_event(
    event: SwipeEventIn,
    user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    user_id = user.id if user else "usr_anon"
    ev = SwipeEvent(
        user_id=user_id,
        topic_id=event.get_topic_id(),
        card_id=event.get_card_id(),
        card_type=event.get_card_type(),
        direction=event.direction,
    )
    db.add(ev)
    db.commit()
    return {"status": "recorded", "direction": event.direction}
