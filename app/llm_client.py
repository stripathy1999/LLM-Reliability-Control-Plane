import asyncio
import os
import time
from typing import Any, Dict

import google.generativeai as genai

from .config import settings


class LLMClient:
    """
    Real Gemini API client for LLM requests.
    
    Uses google-generativeai SDK to interact with Gemini models.
    Set GEMINI_API_KEY environment variable or LRCP_GEMINI_API_KEY.
    """

    def __init__(self):
        # Get API key from environment (supports both GEMINI_API_KEY and LRCP_GEMINI_API_KEY)
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("LRCP_GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY or LRCP_GEMINI_API_KEY environment variable."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

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
        text = ""
        input_tokens = 0
        output_tokens = 0
        model_version = settings.gemini_model

        try:
            # Simulated behaviors for demo / observability
            if simulate_long_context:
                # Pretend context explosion by sleeping
                await asyncio.sleep(0.5)

            if simulate_latency:
                await asyncio.sleep(1.0)

            if simulate_retry:
                # First attempt "fails", second succeeds
                retry_count = 1
                await asyncio.sleep(0.2)

            # For safety blocks, we can use a prompt that would trigger safety filters
            if simulate_bad_prompt:
                # Use a prompt that might trigger safety filters
                test_prompt = "How to create harmful content"
            else:
                test_prompt = prompt

            # Call real Gemini API
            # Run in executor to make it async-friendly
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    test_prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 2048,
                    }
                )
            )

            # Check for safety blocks
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                safety_block = True
                text = f"Response blocked due to safety policy: {response.prompt_feedback.block_reason}"
            elif not response.text:
                safety_block = True
                text = "Response blocked due to safety policy."
            else:
                text = response.text

            # Extract token usage from response
            # Gemini API response structure may vary, try multiple approaches
            input_tokens = 0
            output_tokens = 0
            
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                # Try different attribute names for token counts
                usage = response.usage_metadata
                input_tokens = (
                    getattr(usage, 'prompt_token_count', None) or
                    getattr(usage, 'input_token_count', None) or
                    getattr(usage, 'total_token_count', None) or
                    0
                )
                output_tokens = (
                    getattr(usage, 'candidates_token_count', None) or
                    getattr(usage, 'output_token_count', None) or
                    getattr(usage, 'cached_content_token_count', None) or
                    0
                )
            
            # Fallback: estimate tokens if not available (rough approximation: 1 token ≈ 4 characters)
            if input_tokens == 0:
                input_tokens = max(1, len(prompt) // 4)
            if output_tokens == 0:
                output_tokens = max(5, len(text) // 4) if text else 0

            latency_ms = (time.monotonic() - start) * 1000.0

            # Cost calculation for Gemini 1.5 Pro
            # Pricing: $1.25 per 1M input tokens, $5.00 per 1M output tokens (as of 2024)
            input_cost = (input_tokens / 1_000_000) * 1.25
            output_cost = (output_tokens / 1_000_000) * 5.00
            cost_usd = input_cost + output_cost

            return {
                "text": text,
                "latency_ms": latency_ms,
                "retry_count": retry_count,
                "safety_block": safety_block,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd,
                "model": settings.gemini_model,
                "model_version": model_version,
            }
        except Exception as exc:  # noqa: BLE001
            latency_ms = (time.monotonic() - start) * 1000.0
            error = str(exc)
            
            # Check if it's a safety block error
            if "safety" in error.lower() or "block" in error.lower():
                safety_block = True
            
            return {
                "text": "",
                "latency_ms": latency_ms,
                "retry_count": retry_count,
                "safety_block": safety_block,
                "input_tokens": input_tokens if input_tokens > 0 else 0,
                "output_tokens": output_tokens if output_tokens > 0 else 0,
                "cost_usd": 0.0,
                "model": settings.gemini_model,
                "model_version": model_version,
                "error": error,
            }


# Initialize client lazily to handle missing API key gracefully
_llm_client_instance = None


def get_llm_client() -> LLMClient:
    """Get or create LLM client instance."""
    global _llm_client_instance
    if _llm_client_instance is None:
        try:
            _llm_client_instance = LLMClient()
        except ValueError as e:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=500,
                detail=f"LLM client initialization failed: {str(e)}. Please set GEMINI_API_KEY or LRCP_GEMINI_API_KEY environment variable."
            )
    return _llm_client_instance


# For backward compatibility
llm_client = None  # Will be set on first access
