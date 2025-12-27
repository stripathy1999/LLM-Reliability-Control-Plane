"""
Datadog LLM Observability Integration

This module provides native Datadog LLM Observability instrumentation following
Datadog's standard conventions for LLM traces, metrics, and token/cost tracking.

Reference: https://docs.datadoghq.com/llm_observability/
"""

import os
import logging
from typing import Any, Dict, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

try:
    from ddtrace import tracer
    DD_TRACING_ENABLED = True
except ImportError:
    DD_TRACING_ENABLED = False
    tracer = None


class DatadogLLMObservability:
    """
    Native Datadog LLM Observability instrumentation.
    
    Provides automatic token tracking, cost attribution, and LLM-specific
    trace visualization following Datadog's standard conventions.
    """
    
    def __init__(self):
        self.enabled = DD_TRACING_ENABLED and tracer is not None
        if not self.enabled:
            logger.warning("Datadog LLM Observability disabled: ddtrace not available")
    
    @contextmanager
    def llm_generation_span(
        self,
        provider: str = "google",
        model: str = "gemini-1.5-pro",
        request_type: str = "completion",
        prompt: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Create a Datadog LLM generation span with native LLM Observability tags.
        
        Args:
            provider: LLM provider (e.g., "google", "openai", "anthropic")
            model: Model name (e.g., "gemini-1.5-pro")
            request_type: Type of request (e.g., "completion", "chat", "embedding")
            prompt: The input prompt (will be truncated for tagging)
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Additional metadata to attach
            
        Yields:
            LLMObservabilityContext: Context object for tracking tokens and costs
        """
        if not self.enabled:
            yield LLMObservabilityContext()
            return
        
        # Create LLM generation span using Datadog's standard operation name
        span = tracer.trace(
            "llm.generate",
            service="llm-reliability-control-plane",
            resource=f"{provider}.{model}.{request_type}",
        )
        
        # Standard Datadog LLM Observability tags
        # Reference: https://docs.datadoghq.com/llm_observability/attributes/
        
        # Provider and model tags
        span.set_tag("llm.provider", provider)
        span.set_tag("llm.request.model", model)
        span.set_tag("llm.request.type", request_type)
        
        # Request metadata
        if prompt:
            # Truncate prompt for tagging (keep first 1000 chars)
            truncated_prompt = prompt[:1000] + "..." if len(prompt) > 1000 else prompt
            span.set_tag("llm.request.input", truncated_prompt)
            span.set_tag("llm.request.prompt_length", len(prompt))
        
        if user_id:
            span.set_tag("llm.user.id", user_id)
        if session_id:
            span.set_tag("llm.session.id", session_id)
        
        # Additional metadata
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)):
                    span.set_tag(f"llm.{key}", value)
        
        # Create context for tracking tokens and costs
        context = LLMObservabilityContext(span=span)
        
        try:
            yield context
        finally:
            # Set final tags from context
            if context.input_tokens > 0:
                span.set_tag("llm.request.input_tokens", context.input_tokens)
            if context.output_tokens > 0:
                span.set_tag("llm.response.output_tokens", context.output_tokens)
            if context.total_tokens > 0:
                span.set_tag("llm.request.token_count", context.total_tokens)
            
            if context.cost_usd > 0:
                span.set_tag("llm.request.cost", context.cost_usd)
            
            if context.model:
                span.set_tag("llm.response.model", context.model)
            
            if context.error:
                span.set_tag("error", True)
                span.set_tag("error.type", context.error_type or "LLMError")
                span.set_tag("error.message", str(context.error))
            
            # Set latency (handled by span timing, but we can also set it explicitly)
            if context.latency_ms:
                span.set_tag("llm.request.latency", context.latency_ms)
            
            # EXTENSION: Add semantic similarity and quality metrics (extends native LLM Observability)
            if context.semantic_similarity_score is not None:
                span.set_tag("llm.quality.semantic_similarity", context.semantic_similarity_score)
                span.set_tag("llm.quality.good", context.semantic_similarity_score > 0.7)
                span.set_tag("llm.quality.degraded", context.semantic_similarity_score < 0.4)
            
            if context.ungrounded_flag is not None:
                span.set_tag("llm.quality.ungrounded", context.ungrounded_flag)
            
            if context.response_length:
                span.set_tag("llm.response.length", context.response_length)
            
            span.finish()
    
    def track_llm_metrics(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        latency_ms: float,
        error: bool = False,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Emit native LLM metrics to Datadog.
        
        This emits metrics using Datadog's standard LLM metric conventions.
        """
        if not self.enabled:
            return
        
        try:
            from datadog import statsd
            
            base_tags = [
                f"llm_provider:{provider}",
                f"llm_model:{model}",
            ]
            
            if tags:
                base_tags.extend([f"{k}:{v}" for k, v in tags.items()])
            
            if error:
                base_tags.append("error:true")
            
            # LLM-specific metrics (these will appear in Datadog LLM Observability)
            statsd.histogram("llm.request.duration", latency_ms, tags=base_tags)
            statsd.count("llm.request.tokens.input", input_tokens, tags=base_tags)
            statsd.count("llm.request.tokens.output", output_tokens, tags=base_tags)
            statsd.count("llm.request.tokens.total", input_tokens + output_tokens, tags=base_tags)
            statsd.histogram("llm.request.cost", cost_usd, tags=base_tags)
            
            if error:
                statsd.increment("llm.request.error", tags=base_tags)
            
        except Exception as e:
            logger.warning(f"Failed to emit LLM metrics: {e}")
    
    def track_quality_metrics(
        self,
        semantic_similarity_score: float,
        ungrounded_flag: bool = False,
        provider: str = "google",
        model: str = "gemini-1.5-pro",
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        EXTENSION: Track quality metrics as custom metrics.
        This extends Datadog's native LLM Observability with semantic similarity analysis.
        """
        if not self.enabled:
            return
        
        try:
            from datadog import statsd
            
            base_tags = [
                f"llm_provider:{provider}",
                f"llm_model:{model}",
            ]
            
            if tags:
                base_tags.extend([f"{k}:{v}" for k, v in tags.items()])
            
            # Quality metrics (extends native LLM Observability)
            statsd.gauge("llm.quality.semantic_similarity", semantic_similarity_score, tags=base_tags)
            statsd.gauge("llm.quality.ungrounded", float(ungrounded_flag), tags=base_tags)
            statsd.gauge("llm.quality.good", float(semantic_similarity_score > 0.7), tags=base_tags)
            statsd.gauge("llm.quality.degraded", float(semantic_similarity_score < 0.4), tags=base_tags)
            
        except Exception as e:
            logger.warning(f"Failed to emit quality metrics: {e}")


class LLMObservabilityContext:
    """
    Context object for tracking LLM request metadata during generation.
    Extended with semantic similarity and quality metrics.
    """
    
    def __init__(self, span=None):
        self.span = span
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_tokens = 0
        self.cost_usd = 0.0
        self.model: Optional[str] = None
        self.latency_ms: Optional[float] = None
        self.error: Optional[Exception] = None
        self.error_type: Optional[str] = None
        # EXTENSION: Semantic similarity and quality metrics (extends native LLM Observability)
        self.semantic_similarity_score: Optional[float] = None
        self.ungrounded_flag: Optional[bool] = None
        self.response_length: Optional[int] = None
    
    def set_tokens(self, input_tokens: int, output_tokens: int):
        """Set token counts."""
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens
        
        if self.span:
            self.span.set_tag("llm.request.input_tokens", input_tokens)
            self.span.set_tag("llm.response.output_tokens", output_tokens)
            self.span.set_tag("llm.request.token_count", self.total_tokens)
    
    def set_cost(self, cost_usd: float):
        """Set cost in USD."""
        self.cost_usd = cost_usd
        if self.span:
            self.span.set_tag("llm.request.cost", cost_usd)
    
    def set_model(self, model: str):
        """Set response model name."""
        self.model = model
        if self.span:
            self.span.set_tag("llm.response.model", model)
    
    def set_error(self, error: Exception):
        """Set error information."""
        self.error = error
        self.error_type = type(error).__name__
        if self.span:
            self.span.set_tag("error", True)
            self.span.set_tag("error.type", self.error_type)
            self.span.set_tag("error.message", str(error))
    
    def set_quality_metrics(
        self,
        semantic_similarity_score: float,
        ungrounded_flag: bool = False,
        response_length: Optional[int] = None,
    ):
        """
        EXTENSION: Set quality metrics (semantic similarity, grounding, response length).
        This extends Datadog's native LLM Observability with our custom quality analysis.
        """
        self.semantic_similarity_score = semantic_similarity_score
        self.ungrounded_flag = ungrounded_flag
        if response_length is not None:
            self.response_length = response_length
        
        if self.span:
            self.span.set_tag("llm.quality.semantic_similarity", semantic_similarity_score)
            self.span.set_tag("llm.quality.good", semantic_similarity_score > 0.7)
            self.span.set_tag("llm.quality.degraded", semantic_similarity_score < 0.4)
            self.span.set_tag("llm.quality.ungrounded", ungrounded_flag)
            if response_length is not None:
                self.span.set_tag("llm.response.length", response_length)


# Global instance
_llm_observability: Optional[DatadogLLMObservability] = None


def get_llm_observability() -> DatadogLLMObservability:
    """Get or create global LLM Observability instance."""
    global _llm_observability
    if _llm_observability is None:
        _llm_observability = DatadogLLMObservability()
    return _llm_observability

