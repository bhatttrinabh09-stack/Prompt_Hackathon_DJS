from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import PanicSession, User
from app.schemas import PanicCreateRequest, PanicSessionOut
from app.services.urgency import compute_urgency

router = APIRouter(prefix="", tags=["Panic"])


@router.post("/panic-session", response_model=PanicSessionOut)
def start_panic(
    req: PanicCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    val = req.value
    unit = req.unit.lower()

    now = datetime.utcnow()
    if unit == "hours":
        deadline = now + timedelta(hours=val)
    else:
        deadline = now + timedelta(days=val)

    urgency = compute_urgency(deadline)

    db.query(PanicSession).filter(
        PanicSession.user_id == user.id, PanicSession.is_active.is_(True)
    ).update({"is_active": False})

    session = PanicSession(
        user_id=user.id,
        exam_in_val=val,
        exam_in_unit=unit,
        urgency_level=urgency,
        deadline_ts=deadline,
        is_active=True,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return PanicSessionOut(
        id=session.id,
        examInValue=session.exam_in_val,
        examInUnit=session.exam_in_unit,
        urgencyLevel=session.urgency_level,
        deadline=session.deadline_ts.isoformat(),
    )


@router.get("/panic-session/active", tags=["Panic"])
def get_active_panic(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    active = (
        db.query(PanicSession)
        .filter(PanicSession.user_id == user.id, PanicSession.is_active.is_(True))
        .first()
    )
    if not active:
        return {"active": False, "session": None}

    urgency = compute_urgency(active.deadline_ts)
    return {
        "active": True,
        "session": {
            "id": active.id,
            "examInValue": active.exam_in_val,
            "examInUnit": active.exam_in_unit,
            "urgencyLevel": urgency,
            "deadline": active.deadline_ts.isoformat(),
        },
    }


@router.delete("/panic-session/{session_id}")
def end_panic(
    session_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(PanicSession)
        .filter(PanicSession.id == session_id, PanicSession.user_id == user.id)
        .first()
    )
    if session:
        session.is_active = False
        db.commit()
    return {"status": "deactivated", "session_id": session_id}
