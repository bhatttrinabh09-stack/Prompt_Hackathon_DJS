from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models import PanicSession, User


def compute_urgency(deadline_ts: datetime) -> str:
    """
    Computes urgency based on time delta to deadline:
      < 72h      => 'high'
      72h - 14d  => 'medium'
      > 14d      => 'low'
    """
    now = datetime.utcnow()
    diff = deadline_ts - now
    diff_hours = diff.total_seconds() / 3600.0

    if diff_hours < 72.0:
        return "high"
    elif diff_hours <= 14 * 24:
        return "medium"
    else:
        return "low"


def get_active_urgency_for_user(
    user: Optional[User], header_urgency: Optional[str], db: Session
) -> str:
    """
    Determines effective urgency:
    1. Direct live check against user's active PanicSession deadline
    2. Fallback to X-Urgency-Level header if provided
    3. Default to 'low'
    """
    if header_urgency in ("low", "medium", "high"):
        return header_urgency

    if user:
        active_session = (
            db.query(PanicSession)
            .filter(PanicSession.user_id == user.id, PanicSession.is_active.is_(True))
            .first()
        )
        if active_session:
            return compute_urgency(active_session.deadline_ts)

    return "low"
