"""
Unified Telemetry Layer

This module provides telemetry for Datadog observability.
All telemetry is sent to Datadog for comprehensive monitoring.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict

from .telemetry import emit_llm_metrics as datadog_emit_metrics

# Confluent is optional - only import if available
try:
    from .confluent_producer import get_confluent_producer
    CONFLUENT_AVAILABLE = True
except ImportError:
    CONFLUENT_AVAILABLE = False
    get_confluent_producer = None  # type: ignore[assignment, misc]

logger = None
try:
    import logging
    logger = logging.getLogger(__name__)
except Exception:
    pass


class UnifiedTelemetry:
    """
    Unified telemetry that sends data to Datadog.
    
    - Datadog: For comprehensive observability (metrics, traces, logs)
    
    All LLM telemetry is sent to Datadog for monitoring and analysis.
    """

    def __init__(self):
        self.datadog_enabled = os.getenv("DD_ENABLED", "true").lower() == "true"
        if CONFLUENT_AVAILABLE and get_confluent_producer:
            self.confluent_producer = get_confluent_producer()
            self.confluent_enabled = self.confluent_producer.enabled
        else:
            self.confluent_producer = None
            self.confluent_enabled = False

    def emit_llm_metrics_unified(
        self,
        *,
        endpoint: str,
        model: str,
        model_version: str,
        request_type: str,
        latency_ms: float,
        retry_count: int,
        error: str | None,
        safety_block: bool,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        quality: Dict[str, Any],
        request_id: str,
    ) -> None:
        """
        Emit metrics to Datadog for comprehensive observability.
        
        This is the core unified telemetry function that demonstrates
        how both platforms work together.
        """
        
        # PRIMARY TRACK 1: DATADOG (Observability)
        if self.datadog_enabled:
            try:
                datadog_emit_metrics(
                    endpoint=endpoint,
                    model=model,
                    model_version=model_version,
                    request_type=request_type,
                    latency_ms=latency_ms,
                    retry_count=retry_count,
                    error=error,
                    safety_block=safety_block,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=cost_usd,
                    quality=quality,
                )
            except Exception as e:
                if logger:
                    logger.error(f"Failed to emit to Datadog: {e}")

        # Confluent removed - Datadog-only telemetry
        if False:  # Confluent disabled
            try:
                # Stream event to Kafka for real-time ML processing
                metric_event = {
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "model": model,
                    "model_version": model_version,
                    "request_type": request_type,
                    "latency_ms": latency_ms,
                    "retry_count": retry_count,
                    "error": error,
                    "safety_block": safety_block,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost_usd": cost_usd,
                    "quality_scores": quality,
                    "timestamp": datetime.now().isoformat(),
                }
                
                self.confluent_producer.emit_llm_metric(metric_event)
            except Exception as e:
                if logger:
                    logger.error(f"Failed to emit to Confluent: {e}")

    def emit_llm_request_unified(
        self,
        *,
        request_id: str,
        endpoint: str,
        request_type: str,
        prompt: str,
        model: str,
    ) -> None:
        """Emit LLM request event to both platforms."""
        if self.confluent_enabled:
            try:
                request_event = {
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "request_type": request_type,
                    "prompt_preview": prompt[:200] if prompt else "",
                    "model": model,
                    "timestamp": datetime.now().isoformat(),
                }
                self.confluent_producer.emit_llm_request(request_event)
            except Exception as e:
                if logger:
                    logger.error(f"Failed to emit request telemetry: {e}")

    def emit_llm_response_unified(
        self,
        *,
        request_id: str,
        endpoint: str,
        response_text: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Emit LLM response event to both platforms."""
        if self.confluent_enabled:
            try:
                response_event = {
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "response_preview": response_text[:500] if response_text else "",
                    "metadata": metadata,
                    "timestamp": datetime.now().isoformat(),
                }
                self.confluent_producer.emit_llm_response(response_event)
            except Exception as e:
                if logger:
                    logger.error(f"Failed to emit response telemetry: {e}")


# Global unified telemetry instance
_unified_telemetry: UnifiedTelemetry | None = None


def get_unified_telemetry() -> UnifiedTelemetry:
    """Get or create global unified telemetry instance."""
    global _unified_telemetry
    if _unified_telemetry is None:
        _unified_telemetry = UnifiedTelemetry()
    return _unified_telemetry


