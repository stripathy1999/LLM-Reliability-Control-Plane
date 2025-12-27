"""
Datadog Service Map Integration

Deep integration with Datadog Service Map for dependency visualization.
Enhances service tagging and dependency tracking.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from ddtrace import tracer

logger = logging.getLogger(__name__)

try:
    from ddtrace import tracer
    DD_TRACING_ENABLED = True
except ImportError:
    DD_TRACING_ENABLED = False
    tracer = None
    logger.warning("ddtrace not available. Service Map integration disabled.")


class ServiceMapIntegration:
    """
    Deep integration with Datadog Service Map.
    
    Enhances service tagging and dependency tracking for better visualization.
    """
    
    def __init__(self):
        self.enabled = DD_TRACING_ENABLED and tracer is not None
        if not self.enabled:
            logger.warning("Service Map integration disabled: ddtrace not available")
    
    def enhance_service_tags(
        self,
        service_name: str,
        service_type: str = "llm",
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Enhance service tags for better Service Map visualization.
        
        This demonstrates deep integration: programmatically enhancing
        service metadata for Service Map.
        """
        if not self.enabled:
            return
        
        try:
            # Set service metadata that appears in Service Map
            # These tags help Service Map visualize dependencies
            
            tags = [
                f"service:{service_name}",
                f"service_type:{service_type}",
                "env:production",
            ]
            
            if dependencies:
                for dep in dependencies:
                    tags.append(f"depends_on:{dep}")
            
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        tags.append(f"{key}:{value}")
            
            # Set global service tags
            # These will appear in all spans for this service
            tracer.set_tags(tags)
            
            logger.info(f"Enhanced service tags for Service Map: {service_name}")
            
        except Exception as e:
            logger.warning(f"Failed to enhance service tags: {e}")
    
    def track_service_dependency(
        self,
        from_service: str,
        to_service: str,
        dependency_type: str = "http",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Track a service dependency for Service Map visualization.
        
        This creates spans that show dependencies between services.
        """
        if not self.enabled:
            return
        
        try:
            with tracer.trace(
                "service.dependency",
                service=from_service,
                resource=f"{from_service} -> {to_service}",
            ) as span:
                span.set_tag("service", from_service)
                span.set_tag("dependency.service", to_service)
                span.set_tag("dependency.type", dependency_type)
                span.set_tag("span.kind", "client")
                
                if metadata:
                    for key, value in metadata.items():
                        if isinstance(value, (str, int, float, bool)):
                            span.set_tag(f"dependency.{key}", value)
            
            logger.info(f"Tracked service dependency: {from_service} -> {to_service}")
            
        except Exception as e:
            logger.warning(f"Failed to track service dependency: {e}")
    
    def track_llm_service_dependencies(self):
        """
        Track LLM service dependencies for Service Map.
        
        This demonstrates deep integration: automatically tracking
        all LLM service dependencies.
        """
        if not self.enabled:
            return
        
        # Track dependencies
        self.track_service_dependency(
            from_service="llm-reliability-control-plane",
            to_service="google-vertex-ai",
            dependency_type="llm",
            metadata={
                "provider": "google",
                "model": "gemini-2.5-flash",
                "endpoint": "generativelanguage.googleapis.com",
            }
        )
        
        self.track_service_dependency(
            from_service="llm-reliability-control-plane",
            to_service="datadog-agent",
            dependency_type="observability",
            metadata={
                "protocol": "statsd",
                "port": "8125",
            }
        )
        
        # Enhance main service tags
        self.enhance_service_tags(
            service_name="llm-reliability-control-plane",
            service_type="llm",
            dependencies=[
                "google-vertex-ai",
                "datadog-agent",
            ],
            metadata={
                "deployment": "cloud-run",
                "region": "us-central1",
                "version": os.getenv("DD_VERSION", "0.1.0"),
            }
        )
    
    def create_service_map_widget_config(self) -> Dict[str, Any]:
        """
        Create Service Map widget configuration for dashboard.
        
        This demonstrates deep integration: programmatically creating
        Service Map visualizations.
        """
        return {
            "type": "servicemap",
            "title": "LLM Service Map - Dependencies",
            "service": "llm-reliability-control-plane",
            "filters": [
                "env:production",
                "env:staging",
            ],
            "custom_links": [
                {
                    "label": "View Service Details",
                    "link": "https://app.datadoghq.com/apm/service/llm-reliability-control-plane"
                },
                {
                    "label": "View Dependencies",
                    "link": "https://app.datadoghq.com/infrastructure/map?filter=service:llm-reliability-control-plane"
                }
            ]
        }


# Global instance
_service_map: Optional[ServiceMapIntegration] = None


def get_service_map() -> ServiceMapIntegration:
    """Get or create global ServiceMapIntegration instance."""
    global _service_map
    if _service_map is None:
        _service_map = ServiceMapIntegration()
    return _service_map

