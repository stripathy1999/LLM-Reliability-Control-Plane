from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..llm_client import get_llm_client
from ..quality_signals import compute_quality_signals
from ..telemetry import emit_llm_metrics, log_request
from ..telemetry_unified import get_unified_telemetry
from ..product_analytics import get_product_analytics
from ..datadog_llm_observability import get_llm_observability

router = APIRouter(prefix="/qa", tags=["qa"])


class QARequest(BaseModel):
    question: str = Field(
        ...,
        description="The question to ask about the document",
        example="What is Datadog?",
        min_length=1,
        max_length=1000,
    )
    document: str | None = Field(
        None,
        description="Optional context document to answer the question from. If not provided, the LLM will answer from general knowledge.",
        example="Datadog is a monitoring and observability platform for cloud applications. It provides infrastructure monitoring, application performance monitoring, log management, and security monitoring.",
        max_length=10000,
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Datadog?",
                "document": "Datadog is a monitoring and observability platform for cloud applications. It provides infrastructure monitoring, application performance monitoring, log management, and security monitoring."
            }
        }


class QAResponse(BaseModel):
    answer: str = Field(
        ...,
        description="The LLM-generated answer to the question",
        example="Datadog is a comprehensive monitoring and observability platform designed for cloud applications..."
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="""
        Comprehensive metadata about the request including:
        - **prompt_id**: Unique identifier for this request
        - **latency_ms**: Request latency in milliseconds
        - **input_tokens**: Number of input tokens used
        - **output_tokens**: Number of output tokens generated
        - **cost_usd**: Estimated cost in USD
        - **retry_count**: Number of retries (if any)
        - **safety_block**: Whether the response was blocked by safety filters
        - **llm.semantic_similarity_score**: Quality score (0-1) indicating answer relevance
        - **llm.ungrounded_answer_flag**: Whether the answer may be ungrounded/hallucinated
        - **model**: Model name used (e.g., gemini-2.5-flash)
        """,
        example={
            "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
            "latency_ms": 1234.56,
            "input_tokens": 45,
            "output_tokens": 128,
            "cost_usd": 0.000276,
            "retry_count": 0,
            "safety_block": False,
            "llm.semantic_similarity_score": 0.85,
            "llm.ungrounded_answer_flag": False,
            "model": "gemini-2.5-flash"
        }
    )


@router.post(
    "",
    response_model=QAResponse,
    summary="Question & Answer Endpoint",
    description="""
    Performs question-answering over provided documents using Google's Gemini model.
    
    ## Purpose
    This endpoint is primarily designed for **quality degradation detection** through 
    semantic similarity scoring between the answer and the source document.
    
    ## How It Works
    1. Takes a question and optional document context
2. Sends the prompt to Gemini LLM
3. Computes quality signals (semantic similarity, grounding)
4. Emits metrics to Datadog
5. Returns the answer with comprehensive metadata
    
    ## Quality Metrics
    - **Semantic Similarity Score**: Measures how relevant the answer is to the document (0-1)
    - **Ungrounded Answer Flag**: Detects potential hallucinations or ungrounded responses
    
    ## Failure Simulation
    Use query parameters to simulate production failures:
    - `simulate_latency=true` - Adds artificial delay (triggers latency SLO monitor)
    - `simulate_bad_prompt=true` - Triggers safety filters (triggers security monitor)
    
    ## Example Use Cases
    - Document-based Q&A systems
    - Quality assurance testing
    - Semantic similarity validation
    - Hallucination detection
    """,
    response_description="Answer with comprehensive metadata including quality scores, tokens, cost, and latency",
    responses={
        200: {
            "description": "Successful response with answer and metadata",
        },
        422: {
            "description": "Validation error - check request body format",
        },
        500: {
            "description": "Internal server error - check API key configuration",
        },
    },
)
async def qa_endpoint(
    body: QARequest,
    simulate_latency: bool = Query(
        default=False,
        description="Simulate high latency (adds ~1 second delay). Useful for testing latency SLO monitors.",
        example=False,
    ),
    simulate_retry: bool = Query(
        default=False,
        description="Simulate retry behavior. Useful for testing error burst monitors.",
        example=False,
    ),
    simulate_bad_prompt: bool = Query(
        default=False,
        description="Simulate safety block by using a prompt that triggers safety filters. Useful for testing security monitors.",
        example=False,
    ),
    simulate_long_context: bool = Query(
        default=False,
        description="Simulate long context window. Useful for testing cost anomaly detection.",
        example=False,
    ),
) -> QAResponse:
    """
    Q&A endpoint over small static documents.
    Used primarily for **quality degradation** detection.
    """
    prompt_id = str(uuid.uuid4())
    prompt = f"Q: {body.question}\nContext: {body.document or 'N/A'}"

    llm_client = get_llm_client()
    llm_result = await llm_client.generate(
        prompt,
        request_type="qa",
        simulate_latency=simulate_latency,
        simulate_retry=simulate_retry,
        simulate_bad_prompt=simulate_bad_prompt,
        simulate_long_context=simulate_long_context,
        auto_route=True,  # Enable ML-based model routing
    )

    text = llm_result["text"]
    quality = compute_quality_signals(text, body.document or "")
    
    # EXTENSION: Add quality metrics to LLM Observability (extends native Datadog LLM Observability)
    llm_obs = get_llm_observability()
    semantic_similarity = quality.get("llm.semantic_similarity_score", 0.0)
    ungrounded = quality.get("llm.ungrounded_answer_flag", False)
    response_length = quality.get("llm.response.length", 0)
    
    # Track quality metrics as extension to native LLM Observability
    llm_obs.track_quality_metrics(
        semantic_similarity_score=semantic_similarity,
        ungrounded_flag=ungrounded,
        provider="google",
        model=llm_result["model"],
        tags={
            "request_type": "qa",
            "endpoint": "/qa",
        }
    )

    # Use unified telemetry (feeds Datadog)
    unified = get_unified_telemetry()
    unified.emit_llm_metrics_unified(
        endpoint="/qa",
        model=llm_result["model"],
        model_version=llm_result["model_version"],
        request_type="qa",
        latency_ms=llm_result["latency_ms"],
        retry_count=llm_result["retry_count"],
        error=llm_result.get("error"),
        safety_block=llm_result["safety_block"],
        input_tokens=llm_result["input_tokens"],
        output_tokens=llm_result["output_tokens"],
        cost_usd=llm_result["cost_usd"],
        quality=quality,
        request_id=prompt_id,
    )
    
    # Emit request and response events to Datadog
    unified.emit_llm_request_unified(
        request_id=prompt_id,
        endpoint="/qa",
        request_type="qa",
        prompt=prompt,
        model=llm_result["model"],
    )
    
    unified.emit_llm_response_unified(
        request_id=prompt_id,
        endpoint="/qa",
        response_text=text,
        metadata=llm_result | quality,
    )
    
    # Keep legacy Datadog-only for backward compatibility
    emit_llm_metrics(
        endpoint="/qa",
        model=llm_result["model"],
        model_version=llm_result["model_version"],
        request_type="qa",
        latency_ms=llm_result["latency_ms"],
        retry_count=llm_result["retry_count"],
        error=llm_result.get("error"),
        safety_block=llm_result["safety_block"],
        input_tokens=llm_result["input_tokens"],
        output_tokens=llm_result["output_tokens"],
        cost_usd=llm_result["cost_usd"],
        quality=quality,
    )

    log_request(
        prompt_id=prompt_id,
        endpoint="/qa",
        request_type="qa",
        prompt=prompt,
        response_text=text,
        metadata=llm_result | quality,
    )
    
    # Track product analytics
    analytics = get_product_analytics()
    analytics.track_endpoint_usage(
        endpoint="/qa",
        request_type="qa",
        success=not llm_result.get("error"),
        latency_ms=llm_result.get("latency_ms", 0.0),
        cost_usd=llm_result.get("cost_usd", 0.0),
    )

    return QAResponse(
        answer=text,
        metadata=llm_result | quality | {"prompt_id": prompt_id},
    )


