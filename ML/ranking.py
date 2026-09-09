import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List

# Load fixture topics
FIXTURES_PATH = Path(__file__).parent / "fixtures" / "os_topics.json"

if FIXTURES_PATH.exists():
    with open(FIXTURES_PATH, "r", encoding="utf-8") as f:
        OS_TOPICS_FIXTURE = json.load(f)
else:
    OS_TOPICS_FIXTURE = []

TOPIC_INDEX: Dict[str, Dict[str, Any]] = {t["id"]: t for t in OS_TOPICS_FIXTURE}


def compute_importance_scores(topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Computes a normalized importance score [0.0 - 1.0] for every topic in a subject.
    Weighted combination:
      - 50% Historical Exam Frequency
      - 30% Syllabus Weight
      - 20% Conceptual Depth & Prerequisite Centrality
    """
    if not topics:
        return []

    max_freq = max((t.get("prior_exam_frequency", 1) for t in topics), default=1)
    max_weight = max((t.get("syllabus_weight", 0.1) for t in topics), default=1.0)

    scored_topics = []
    for t in topics:
        freq_norm = t.get("prior_exam_frequency", 0) / max_freq if max_freq > 0 else 0
        weight_norm = t.get("syllabus_weight", 0) / max_weight if max_weight > 0 else 0
        depth = t.get("conceptual_depth", 0.5)

        score = (0.50 * freq_norm) + (0.30 * weight_norm) + (0.20 * depth)
        score_clamped = round(min(1.0, max(0.0, score)), 4)

        item = dict(t)
        item["importance_score"] = score_clamped
        scored_topics.append(item)

    return scored_topics


def rank_topics(subject_id: str = "os-sem3-aiml") -> List[Dict[str, Any]]:
    """
    Ranks all topics descending by importance score and flags the top 30% as `must_ask: true`.
    """
    subject_topics = [t for t in OS_TOPICS_FIXTURE if t.get("subject_id") == subject_id]
    if not subject_topics:
        subject_topics = OS_TOPICS_FIXTURE

    scored = compute_importance_scores(subject_topics)
    scored.sort(key=lambda x: x["importance_score"], reverse=True)

    # Top 30% cutoff
    top_count = max(1, math.ceil(len(scored) * 0.30))

    ranked = []
    for idx, item in enumerate(scored):
        is_must_ask = idx < top_count
        ranked.append({
            "id": item["id"],
            "title": item["title"],
            "order": item["order"],
            "importance_score": item["importance_score"],
            "must_ask": is_must_ask,
            "rank": idx + 1,
            "prior_exam_frequency": item.get("prior_exam_frequency", 0),
        })

    return ranked


def infer_prerequisites(topic_id: str) -> List[Dict[str, Any]]:
    """
    Infers 2-4 prerequisite concepts for a topic using explicit links & keyword dependencies.
    """
    topic = TOPIC_INDEX.get(topic_id)
    if not topic:
        return []

    results = []
    # 1. Direct explicit prerequisites
    for p in topic.get("prerequisites", []):
        if p in TOPIC_INDEX:
            target = TOPIC_INDEX[p]
            results.append({
                "concept_id": target["id"],
                "title": target["title"],
                "reason": "Direct foundational topic dependency",
            })
        else:
            results.append({
                "concept_id": None,
                "title": p,
                "reason": "Foundational course requirement",
            })

    # 2. If fewer than 2, check keyword overlaps in earlier topics
    if len(results) < 2:
        topic_keywords = set(topic.get("keywords", []))
        for other in OS_TOPICS_FIXTURE:
            if other["order"] < topic["order"] and other["id"] != topic_id:
                other_keywords = set(other.get("keywords", []))
                overlap = topic_keywords.intersection(other_keywords)
                if overlap and not any(r.get("concept_id") == other["id"] for r in results):
                    results.append({
                        "concept_id": other["id"],
                        "title": other["title"],
                        "reason": f"Shared concept bridge: {', '.join(list(overlap)[:2])}",
                    })
            if len(results) >= 3:
                break

    return results


if __name__ == "__main__":
    print("=== SMOKE TEST: Topic Importance Ranking ===")
    ranked = rank_topics()
    for item in ranked[:4]:
        flag = " [MUST ASK ⭐]" if item["must_ask"] else ""
        print(f"Rank {item['rank']}: {item['title']} (Score: {item['importance_score']}){flag}")

    print("\n=== SMOKE TEST: Prerequisite Inference ===")
    prereqs = infer_prerequisites("os-t06")
    print(f"Prerequisites for os-t06 ({TOPIC_INDEX['os-t06']['title']}):")
    for p in prereqs:
        print(f" - {p['title']} ({p['reason']})")
