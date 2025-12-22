from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..llm_client import llm_client
from ..quality_signals import compute_quality_signals
from ..telemetry import emit_llm_metrics, log_request

router = APIRouter(prefix="/stress", tags=["stress"])


class StressRequest(BaseModel):
    prompt: str
    repetitions: int = 10


class StressResponse(BaseModel):
    answer: str
    metadata: Dict[str, Any]


@router.post("", response_model=StressResponse)
async def stress_endpoint(
    body: StressRequest,
    simulate_latency: bool = Query(default=False),
    simulate_retry: bool = Query(default=False),
    simulate_bad_prompt: bool = Query(default=False),
    simulate_long_context: bool = Query(default=False),
) -> StressResponse:
    """
    Long-context, high-token requests to trigger **token & cost explosions**.
    """
    prompt_id = str(uuid.uuid4())
    long_prompt = (" " + body.prompt) * max(1, body.repetitions)

    llm_result = await llm_client.generate(
        long_prompt,
        request_type="stress",
        simulate_latency=simulate_latency,
        simulate_retry=simulate_retry,
        simulate_bad_prompt=simulate_bad_prompt,
        simulate_long_context=True or simulate_long_context,
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


