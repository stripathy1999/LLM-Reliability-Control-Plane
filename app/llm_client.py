import asyncio
import time
from typing import Any, Dict

from .config import settings


class LLMClient:
    """
    Thin wrapper around an LLM provider (Gemini via Vertex AI in the real system).

    For hackathon/demo purposes, this implementation is intentionally simple and
    returns synthetic responses so you can focus on observability and control-plane
    behavior. You can later swap this out for a real Vertex AI client.

    To integrate with real Vertex AI:
    1. Install: pip install google-cloud-aiplatform
    2. Set GCP credentials: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
    3. Replace synthetic logic with:
       from vertexai.generative_models import GenerativeModel
       model = GenerativeModel(settings.gemini_model)
       response = await model.generate_content_async(prompt)
       # Extract tokens, cost, etc. from response
    """

    async def generate(
        self,
        prompt: str,
        request_type: str,
        *,
        simulate_latency: bool = False,
        simulate_retry: bool = False,
        simulate_bad_prompt: bool = False,
        simulate_long_context: bool = False,
    ) -> Dict[str, Any]:
        start = time.monotonic()
        latency_ms: float
        retry_count = 0
        safety_block = False
        error: str | None = None

        try:
            # Simulated behaviors for demo / observability
            if simulate_long_context:
                # Pretend context explosion by sleeping and inflating tokens
                await asyncio.sleep(0.5)

            if simulate_latency:
                await asyncio.sleep(1.0)

            if simulate_retry:
                # First attempt "fails", second succeeds
                retry_count = 1
                await asyncio.sleep(0.2)

            if simulate_bad_prompt:
                safety_block = True
                text = "Response blocked due to safety policy."
            else:
                text = f"[{request_type.upper()}] Synthetic response for: {prompt[:120]}..."

            latency_ms = (time.monotonic() - start) * 1000.0

            # Very rough token estimates
            input_tokens = max(1, len(prompt.split()))
            output_tokens = max(5, len(text.split()))

            # Fake cost model: $0.000002 per token
            cost_usd = (input_tokens + output_tokens) * 0.000002

            return {
                "text": text,
                "latency_ms": latency_ms,
                "retry_count": retry_count,
                "safety_block": safety_block,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd,
                "model": settings.gemini_model,
                "model_version": "synthetic-0.1",
            }
        except Exception as exc:  # noqa: BLE001
            latency_ms = (time.monotonic() - start) * 1000.0
            error = str(exc)
            return {
                "text": "",
                "latency_ms": latency_ms,
                "retry_count": retry_count,
                "safety_block": safety_block,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
                "model": settings.gemini_model,
                "model_version": "synthetic-0.1",
                "error": error,
            }


llm_client = LLMClient()


