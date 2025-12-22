from __future__ import annotations

import json
import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Dict, Iterator

from .config import settings

# Configure structured logging for Datadog
logger = logging.getLogger("llm_reliability_control_plane")
logger.setLevel(logging.INFO)

# Use JSON formatter for Datadog log ingestion
if os.getenv("DD_LOGS_ENABLED", "true").lower() == "true":
    try:
        from pythonjsonlogger import jsonlogger

        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s",
            timestamp=True,
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except ImportError:
        # Fallback to standard logging if jsonlogger not available
        logging.basicConfig(level=logging.INFO)

# Initialize Datadog StatsD for custom metrics
try:
    from datadog import initialize, statsd

    if settings.datadog_api_key:
        initialize(
            api_key=settings.datadog_api_key,
            app_key=os.getenv("DD_APP_KEY"),  # Optional, for API calls
            api_host=os.getenv("DD_SITE", "datadoghq.com"),
            statsd_host=os.getenv("DD_AGENT_HOST", "localhost"),
            statsd_port=int(os.getenv("DD_DOGSTATSD_PORT", "8125")),
        )
except Exception:  # noqa: BLE001
    statsd = None  # type: ignore[assignment]


def _tags(extra: Dict[str, str] | None = None) -> list[str]:
    base = {
        "env": settings.datadog_env,
        "service": settings.datadog_service,
    }
    if extra:
        base.update(extra)
    return [f"{k}:{v}" for k, v in base.items() if v is not None]


@contextmanager
def record_latency(
    metric_name: str,
    *,
    tags: Dict[str, str] | None = None,
) -> Iterator[None]:
    start = time.monotonic()
    try:
        yield
    finally:
        latency_ms = (time.monotonic() - start) * 1000.0
        emit_histogram(metric_name, latency_ms, tags=tags)


def emit_histogram(name: str, value: float, *, tags: Dict[str, str] | None = None) -> None:
    tag_list = _tags(tags)
    if statsd:
        statsd.histogram(name, value, tags=tag_list)
    logger.info("metric_histogram %s=%s tags=%s", name, value, tag_list)


def emit_counter(name: str, value: int = 1, *, tags: Dict[str, str] | None = None) -> None:
    tag_list = _tags(tags)
    if statsd:
        statsd.increment(name, value, tags=tag_list)
    logger.info("metric_counter %s+=%s tags=%s", name, value, tag_list)


def emit_gauge(name: str, value: float, *, tags: Dict[str, str] | None = None) -> None:
    tag_list = _tags(tags)
    if statsd:
        statsd.gauge(name, value, tags=tag_list)
    logger.info("metric_gauge %s=%s tags=%s", name, value, tag_list)


def emit_llm_metrics(
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
) -> None:
    base_tags = {
        "endpoint": endpoint,
        "model": model,
        "model_version": model_version,
        "request_type": request_type,
    }

    # Performance
    emit_histogram("llm.request.latency_ms", latency_ms, tags=base_tags)
    emit_histogram("llm.time_to_first_token_ms", latency_ms, tags=base_tags)  # synthetic
    emit_gauge("llm.retry_count", retry_count, tags=base_tags)

    # Reliability
    if error:
        emit_counter("llm.error.count", tags=base_tags)
    if latency_ms > 10_000:
        emit_counter("llm.timeout.count", tags=base_tags)
    if not error and (input_tokens == 0 or output_tokens == 0):
        emit_counter("llm.empty_response.count", tags=base_tags)
    if safety_block:
        emit_counter("llm.safety_block.count", tags=base_tags)

    # Cost
    emit_gauge("llm.tokens.input", input_tokens, tags=base_tags)
    emit_gauge("llm.tokens.output", output_tokens, tags=base_tags)
    emit_gauge("llm.cost.usd", cost_usd, tags=base_tags)

    # Security signals
    # Detect potential prompt injection (heuristic: suspicious patterns)
    prompt_injection_risk = False
    if request_type in ("qa", "reason"):
        # Simple heuristic: very long prompts or suspicious patterns
        if input_tokens > 1000:
            prompt_injection_risk = True
    if prompt_injection_risk:
        emit_counter("llm.security.prompt_injection_risk", tags=base_tags)

    # Token abuse detection (unusually high token usage)
    total_tokens = input_tokens + output_tokens
    if total_tokens > 5000:
        emit_counter("llm.security.token_abuse", tags=base_tags)

    # Quality (already named as final metric keys)
    for key, val in quality.items():
        if isinstance(val, bool):
            emit_gauge(key, float(val), tags=base_tags)
        elif isinstance(val, (int, float)):
            emit_gauge(key, float(val), tags=base_tags)


def log_request(
    *,
    prompt_id: str,
    endpoint: str,
    request_type: str,
    prompt: str,
    response_text: str,
    metadata: Dict[str, Any],
) -> None:
    """
    Emit structured log for Datadog ingestion.
    These logs will be automatically attached to incidents and traces.
    """
    truncated_prompt = (prompt[:200] + "...") if len(prompt) > 200 else prompt
    log_payload = {
        "prompt_id": prompt_id,
        "endpoint": endpoint,
        "request_type": request_type,
        "prompt": truncated_prompt,
        "response_preview": response_text[:200],
        "metadata": metadata,
        # Datadog log attributes for correlation
        "dd.service": settings.datadog_service,
        "dd.env": settings.datadog_env,
        "dd.version": settings.datadog_version,
    }
    # Use JSON logging if available, otherwise structured string
    try:
        logger.info("llm_request", extra=log_payload)
    except Exception:  # noqa: BLE001
        logger.info("llm_request_log %s", json.dumps(log_payload))


