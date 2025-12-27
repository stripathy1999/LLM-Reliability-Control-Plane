"""
Datadog Product Analytics Integration

This module provides product analytics tracking for user interactions and feature usage.
Tracks user behavior, feature adoption, and business metrics in Datadog.
"""

import os
import logging
from typing import Any, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from datadog import api, statsd
    DD_API_AVAILABLE = True
except ImportError:
    DD_API_AVAILABLE = False
    statsd = None
    logger.warning("Datadog API not available. Install: pip install datadog")


class ProductAnalytics:
    """
    Product Analytics tracking for LLM application.
    
    Tracks user interactions, feature usage, and business metrics.
    """
    
    def __init__(self):
        self.enabled = DD_API_AVAILABLE and statsd is not None
        if not self.enabled:
            logger.warning("Product Analytics disabled: Datadog not available")
    
    def track_event(
        self,
        event_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """
        Track a product analytics event.
        
        Args:
            event_name: Name of the event (e.g., "endpoint_used", "feature_enabled")
            user_id: Optional user identifier
            session_id: Optional session identifier
            properties: Additional event properties
        """
        if not self.enabled:
            return
        
        try:
            # Create event properties
            event_properties = properties or {}
            if user_id:
                event_properties["user_id"] = user_id
            if session_id:
                event_properties["session_id"] = session_id
            
            # Tags for the event
            tags = [
                f"event:{event_name}",
                "product:llm_reliability_control_plane",
            ]
            if user_id:
                tags.append(f"user_id:{user_id}")
            if session_id:
                tags.append(f"session_id:{session_id}")
            
            # Emit as custom event
            if api:
                try:
                    api.Event.create(
                        title=f"Product Analytics: {event_name}",
                        text=str(event_properties),
                        alert_type="info",
                        source_type_name="Product Analytics",
                        tags=tags,
                    )
                except Exception as e:
                    logger.warning(f"Failed to create event: {e}")
            
            # Also emit as metric for aggregation
            statsd.increment(
                f"product_analytics.{event_name}",
                tags=tags,
            )
            
            logger.info(f"Tracked product analytics event: {event_name}", extra=event_properties)
            
        except Exception as e:
            logger.warning(f"Failed to track product analytics event: {e}")
    
    def track_endpoint_usage(
        self,
        endpoint: str,
        request_type: str,
        user_id: Optional[str] = None,
        success: bool = True,
        latency_ms: float = 0.0,
        cost_usd: float = 0.0,
    ):
        """Track endpoint usage."""
        self.track_event(
            "endpoint_used",
            user_id=user_id,
            properties={
                "endpoint": endpoint,
                "request_type": request_type,
                "success": success,
                "latency_ms": latency_ms,
                "cost_usd": cost_usd,
            },
        )
        
        # Also emit detailed metrics
        if self.enabled:
            tags = [
                f"endpoint:{endpoint}",
                f"request_type:{request_type}",
                f"success:{success}",
            ]
            if user_id:
                tags.append(f"user_id:{user_id}")
            
            statsd.increment("product_analytics.endpoint_usage", tags=tags)
            statsd.histogram("product_analytics.endpoint_latency", latency_ms, tags=tags)
            if cost_usd > 0:
                statsd.histogram("product_analytics.endpoint_cost", cost_usd, tags=tags)
    
    def track_feature_usage(
        self,
        feature_name: str,
        user_id: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Track feature usage."""
        self.track_event(
            "feature_used",
            user_id=user_id,
            properties={
                "feature_name": feature_name,
                **(properties or {}),
            },
        )
    
    def track_user_action(
        self,
        action: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Track user action (e.g., button click, form submission)."""
        self.track_event(
            "user_action",
            user_id=user_id,
            properties={
                "action": action,
                **(context or {}),
            },
        )
    
    def track_conversion(
        self,
        conversion_type: str,
        user_id: Optional[str] = None,
        value: Optional[float] = None,
        properties: Optional[Dict[str, Any]] = None,
    ):
        """Track conversion event (e.g., successful request, cost savings)."""
        props = {
            "conversion_type": conversion_type,
            **(properties or {}),
        }
        if value is not None:
            props["value"] = value
        
        self.track_event(
            "conversion",
            user_id=user_id,
            properties=props,
        )
        
        # Emit conversion metric
        if self.enabled and value is not None:
            tags = [f"conversion_type:{conversion_type}"]
            if user_id:
                tags.append(f"user_id:{user_id}")
            statsd.histogram("product_analytics.conversion_value", value, tags=tags)


# Global instance
_product_analytics: Optional[ProductAnalytics] = None


def get_product_analytics() -> ProductAnalytics:
    """Get or create global ProductAnalytics instance."""
    global _product_analytics
    if _product_analytics is None:
        _product_analytics = ProductAnalytics()
    return _product_analytics


def track_endpoint_usage(
    endpoint: str,
    request_type: str,
    user_id: Optional[str] = None,
    success: bool = True,
    latency_ms: float = 0.0,
    cost_usd: float = 0.0,
):
    """Convenience function to track endpoint usage."""
    analytics = get_product_analytics()
    analytics.track_endpoint_usage(
        endpoint=endpoint,
        request_type=request_type,
        user_id=user_id,
        success=success,
        latency_ms=latency_ms,
        cost_usd=cost_usd,
    )

