"""
ranking.py
----------
Part A of the AdaptLearn ML microservice: topic importance ranking and
lightweight prerequisite inference.

Design notes
------------
- Functions here are written against duck-typed "topic-like" objects (any
  object exposing .topic_id, .topic_name, .raw_notes_text,
  .prior_exam_frequency, .syllabus_weightage, .order). This lets the module
  be unit-tested with plain dataclasses (see the __main__ block) without a
  hard runtime dependency on pydantic/FastAPI, while working transparently
  with the pydantic `Topic` model used in main.py (pydantic model instances
  support the same attribute access).
- Importance scoring combines three normalized 0-1 signals:
    1. prior_exam_frequency (min-max normalized across the corpus)
    2. syllabus_weightage (already 0-1 by contract)
    3. TF-IDF centrality (cosine similarity of a topic's notes to the
       corpus centroid) as a proxy for "how central/representative this
       topic's content is within the subject" -- topics that share a lot
       of vocabulary with the rest of the syllabus tend to be
       foundational/high-yield.
- The final score is a weighted sum, re-clipped to [0, 1]. Weights are
  exposed as constants so they can be tuned without touching call sites.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence, TYPE_CHECKING

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

if TYPE_CHECKING:
    # Only imported for type checkers; avoids a hard runtime dependency on
    # pydantic so this module can be unit-tested standalone.
    from models import Topic

# ---------------------------------------------------------------------------
# Tunable weights for the importance score. Must sum to 1.0.
# ---------------------------------------------------------------------------
WEIGHT_EXAM_FREQUENCY = 0.40
WEIGHT_SYLLABUS_WEIGHTAGE = 0.35
WEIGHT_TFIDF_CENTRALITY = 0.25

# Fraction of topics flagged as "must_ask" (used to drive medium-urgency
# filtering on the backend).
MUST_ASK_TOP_FRACTION = 0.30

# Minimum / maximum number of prerequisites to return per topic.
MIN_PREREQUISITES = 2
MAX_PREREQUISITES = 4


def _min_max_normalize(values: Sequence[float]) -> np.ndarray:
    """Normalize a sequence of floats to the [0, 1] range.

    Falls back to a constant 0.5 vector when all values are identical
    (avoids division by zero and avoids arbitrarily favoring one topic).
    """
    arr = np.array(values, dtype=float)
    lo, hi = arr.min(), arr.max()
    if hi - lo < 1e-9:
        return np.full_like(arr, 0.5)
    return (arr - lo) / (hi - lo)


def _tfidf_centrality(notes: Sequence[str]) -> np.ndarray:
    """Compute each document's cosine similarity to the corpus centroid.

    This is a cheap, dependency-light proxy for "topical centrality":
    topics whose vocabulary overlaps heavily with the rest of the subject
    corpus tend to be foundational / high-yield topics.
    """
    if len(notes) < 2:
        return np.array([1.0] * len(notes))

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(notes)
    centroid = np.asarray(tfidf_matrix.mean(axis=0))
    similarities = cosine_similarity(tfidf_matrix, centroid).flatten()
    return _min_max_normalize(similarities)


def compute_importance_scores(topics: Iterable["Topic"]) -> dict:
    """Compute a 0-1 importance_score for each topic.

    Args:
        topics: iterable of topic-like objects (see module docstring).

    Returns:
        Dict mapping topic_id -> importance_score (float, 0-1).
    """
    topics = list(topics)
    if not topics:
        return {}

    freq_norm = _min_max_normalize([t.prior_exam_frequency for t in topics])
    weightage_norm = _min_max_normalize([t.syllabus_weightage for t in topics])
    centrality_norm = _tfidf_centrality([t.raw_notes_text for t in topics])

    scores = (
        WEIGHT_EXAM_FREQUENCY * freq_norm
        + WEIGHT_SYLLABUS_WEIGHTAGE * weightage_norm
        + WEIGHT_TFIDF_CENTRALITY * centrality_norm
    )
    scores = np.clip(scores, 0.0, 1.0)

    return {t.topic_id: round(float(s), 4) for t, s in zip(topics, scores)}


def rank_topics(topics: Iterable["Topic"]) -> List[dict]:
    """Rank topics by importance_score (desc) and flag the top fraction as
    'must_ask' -- consumed by the backend for medium-urgency filtering.

    Returns:
        List of dicts: {topic_id, topic_name, importance_score, must_ask}
        sorted by importance_score descending.
    """
    topics = list(topics)
    scores = compute_importance_scores(topics)

    ranked = sorted(topics, key=lambda t: scores[t.topic_id], reverse=True)
    cutoff_idx = max(1, round(len(ranked) * MUST_ASK_TOP_FRACTION))

    result = []
    for i, t in enumerate(ranked):
        result.append(
            {
                "topic_id": t.topic_id,
                "topic_name": t.topic_name,
                "importance_score": scores[t.topic_id],
                "must_ask": i < cutoff_idx,
            }
        )
    return result


# ---------------------------------------------------------------------------
# Prerequisite inference
# ---------------------------------------------------------------------------

# Curated fallback prerequisites for topics with little/no prior syllabus
# content to compare against (e.g. the very first topic). Keyed by
# topic_name substring match (case-insensitive) for robustness against
# fixture edits.
_CURATED_FALLBACK_PREREQUISITES = {
    "introduction to operating systems": [
        "Computer Organization Basics",
        "Program vs. Process Distinction",
        "CPU & Memory Fundamentals",
    ],
}


def infer_prerequisites(
    topic: "Topic",
    all_topics: Iterable["Topic"],
    top_n: int = MAX_PREREQUISITES,
) -> List[str]:
    """Infer 2-4 prerequisite concepts for a topic using a lightweight
    heuristic: TF-IDF similarity to topics earlier in the syllabus order.

    Rationale: a topic's true prerequisites are, in practice, almost always
    a subset of what's already been taught earlier in the same subject.
    Restricting candidates to `order < topic.order` avoids "prerequisites"
    that are really just related/co-requisite topics taught later.

    Falls back to a curated list for topics with no earlier topics to draw
    from (e.g. the first topic in a subject).
    """
    all_topics = list(all_topics)
    earlier_topics = [t for t in all_topics if t.order < topic.order]

    if not earlier_topics:
        for key, fallback in _CURATED_FALLBACK_PREREQUISITES.items():
            if key in topic.topic_name.lower():
                return fallback[:top_n]
        return ["Foundational concepts for this subject (no earlier topics in syllabus)"]

    corpus = [t.raw_notes_text for t in earlier_topics] + [topic.raw_notes_text]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    topic_vector = tfidf_matrix[-1]
    earlier_vectors = tfidf_matrix[:-1]
    similarities = cosine_similarity(topic_vector, earlier_vectors).flatten()

    ranked_indices = np.argsort(similarities)[::-1]
    n_candidates = min(top_n, max(MIN_PREREQUISITES, len(earlier_topics)))
    top_indices = ranked_indices[:n_candidates]

    return [earlier_topics[i].topic_name for i in top_indices]


# ---------------------------------------------------------------------------
# Standalone smoke test (no FastAPI/pydantic dependency required)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    from dataclasses import dataclass
    from pathlib import Path

    @dataclass
    class _MockTopic:
        topic_id: str
        topic_name: str
        order: int
        prior_exam_frequency: int
        syllabus_weightage: float
        raw_notes_text: str

    fixtures_path = Path(__file__).parent / "fixtures" / "os_topics.json"
    data = json.loads(fixtures_path.read_text())
    mock_topics = [_MockTopic(**t) for t in data["topics"]]

    print("=== rank_topics ===")
    for row in rank_topics(mock_topics):
        flag = "MUST-ASK" if row["must_ask"] else "        "
        print(f"{flag}  {row['importance_score']:.4f}  {row['topic_name']}")

    print("\n=== infer_prerequisites (topic 6: Deadlocks) ===")
    target = next(t for t in mock_topics if t.topic_id == "os-t06")
    print(infer_prerequisites(target, mock_topics))

    print("\n=== infer_prerequisites (topic 1: Introduction) ===")
    target = mock_topics[0]
    print(infer_prerequisites(target, mock_topics))
