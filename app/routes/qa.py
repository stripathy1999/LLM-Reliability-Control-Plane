from __future__ import annotations

import uuid
from typing import Any, Dict

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..llm_client import get_llm_client
from ..quality_signals import compute_quality_signals
from ..telemetry import emit_llm_metrics, log_request

router = APIRouter(prefix="/qa", tags=["qa"])


class QARequest(BaseModel):
    question: str
    document: str | None = None


class QAResponse(BaseModel):
    answer: str
    metadata: Dict[str, Any]


@router.post("", response_model=QAResponse)
async def qa_endpoint(
    body: QARequest,
    simulate_latency: bool = Query(default=False),
    simulate_retry: bool = Query(default=False),
    simulate_bad_prompt: bool = Query(default=False),
    simulate_long_context: bool = Query(default=False),
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
    )

    text = llm_result["text"]
    quality = compute_quality_signals(text, body.document or "")

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

    return QAResponse(
        answer=text,
        metadata=llm_result | quality | {"prompt_id": prompt_id},
    )


