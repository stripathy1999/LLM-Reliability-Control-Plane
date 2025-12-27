from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..llm_client import get_llm_client
from ..quality_signals import compute_quality_signals
from ..telemetry import emit_llm_metrics, log_request
from ..telemetry_unified import get_unified_telemetry

router = APIRouter(prefix="/reason", tags=["reason"])


class ReasonRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="The reasoning prompt or question that requires complex thinking or multi-step reasoning",
        example="Explain the golden signals of SRE (Site Reliability Engineering) and why they matter for LLM applications. Include examples of how to measure each signal.",
        min_length=1,
        max_length=5000,
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Explain the golden signals of SRE (Site Reliability Engineering) and why they matter for LLM applications. Include examples of how to measure each signal."
            }
        }


class ReasonResponse(BaseModel):
    answer: str = Field(
        ...,
        description="The LLM-generated reasoning response",
        example="The four golden signals of SRE are latency, traffic, errors, and saturation..."
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="""
        Comprehensive metadata about the request including:
        - **prompt_id**: Unique identifier for this request
        - **latency_ms**: Request latency in milliseconds (key metric for this endpoint)
        - **retry_count**: Number of retries attempted (important for reliability monitoring)
        - **input_tokens**: Number of input tokens used
        - **output_tokens**: Number of output tokens generated
        - **cost_usd**: Estimated cost in USD
        - **model**: Model name used
        """,
        example={
            "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
            "latency_ms": 2345.67,
            "retry_count": 1,
            "input_tokens": 78,
            "output_tokens": 456,
            "cost_usd": 0.001234,
            "model": "gemini-2.5-flash"
        }
    )


@router.post(
    "",
    response_model=ReasonResponse,
    summary="Reasoning Endpoint",
    description="""
    Handles reasoning-style prompts that require complex thinking, multi-step problem solving, 
    or detailed explanations.
    
    ## Purpose
    This endpoint is designed to observe **latency** and **retry** behavior patterns, 
    making it ideal for performance monitoring and reliability testing.
    
    ## How It Works
    1. Takes a reasoning prompt
    2. Sends to Gemini LLM for processing
    3. Tracks latency and retry behavior
    4. Emits performance metrics to Datadog
    5. Returns detailed response with timing information
    
    ## Key Metrics
    - **Latency (p50, p95, p99)**: Critical for SLO monitoring
    - **Retry Count**: Indicates reliability issues
    - **Timeout Rate**: Shows when requests exceed time limits
    
    ## Failure Simulation
    Use query parameters to simulate production failures:
    - `simulate_latency=true` - Adds artificial delay (triggers latency SLO monitor)
    - `simulate_retry=true` - Simulates retry behavior (triggers error burst monitor)
    
    ## Example Use Cases
    - Complex reasoning tasks
    - Multi-step problem solving
    - Educational explanations
    - Latency monitoring and SLO testing
    - Retry behavior analysis
    """,
    response_description="Reasoning response with detailed performance metadata",
    responses={
        200: {
            "description": "Successful response with reasoning answer and performance metrics",
        },
        422: {
            "description": "Validation error - check request body format",
        },
        500: {
            "description": "Internal server error - check API key configuration",
        },
    },
)
async def reason_endpoint(
    body: ReasonRequest,
    simulate_latency: bool = Query(
        default=False,
        description="Simulate high latency (adds ~1 second delay). Triggers latency SLO monitor when p95 > 1500ms.",
        example=False,
    ),
    simulate_retry: bool = Query(
        default=False,
        description="Simulate retry behavior (first attempt fails, second succeeds). Triggers error burst monitor.",
        example=False,
    ),
    simulate_bad_prompt: bool = Query(
        default=False,
        description="Simulate safety block. Triggers security monitor.",
        example=False,
    ),
    simulate_long_context: bool = Query(
        default=False,
        description="Simulate long context window. Triggers cost anomaly detection.",
        example=False,
    ),
) -> ReasonResponse:
    """
    Reasoning-style prompts.
    Used to observe **latency** and **retry** behavior.
    """
    prompt_id = str(uuid.uuid4())
    prompt = body.prompt

    llm_client = get_llm_client()
    llm_result = await llm_client.generate(
        prompt,
        request_type="reason",
        simulate_latency=simulate_latency,
        simulate_retry=simulate_retry,
        simulate_bad_prompt=simulate_bad_prompt,
        simulate_long_context=simulate_long_context,
        auto_route=True,  # Enable ML-based model routing
    )

    text = llm_result["text"]
    quality = compute_quality_signals(text)

    # Use unified telemetry (feeds BOTH Datadog + Confluent)
    unified = get_unified_telemetry()
    unified.emit_llm_metrics_unified(
        endpoint="/reason",
        model=llm_result["model"],
        model_version=llm_result["model_version"],
        request_type="reason",
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
    
    unified.emit_llm_request_unified(
        request_id=prompt_id,
        endpoint="/reason",
        request_type="reason",
        prompt=prompt,
        model=llm_result["model"],
    )
    
    unified.emit_llm_response_unified(
        request_id=prompt_id,
        endpoint="/reason",
        response_text=text,
        metadata=llm_result | quality,
    )
    
    # Keep legacy Datadog-only for backward compatibility
    emit_llm_metrics(
        endpoint="/reason",
        model=llm_result["model"],
        model_version=llm_result["model_version"],
        request_type="reason",
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
        endpoint="/reason",
        request_type="reason",
        prompt=prompt,
        response_text=text,
        metadata=llm_result | quality,
    )

    return ReasonResponse(
        answer=text,
        metadata=llm_result | quality | {"prompt_id": prompt_id},
    )


