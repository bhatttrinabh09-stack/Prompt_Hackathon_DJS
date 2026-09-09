from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import AuthResponse, BranchUpdateRequest, LoginRequest, SignupRequest, UserOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="", tags=["Auth"])


@router.post("/auth/signup", response_model=AuthResponse)
def signup(req: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=req.name,
        email=req.email.lower(),
        password_hash=hash_password(req.password),
        branch=req.branch or "AIML",
        semester=req.semester or 3,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.email)
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/auth/login", response_model=AuthResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id, user.email)
    return AuthResponse(access_token=token, user=UserOut.model_validate(user))


@router.get("/user/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.post("/user/branch", response_model=UserOut)
def update_branch(
    req: BranchUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.branch = req.branch
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
