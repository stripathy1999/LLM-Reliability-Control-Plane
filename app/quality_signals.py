from __future__ import annotations

from typing import Dict


def response_length(text: str) -> int:
    return len(text.split())


def simple_semantic_similarity(a: str, b: str) -> float:
    """
    Extremely lightweight heuristic similarity metric.

    Uses token overlap (Jaccard) to approximate semantic similarity.
    This is enough to power a "quality degradation" monitor in Datadog.
    """
    if not a or not b:
        return 0.0

    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    intersection = len(tokens_a & tokens_b)
    union = len(tokens_a | tokens_b)
    if union == 0:
        return 0.0
    return intersection / union


def ungrounded_answer_flag(response: str, reference: str | None = None) -> bool:
    """
    Heuristic "ungrounded" detector.

    You can later replace this with embedding similarity or citation checks.
    For now, mark ungrounded if the model confidently asserts facts without
    uncertainty language AND similarity is low.
    """
    lower = response.lower()
    looks_confident = "definitely" in lower or "certainly" in lower or "guarantee" in lower
    if reference is None:
        # Without a reference, just flag very short, overconfident answers
        return looks_confident and response_length(response) < 10

    sim = simple_semantic_similarity(response, reference)
    return looks_confident and sim < 0.3


def compute_quality_signals(response: str, reference: str | None = None) -> Dict[str, float | bool | int]:
    length = response_length(response)
    sim = simple_semantic_similarity(response, reference or "")
    ungrounded = ungrounded_answer_flag(response, reference)
    return {
        "llm.response.length": length,
        "llm.semantic_similarity_score": sim,
        "llm.ungrounded_answer_flag": ungrounded,
    }


