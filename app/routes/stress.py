from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..llm_client import get_llm_client
from ..quality_signals import compute_quality_signals
from ..telemetry import emit_llm_metrics, log_request
from ..telemetry_unified import get_unified_telemetry

router = APIRouter(prefix="/stress", tags=["stress"])


class StressRequest(BaseModel):
    prompt: str = Field(
        ...,
        description="Base prompt that will be repeated to create a long context",
        example="Summarize production incidents",
        min_length=1,
        max_length=1000,
    )
    repetitions: int = Field(
        default=10,
        description="Number of times to repeat the prompt. Higher values create longer contexts and higher costs.",
        example=50,
        ge=1,
        le=100,
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Summarize production incidents",
                "repetitions": 50
            }
        }


class StressResponse(BaseModel):
    answer: str = Field(
        ...,
        description="The LLM-generated response",
        example="Production incidents are critical events that impact system availability..."
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="""
        Comprehensive metadata about the request including:
        - **prompt_id**: Unique identifier for this request
        - **input_tokens**: Number of input tokens (will be high due to repetitions)
        - **output_tokens**: Number of output tokens generated
        - **cost_usd**: Estimated cost in USD (key metric - watch for anomalies!)
        - **latency_ms**: Request latency in milliseconds
        - **model**: Model name used
        
        **Note**: This endpoint always simulates long context, so input_tokens and cost_usd 
        will be elevated compared to other endpoints.
        """,
        example={
            "prompt_id": "550e8400-e29b-41d4-a716-446655440000",
            "input_tokens": 1250,
            "output_tokens": 234,
            "cost_usd": 0.008765,
            "latency_ms": 3456.78,
            "model": "gemini-2.5-flash"
        }
    )


@router.post(
    "",
    response_model=StressResponse,
    summary="Stress Testing Endpoint",
    description="""
    Generates long-context, high-token requests to trigger **token & cost explosions**.
    
    ## Purpose
    This endpoint is designed to test cost anomaly detection and token abuse monitoring 
    by creating requests with artificially inflated context lengths.
    
    ## How It Works
    1. Takes a base prompt and repetition count
    2. Repeats the prompt multiple times to create a long context
    3. Sends to Gemini LLM (always simulates long context)
    4. Tracks token usage and cost
    5. Emits cost metrics to Datadog for anomaly detection
    
    ## Key Metrics
    - **Input Tokens**: Will be high due to repetitions (triggers token abuse detection)
    - **Cost per Request**: Elevated costs trigger cost anomaly monitor
    - **Token Ratio**: Input/output token ratio indicates efficiency
    
    ## Failure Simulation
    Use query parameters to simulate additional failure scenarios:
    - `simulate_latency=true` - Adds artificial delay
    - `simulate_retry=true` - Simulates retry behavior
    
    **Note**: This endpoint always simulates long context regardless of the `simulate_long_context` parameter.
    
    ## Example Use Cases
    - Cost anomaly testing
    - Token usage monitoring
    - Context window stress testing
    - Cost optimization validation
    
    ## Cost Anomaly Detection
    When cost exceeds 2x baseline, the Datadog monitor will trigger and create an incident 
    with cost breakdown and optimization recommendations.
    """,
    response_description="Response with detailed cost and token metadata",
    responses={
        200: {
            "description": "Successful response with cost and token metrics",
        },
        422: {
            "description": "Validation error - check request body format (repetitions must be 1-100)",
        },
        500: {
            "description": "Internal server error - check API key configuration",
        },
    },
)
async def stress_endpoint(
    body: StressRequest,
    simulate_latency: bool = Query(
        default=False,
        description="Simulate high latency in addition to long context",
        example=False,
    ),
    simulate_retry: bool = Query(
        default=False,
        description="Simulate retry behavior in addition to long context",
        example=False,
    ),
    simulate_bad_prompt: bool = Query(
        default=False,
        description="Simulate safety block",
        example=False,
    ),
    simulate_long_context: bool = Query(
        default=False,
        description="Note: This endpoint always simulates long context regardless of this parameter",
        example=False,
    ),
) -> StressResponse:
    """
    Long-context, high-token requests to trigger **token & cost explosions**.
    """
    prompt_id = str(uuid.uuid4())
    long_prompt = (" " + body.prompt) * max(1, body.repetitions)

    llm_client = get_llm_client()
    llm_result = await llm_client.generate(
        long_prompt,
        request_type="stress",
        simulate_latency=simulate_latency,
        simulate_retry=simulate_retry,
        simulate_bad_prompt=simulate_bad_prompt,
        simulate_long_context=True,  # Always simulate long context for stress endpoint
        auto_route=True,  # Enable ML-based model routing
    )

    text = llm_result["text"]
    quality = compute_quality_signals(text)

    emit_llm_metrics(
        endpoint="/stress",
        model=llm_result["model"],
        model_version=llm_result["model_version"],
        request_type="stress",
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
        endpoint="/stress",
        request_type="stress",
        prompt=long_prompt[:500],
        response_text=text,
        metadata=llm_result | quality,
    )

    return StressResponse(
        answer=text,
        metadata=llm_result | quality | {"prompt_id": prompt_id},
    )


