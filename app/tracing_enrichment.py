"""
Distributed Tracing Context Propagation and Enrichment

This module provides enhanced distributed tracing with context propagation,
resource-level tagging, and infrastructure correlation.
"""

import os
import logging
from typing import Any, Dict, Optional
import platform

logger = logging.getLogger(__name__)

try:
    from ddtrace import tracer
    DD_TRACING_ENABLED = True
except ImportError:
    DD_TRACING_ENABLED = False
    tracer = None


def get_host_metadata() -> Dict[str, str]:
    """Get host/infrastructure metadata for tagging."""
    return {
        "host.name": platform.node(),
        "host.platform": platform.platform(),
        "host.arch": platform.machine(),
        "host.processor": platform.processor(),
        "host.python.version": platform.python_version(),
    }


def enrich_span_with_infrastructure(span) -> None:
    """
    Enrich span with infrastructure and resource-level tags.
    Extends native Datadog tracing with infrastructure correlation.
    """
    if not span:
        return
    
    # Host/Infrastructure tags
    host_metadata = get_host_metadata()
    for key, value in host_metadata.items():
        if value:
            span.set_tag(key, value)
    
    # Environment tags
    span.set_tag("deployment.environment", os.getenv("DD_ENV", "local"))
    span.set_tag("deployment.version", os.getenv("DD_VERSION", "0.1.0"))
    
    # Resource tags (extend beyond basic service tags)
    span.set_tag("resource.type", "llm_api")
    span.set_tag("resource.region", os.getenv("DD_REGION", "us-east-1"))
    span.set_tag("resource.zone", os.getenv("DD_ZONE", "unknown"))
    
    # Infrastructure correlation tags
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        span.set_tag("infrastructure.type", "kubernetes")
        span.set_tag("infrastructure.cluster", os.getenv("KUBERNETES_CLUSTER", "unknown"))
        span.set_tag("infrastructure.namespace", os.getenv("KUBERNETES_NAMESPACE", "default"))
    
    # Cloud provider tags
    if os.getenv("GCP_PROJECT"):
        span.set_tag("cloud.provider", "gcp")
        span.set_tag("cloud.project_id", os.getenv("GCP_PROJECT"))
        span.set_tag("cloud.region", os.getenv("GCP_REGION", "us-central1"))
    elif os.getenv("AWS_REGION"):
        span.set_tag("cloud.provider", "aws")
        span.set_tag("cloud.region", os.getenv("AWS_REGION"))


def propagate_trace_context(headers: Dict[str, str]) -> Dict[str, str]:
    """
    Propagate distributed tracing context in HTTP headers.
    Enables trace correlation across services.
    """
    if not DD_TRACING_ENABLED or not tracer:
        return headers
    
    try:
        current_span = tracer.current_span()
        if current_span:
            trace_id = str(current_span.trace_id)
            span_id = str(current_span.span_id)
            
            # Datadog trace context headers
            headers["x-datadog-trace-id"] = trace_id
            headers["x-datadog-parent-id"] = span_id
            headers["x-datadog-sampling-priority"] = "1"
            
            # W3C Trace Context (for interoperability)
            headers["traceparent"] = f"00-{trace_id:032x}-{span_id:016x}-01"
            
    except Exception as e:
        logger.warning(f"Failed to propagate trace context: {e}")
    
    return headers


def extract_trace_context(headers: Dict[str, str]) -> Optional[Dict[str, str]]:
    """
    Extract distributed tracing context from HTTP headers.
    Enables trace correlation when receiving requests.
    """
    context = {}
    
    # Datadog headers
    if "x-datadog-trace-id" in headers:
        context["trace_id"] = headers["x-datadog-trace-id"]
    if "x-datadog-parent-id" in headers:
        context["parent_id"] = headers["x-datadog-parent-id"]
    
    # W3C Trace Context
    if "traceparent" in headers:
        try:
            traceparent = headers["traceparent"]
            parts = traceparent.split("-")
            if len(parts) >= 3:
                context["trace_id"] = parts[1]
                context["parent_id"] = parts[2]
        except Exception as e:
            logger.warning(f"Failed to parse traceparent: {e}")
    
    return context if context else None


def add_resource_tags(
    span,
    resource_name: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    additional_tags: Optional[Dict[str, str]] = None,
) -> None:
    """
    Add resource-level tags to span for infrastructure correlation.
    
    Args:
        span: Datadog span
        resource_name: Name of the resource (e.g., "vertex-ai-endpoint")
        resource_type: Type of resource (e.g., "llm_endpoint", "database", "cache")
        resource_id: Optional resource identifier
        additional_tags: Optional additional resource tags
    """
    if not span:
        return
    
    span.set_tag("resource.name", resource_name)
    span.set_tag("resource.type", resource_type)
    
    if resource_id:
        span.set_tag("resource.id", resource_id)
    
    if additional_tags:
        for key, value in additional_tags.items():
            span.set_tag(f"resource.{key}", value)


def correlate_infrastructure_metrics(span, metric_tags: Optional[Dict[str, str]] = None) -> None:
    """
    Add tags that enable correlation between application traces and infrastructure metrics.
    
    Args:
        span: Datadog span
        metric_tags: Tags that match infrastructure metric tags (e.g., host tags)
    """
    if not span:
        return
    
    # Add host tags for infrastructure correlation
    host_metadata = get_host_metadata()
    if "host.name" in host_metadata:
        span.set_tag("host", host_metadata["host.name"])
    
    # Add custom metric correlation tags
    if metric_tags:
        for key, value in metric_tags.items():
            span.set_tag(f"infra.{key}", value)


# Global context manager for enriched spans
class EnrichedSpanContext:
    """Context manager for enriched spans with infrastructure correlation."""
    
    def __init__(self, operation_name: str, service: str = "llm-reliability-control-plane", **kwargs):
        self.operation_name = operation_name
        self.service = service
        self.kwargs = kwargs
        self.span = None
    
    def __enter__(self):
        if DD_TRACING_ENABLED and tracer:
            self.span = tracer.trace(
                self.operation_name,
                service=self.service,
                **self.kwargs
            )
            enrich_span_with_infrastructure(self.span)
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span:
            self.span.finish()
        return False

