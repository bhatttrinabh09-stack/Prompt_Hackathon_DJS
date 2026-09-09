from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.security import decode_access_token

security_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db),
) -> User:
    if not auth or not auth.credentials:
        # Development fallback to demo user if not logged in
        demo_user = db.query(User).filter(User.email == "demo@adaptlearn.dev").first()
        if demo_user:
            return demo_user
        raise HTTPException(status_code=401, detail="Authentication required")

    payload = decode_access_token(auth.credentials)
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_optional_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not auth or not auth.credentials:
        return db.query(User).filter(User.email == "demo@adaptlearn.dev").first()
    try:
        payload = decode_access_token(auth.credentials)
        user_id = payload.get("sub")
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None
