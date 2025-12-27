from __future__ import annotations

from typing import Dict

# Datadog tracing for custom spans
try:
    from ddtrace import tracer
    DD_TRACING_ENABLED = True
except ImportError:
    DD_TRACING_ENABLED = False
    tracer = None


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
    # Custom span for quality scoring
    if DD_TRACING_ENABLED and tracer:
        with tracer.trace("llm.quality_scoring", service="llm-reliability-control-plane") as quality_span:
            quality_span.set_tag("llm.response_length", len(response))
            quality_span.set_tag("llm.has_reference", reference is not None)
            
            length = response_length(response)
            quality_span.set_tag("llm.response.word_count", length)
            
            sim = simple_semantic_similarity(response, reference or "")
            quality_span.set_tag("llm.semantic_similarity_score", sim)
            
            ungrounded = ungrounded_answer_flag(response, reference)
            quality_span.set_tag("llm.ungrounded_answer_flag", ungrounded)
            
            # Set quality thresholds for monitoring
            quality_span.set_tag("llm.quality.good", sim > 0.7)
            quality_span.set_tag("llm.quality.degraded", sim < 0.4)
            
            return {
                "llm.response.length": length,
                "llm.semantic_similarity_score": sim,
                "llm.ungrounded_answer_flag": ungrounded,
            }
    else:
        length = response_length(response)
        sim = simple_semantic_similarity(response, reference or "")
        ungrounded = ungrounded_answer_flag(response, reference)
        return {
            "llm.response.length": length,
            "llm.semantic_similarity_score": sim,
            "llm.ungrounded_answer_flag": ungrounded,
        }


