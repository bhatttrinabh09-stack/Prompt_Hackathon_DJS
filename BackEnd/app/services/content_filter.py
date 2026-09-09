from typing import Any, Dict, List, Optional
from app.config import settings
from app.models import ContentAsset, Topic


def filter_topic_content(
    topic: Topic,
    urgency_level: str,
    selected_mode: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Applies server-side urgency filtering rules:
    - HIGH:
      Topics with importance_score < IMPORTANCE_THRESHOLD (0.7) are dropped.
      Surviving topics return shortest (est_minutes) asset per type.
    - MEDIUM:
      All topics returned.
      Topics with importance_score >= 0.7 get `must_ask: true`.
      Dense text assets condensed to ~240 characters.
    - LOW:
      All topics, all content variants, no restrictions.
    - `selected_mode`:
      Filters to the specific mode requested ('dense', 'fast', 'short_video').
    """
    if urgency_level == "high" and topic.importance_score < settings.IMPORTANCE_THRESHOLD:
        return None

    assets: List[ContentAsset] = topic.assets

    if selected_mode:
        assets = [a for a in assets if a.asset_type == selected_mode]

    if not assets:
        return None

    if urgency_level == "high":
        # Shortest variant
        assets = sorted(assets, key=lambda a: a.est_minutes)
        chosen = assets[0]
        payload = dict(chosen.payload)
        payload["mode"] = chosen.asset_type
        payload["urgency_applied"] = "high"
        return payload

    elif urgency_level == "medium":
        chosen = assets[0]
        payload = dict(chosen.payload)
        payload["mode"] = chosen.asset_type
        if topic.importance_score >= settings.IMPORTANCE_THRESHOLD:
            payload["must_ask"] = True

        if chosen.asset_type == "dense" and "notes" in payload:
            raw_notes = payload["notes"]
            if len(raw_notes) > 240:
                payload["notes"] = raw_notes[:237].rsplit(" ", 1)[0] + "..."
        payload["urgency_applied"] = "medium"
        return payload

    else:
        chosen = assets[0]
        payload = dict(chosen.payload)
        payload["mode"] = chosen.asset_type
        payload["urgency_applied"] = "low"
        return payload
