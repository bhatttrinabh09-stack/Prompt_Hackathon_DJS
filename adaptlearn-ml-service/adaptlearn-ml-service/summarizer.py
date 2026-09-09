"""
summarizer.py
-------------
Part B of the AdaptLearn ML microservice: content difficulty/length
classification via extractive condensation.

Design notes
------------
- The prototype deliberately uses a TF-IDF-based *extractive* summarizer
  (scikit-learn only, CPU-friendly, no model download / network access
  required) rather than an abstractive transformer pipeline. This keeps the
  service runnable out-of-the-box on any machine with `pip install -r
  requirements.txt`, which matters for a hackathon/prototype context.
- A hook (`abstractive_condense`) is provided for swapping in a HuggingFace
  summarization pipeline (e.g. `sshleifer/distilbart-cnn-12-6`) later,
  behind the same function signature -- see requirements.txt for the
  optional extra.
- Sentence scoring combines three signals so the condensed output
  preserves *definitions* and *must-ask* content, per the product spec:
    1. TF-IDF salience (how much unique/important vocabulary the sentence
       carries relative to the rest of the note)
    2. A "definition bonus" for sentences that read like definitions
       (pattern-matched: "is defined as", "refers to", "means", etc.) --
       these are exactly what a student needs first under time pressure.
    3. A "boost term" bonus for sentences mentioning caller-supplied
       high-priority terms (e.g. the topic's own name, or must-ask
       keywords surfaced by ranking.py), so condensation stays aligned
       with what Part A flagged as important.
"""

from __future__ import annotations

import re
from typing import List, Optional, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_DEFINITION_PATTERN_RE = re.compile(
    r"\b(is defined as|are defined as|refers to|is a\b|is defined|means that|"
    r"is known as|is called)\b",
    re.IGNORECASE,
)

DEFINITION_BONUS = 0.35
BOOST_TERM_BONUS = 0.15
MIN_BULLETS = 2


def _split_sentences(text: str) -> List[str]:
    text = text.strip()
    if not text:
        return []
    sentences = _SENTENCE_SPLIT_RE.split(text)
    return [s.strip() for s in sentences if s.strip()]


def _tfidf_salience(sentences: Sequence[str]) -> np.ndarray:
    if len(sentences) < 2:
        return np.array([1.0] * len(sentences))
    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(sentences)
    # Salience = sum of TF-IDF weights in the sentence, normalized to 0-1.
    raw_scores = np.asarray(matrix.sum(axis=1)).flatten()
    lo, hi = raw_scores.min(), raw_scores.max()
    if hi - lo < 1e-9:
        return np.full_like(raw_scores, 0.5)
    return (raw_scores - lo) / (hi - lo)


def condense(
    text: str,
    target_ratio: float = 0.25,
    boost_terms: Optional[Sequence[str]] = None,
) -> List[str]:
    """Condense `text` into a bullet-point list at roughly `target_ratio` of
    the original sentence count, biased to keep definitions and any
    caller-supplied `boost_terms` (e.g. must-ask keywords from ranking.py).

    Args:
        text: raw notes text for a topic.
        target_ratio: fraction of original sentences to keep (0 < r <= 1).
        boost_terms: optional list of terms to up-weight when scoring
            sentences (e.g. the topic name, or must-ask flagged keywords).

    Returns:
        Ordered list of bullet strings (original sentence order preserved),
        length >= MIN_BULLETS whenever the source has enough sentences.
    """
    sentences = _split_sentences(text)
    if not sentences:
        return []

    salience = _tfidf_salience(sentences)

    definition_bonus = np.array(
        [DEFINITION_BONUS if _DEFINITION_PATTERN_RE.search(s) else 0.0 for s in sentences]
    )

    boost_bonus = np.zeros(len(sentences))
    if boost_terms:
        lowered_terms = [t.lower() for t in boost_terms if t.strip()]
        for i, s in enumerate(sentences):
            s_lower = s.lower()
            hits = sum(1 for term in lowered_terms if term in s_lower)
            boost_bonus[i] = min(hits * BOOST_TERM_BONUS, BOOST_TERM_BONUS * 2)

    combined_score = salience + definition_bonus + boost_bonus

    target_count = max(MIN_BULLETS, round(len(sentences) * target_ratio))
    target_count = min(target_count, len(sentences))

    top_indices = np.argsort(combined_score)[::-1][:target_count]
    ordered_indices = sorted(top_indices.tolist())  # preserve original order

    return [sentences[i] for i in ordered_indices]


def abstractive_condense(text: str, target_ratio: float = 0.25) -> List[str]:
    """Optional upgrade path: abstractive summarization via a HuggingFace
    pipeline. Lazily imported so `transformers`/`torch` are not required
    for the prototype to run. Falls back to the extractive `condense()`
    if the dependency isn't installed.

    Not wired into main.py by default -- kept available for when the
    service is promoted beyond prototype scope.
    """
    try:
        from transformers import pipeline  # type: ignore
    except ImportError:
        return condense(text, target_ratio=target_ratio)

    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    approx_word_count = len(text.split())
    target_words = max(20, int(approx_word_count * target_ratio))
    result = summarizer(
        text, max_length=target_words + 20, min_length=max(10, target_words - 20), do_sample=False
    )
    summary_text = result[0]["summary_text"]
    return _split_sentences(summary_text)


# ---------------------------------------------------------------------------
# Standalone smoke test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    from pathlib import Path

    fixtures_path = Path(__file__).parent / "fixtures" / "os_topics.json"
    data = json.loads(fixtures_path.read_text())
    topic = next(t for t in data["topics"] if t["topic_id"] == "os-t06")

    print(f"=== condense: {topic['topic_name']} ===")
    bullets = condense(
        topic["raw_notes_text"], target_ratio=0.25, boost_terms=["Banker's Algorithm", "deadlock"]
    )
    for b in bullets:
        print(f"- {b}")

    original_len = len(_split_sentences(topic["raw_notes_text"]))
    print(f"\n{original_len} sentences -> {len(bullets)} bullets")
