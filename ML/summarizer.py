from collections import Counter
import math
import re
from typing import Any, Dict, List, Optional
from ranking import TOPIC_INDEX


class PurePythonTFIDFSummarizer:
    """
    Zero-external-dependency TF-IDF Sentence Scoring Engine.
    Works 100% on CPU without installing heavy weights,
    while producing high-quality extractive condensations.
    """

    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
        "by", "can", "cannot", "could", "did", "do", "does", "doing", "down", "during", "each",
        "few", "for", "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers",
        "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "me",
        "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
        "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
        "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
        "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
        "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why",
        "with", "would", "you", "your", "yours", "yourself", "yourselves"
    }

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        cleaned = re.sub(r'\s+', ' ', text).strip()
        raw = re.split(r'(?<=[.!?])\s+', cleaned)
        return [s.strip() for s in raw if len(s.strip()) > 15]

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        words = re.findall(r'[a-zA-Z0-9_\-]+', text.lower())
        return [w for w in words if w not in cls.STOPWORDS and len(w) > 2]

    @classmethod
    def summarize(cls, text: str, target_ratio: float = 0.3) -> List[str]:
        sentences = cls.split_sentences(text)
        if len(sentences) <= 2:
            return sentences

        num_to_keep = max(1, round(len(sentences) * target_ratio))
        num_to_keep = min(num_to_keep, len(sentences))

        sentence_tokens = [cls.tokenize(s) for s in sentences]
        total_sentences = len(sentences)

        df: Counter = Counter()
        for tokens in sentence_tokens:
            for word in set(tokens):
                df[word] += 1

        sentence_scores = []
        for idx, tokens in enumerate(sentence_tokens):
            if not tokens:
                sentence_scores.append((0.0, idx))
                continue
            tf = Counter(tokens)
            score = 0.0
            for w, count in tf.items():
                idf = math.log((total_sentences + 1) / (df[w] + 1)) + 1.0
                score += count * idf
            normalized_score = score / (len(tokens) ** 0.6)
            if idx == 0:
                normalized_score *= 1.25
            sentence_scores.append((normalized_score, idx))

        sentence_scores.sort(key=lambda x: x[0], reverse=True)
        top_indices = sorted([idx for _, idx in sentence_scores[:num_to_keep]])

        return [sentences[i] for i in top_indices]


def condense_topic(
    topic_id_or_text: str,
    target_ratio: float = 0.25,
) -> Dict[str, Any]:
    """
    Part B summarization function:
    Condenses text or topic into punchy bullet points and concise study notes.
    """
    topic_info = TOPIC_INDEX.get(topic_id_or_text)
    if topic_info:
        raw_text = topic_info["raw_notes"]
        title = topic_info["title"]
    else:
        raw_text = topic_id_or_text
        title = "Custom Topic"

    bullets = PurePythonTFIDFSummarizer.summarize(raw_text, target_ratio=target_ratio)
    char_count_original = len(raw_text)
    char_count_condensed = sum(len(b) for b in bullets)
    actual_compression = round(char_count_condensed / max(1, char_count_original), 3)

    return {
        "title": title,
        "target_ratio": target_ratio,
        "actual_ratio": actual_compression,
        "bullet_count": len(bullets),
        "bullets": bullets,
        "condensed_text": " ".join(bullets),
    }


def abstractive_condense(raw_text: str) -> Optional[str]:
    """
    Drop-in seam for HuggingFace Transformers abstractive condensation.
    Returns None if library or weights are not installed.
    """
    try:
        from transformers import pipeline  # type: ignore
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
        res = summarizer(raw_text[:1024], max_length=120, min_length=30, do_sample=False)
        return res[0]["summary_text"]
    except Exception:
        return None


if __name__ == "__main__":
    print("=== SMOKE TEST: TF-IDF Content Condensation ===")
    res = condense_topic("os-t06", target_ratio=0.25)
    print(f"Topic: {res['title']}")
    print(f"Target ratio: {res['target_ratio']} -> Actual compression: {res['actual_ratio']}")
    print(f"Bullet count: {res['bullet_count']}")
    for i, b in enumerate(res["bullets"], 1):
        print(f" {i}. {b}")
