"""
Datadog Error Tracking Integration

Deep integration with Datadog Error Tracking for enhanced error monitoring.
Tracks errors with context, stack traces, and user impact.
"""

import os
import logging
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from datadog import api, statsd
    DD_API_AVAILABLE = True
except ImportError:
    DD_API_AVAILABLE = False
    logger.warning("Datadog API not available. Install: pip install datadog")

try:
    from ddtrace import tracer
    DD_TRACING_ENABLED = True
except ImportError:
    DD_TRACING_ENABLED = False
    tracer = None


class ErrorTrackingIntegration:
    """
    Deep integration with Datadog Error Tracking.
    
    Tracks errors with full context, stack traces, and user impact.
    """
    
    def __init__(self):
        if DD_API_AVAILABLE:
            self.api_key = os.getenv("DD_API_KEY") or os.getenv("LRCP_DATADOG_API_KEY")
            self.app_key = os.getenv("DD_APP_KEY")
            if self.api_key and self.app_key:
                api._api_key = self.api_key
                api._application_key = self.app_key
                self.enabled = True
            else:
                self.enabled = False
        else:
            self.enabled = False
    
    def track_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        severity: str = "error",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Track an error with full context.
        
        This demonstrates deep integration: programmatically tracking
        errors with context for Error Tracking.
        """
        if not self.enabled:
            logger.warning("Error Tracking disabled: Missing API keys")
            return {"error": "Error Tracking disabled"}
        
        try:
            error_type = type(error).__name__
            error_message = str(error)
            stack_trace = traceback.format_exc()
            
            # Create error event
            event_data = {
                "title": f"🚨 Error: {error_type}",
                "text": f"{error_message}\n\n**Stack Trace:**\n```\n{stack_trace}\n```\n\n**Context:**\n{self._format_context(context)}",
                "alert_type": "error",
                "source_type_name": "Error Tracking",
                "tags": [
                    "error",
                    f"error_type:{error_type}",
                    f"severity:{severity}",
                    "llm",
                    "error_tracking",
                ],
            }
            
            if tags:
                event_data["tags"].extend(tags)
            
            if user_id:
                event_data["tags"].append(f"user_id:{user_id}")
            
            if context:
                for key, value in context.items():
                    if isinstance(value, (str, int, float, bool)):
                        event_data["tags"].append(f"{key}:{value}")
            
            # Create event
            event = api.Event.create(**event_data)
            
            # Emit error metrics
            statsd.increment(
                "error.count",
                tags=[
                    f"error_type:{error_type}",
                    f"severity:{severity}",
                    "service:llm-reliability-control-plane",
                ]
            )
            
            # Add error to trace if available
            if DD_TRACING_ENABLED and tracer:
                span = tracer.current_span()
                if span:
                    span.set_tag("error", True)
                    span.set_tag("error.type", error_type)
                    span.set_tag("error.message", error_message)
                    span.set_tag("error.stack", stack_trace)
            
            logger.error(f"Tracked error: {error_type} - {error_message}")
            return {
                "status": "tracked",
                "event_id": event.get("event", {}).get("id"),
                "error_type": error_type,
                "error_message": error_message,
            }
            
        except Exception as e:
            logger.error(f"Failed to track error: {e}")
            return {"error": str(e)}
    
    def track_llm_error(
        self,
        error: Exception,
        provider: str,
        model: str,
        prompt: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Track an LLM-specific error with context.
        
        This demonstrates deep integration: tracking LLM errors
        with provider, model, and prompt context.
        """
        context = {
            "provider": provider,
            "model": model,
            "service": "llm-reliability-control-plane",
        }
        
        if prompt:
            # Truncate prompt for error tracking
            context["prompt_length"] = len(prompt)
            context["prompt_preview"] = prompt[:100] + "..." if len(prompt) > 100 else prompt
        
        return self.track_error(
            error=error,
            context=context,
            user_id=user_id,
            severity="error",
            tags=["llm", "llm_error", f"provider:{provider}", f"model:{model}"],
        )
    
    def track_cost_error(
        self,
        error: Exception,
        cost_calculation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Track a cost calculation error."""
        return self.track_error(
            error=error,
            context=cost_calculation or {},
            severity="warning",
            tags=["llm", "cost", "calculation_error"],
        )
    
    def track_quality_error(
        self,
        error: Exception,
        quality_calculation: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Track a quality calculation error."""
        return self.track_error(
            error=error,
            context=quality_calculation or {},
            severity="warning",
            tags=["llm", "quality", "calculation_error"],
        )
    
    def _format_context(self, context: Optional[Dict[str, Any]]) -> str:
        """Format context dictionary for error message."""
        if not context:
            return "No additional context"
        
        lines = []
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"- **{key}**: {value}")
            elif isinstance(value, dict):
                lines.append(f"- **{key}**: {self._format_context(value)}")
        
        return "\n".join(lines) if lines else "No additional context"
    
    def get_error_summary(
        self,
        hours: int = 24,
        error_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get error summary for the last N hours.
        
        This demonstrates deep integration: querying error data
        from Datadog Error Tracking.
        """
        if not self.enabled:
            return {"error": "Error Tracking disabled"}
        
        try:
            # Query errors from Datadog
            # Note: Error Tracking API format may vary
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (hours * 3600)
            
            # Query error events
            events = api.Event.query(
                start=start_time,
                end=end_time,
                tags=["error", "llm"] + ([f"error_type:{error_type}"] if error_type else []),
                page_size=100,
            )
            
            error_count = len(events.get("events", []))
            
            # Group by error type
            error_types = {}
            for event in events.get("events", []):
                event_type = next(
                    (tag.split(":")[1] for tag in event.get("tags", []) if tag.startswith("error_type:")),
                    "unknown"
                )
                error_types[event_type] = error_types.get(event_type, 0) + 1
            
            return {
                "period_hours": hours,
                "total_errors": error_count,
                "error_types": error_types,
                "errors": events.get("events", [])[:10],  # Top 10
            }
            
        except Exception as e:
            logger.error(f"Failed to get error summary: {e}")
            return {"error": str(e)}


# Global instance
_error_tracking: Optional[ErrorTrackingIntegration] = None


def get_error_tracking() -> ErrorTrackingIntegration:
    """Get or create global ErrorTrackingIntegration instance."""
    global _error_tracking
    if _error_tracking is None:
        _error_tracking = ErrorTrackingIntegration()
    return _error_tracking

