from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine, get_db
from app.models import Subject, Topic
from app.seed import seed_database
from app.routers import auth, catalog, panic, cards, content, progress, swipe


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize and seed tables if empty
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield


app = FastAPI(
    title="AdaptLearn Backend API",
    description="Adaptive Exam-Prep Backend with Urgency-based Content Filtering (AIML / Sem 3 / Operating Systems)",
    version="1.0.0",
    lifespan=lifespan,
)

# Open CORS for mobile/Expo app development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(catalog.router)
app.include_router(panic.router)
app.include_router(cards.router)
app.include_router(content.router)
app.include_router(progress.router)
app.include_router(swipe.router)


@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    topic_count = db.query(Topic).count()
    subject_count = db.query(Subject).count()
    return {
        "status": "ok",
        "service": "adaptlearn-backend",
        "database": "connected",
        "subjects": subject_count,
        "topics": topic_count,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
