from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Topic
from app.schemas import SwipeCardOut

router = APIRouter(prefix="", tags=["Cards"])


@router.get("/topics/{topic_id}/cards", response_model=List[SwipeCardOut])
def get_swipe_cards(topic_id: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    cards: List[SwipeCardOut] = []
    for asset in topic.assets:
        payload = asset.payload
        preview = ""
        thumbnail = None

        if asset.asset_type == "dense":
            preview = payload.get("notes", "")[:280] + "..."
        elif asset.asset_type == "fast":
            bullets = payload.get("bullets", [])
            preview = "\n".join(bullets[:4])
        elif asset.asset_type == "short_video":
            videos = payload.get("videos", [])
            if videos:
                preview = videos[0].get("caption", "Quick visual overview")
                thumbnail = videos[0].get("url")

        cards.append(
            SwipeCardOut(
                id=asset.id,
                type=asset.asset_type,
                title=f"{topic.title} ({asset.asset_type.capitalize()})",
                preview=preview,
                thumbnailUrl=thumbnail,
            )
        )

    order_map = {"fast": 0, "dense": 1, "short_video": 2}
    cards.sort(key=lambda c: order_map.get(c.type, 99))
    return cards
