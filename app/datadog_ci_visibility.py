"""
Datadog CI Visibility Integration

Deep integration with Datadog CI Visibility for build and deployment tracking.
Tracks CI/CD pipelines, test results, and deployments.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from datadog import api, statsd
    DD_API_AVAILABLE = True
except ImportError:
    DD_API_AVAILABLE = False
    logger.warning("Datadog API not available. Install: pip install datadog")


class CIVisibilityIntegration:
    """
    Deep integration with Datadog CI Visibility.
    
    Tracks CI/CD pipelines, test results, and deployments.
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
    
    def track_deployment(
        self,
        service: str,
        version: str,
        environment: str = "production",
        git_commit: Optional[str] = None,
        git_branch: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Track a deployment event.
        
        This demonstrates deep integration: programmatically tracking
        deployments for CI Visibility.
        """
        if not self.enabled:
            logger.warning("CI Visibility disabled: Missing API keys")
            return {"error": "CI Visibility disabled"}
        
        try:
            # Create deployment event
            event_data = {
                "title": f"🚀 Deployment: {service} v{version}",
                "text": f"Deployed {service} version {version} to {environment}\n\nGit Commit: {git_commit or 'N/A'}\nGit Branch: {git_branch or 'N/A'}",
                "alert_type": "info",
                "source_type_name": "CI/CD",
                "tags": [
                    "deployment",
                    f"service:{service}",
                    f"version:{version}",
                    f"environment:{environment}",
                    "ci_visibility",
                ],
            }
            
            if git_commit:
                event_data["tags"].append(f"git.commit:{git_commit}")
            if git_branch:
                event_data["tags"].append(f"git.branch:{git_branch}")
            
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        event_data["tags"].append(f"{key}:{value}")
            
            event = api.Event.create(**event_data)
            
            # Also emit deployment metric
            statsd.increment(
                "ci.deployment.count",
                tags=[
                    f"service:{service}",
                    f"version:{version}",
                    f"environment:{environment}",
                ]
            )
            
            logger.info(f"Tracked deployment: {service} v{version} to {environment}")
            return {
                "status": "tracked",
                "event_id": event.get("event", {}).get("id"),
                "service": service,
                "version": version,
                "environment": environment,
            }
            
        except Exception as e:
            logger.error(f"Failed to track deployment: {e}")
            return {"error": str(e)}
    
    def track_test_result(
        self,
        test_name: str,
        status: str,  # "pass", "fail", "skip"
        duration_ms: float,
        service: str = "llm-reliability-control-plane",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Track a test result.
        
        This demonstrates deep integration: tracking test results
        for CI Visibility.
        """
        if not self.enabled:
            return {"error": "CI Visibility disabled"}
        
        try:
            # Emit test result metric
            tags = [
                f"test:{test_name}",
                f"status:{status}",
                f"service:{service}",
                "ci_visibility",
            ]
            
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        tags.append(f"{key}:{value}")
            
            statsd.increment(
                "ci.test.count",
                tags=tags,
            )
            
            statsd.histogram(
                "ci.test.duration",
                duration_ms,
                tags=tags,
            )
            
            if status == "fail":
                statsd.increment(
                    "ci.test.failure",
                    tags=tags,
                )
            
            logger.info(f"Tracked test result: {test_name} - {status}")
            return {
                "status": "tracked",
                "test_name": test_name,
                "result": status,
                "duration_ms": duration_ms,
            }
            
        except Exception as e:
            logger.error(f"Failed to track test result: {e}")
            return {"error": str(e)}
    
    def track_build(
        self,
        build_id: str,
        status: str,  # "success", "failure", "cancelled"
        duration_ms: float,
        service: str = "llm-reliability-control-plane",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Track a build event."""
        if not self.enabled:
            return {"error": "CI Visibility disabled"}
        
        try:
            tags = [
                f"build_id:{build_id}",
                f"status:{status}",
                f"service:{service}",
                "ci_visibility",
            ]
            
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        tags.append(f"{key}:{value}")
            
            statsd.increment(
                "ci.build.count",
                tags=tags,
            )
            
            statsd.histogram(
                "ci.build.duration",
                duration_ms,
                tags=tags,
            )
            
            if status == "failure":
                statsd.increment(
                    "ci.build.failure",
                    tags=tags,
                )
            
            logger.info(f"Tracked build: {build_id} - {status}")
            return {
                "status": "tracked",
                "build_id": build_id,
                "result": status,
                "duration_ms": duration_ms,
            }
            
        except Exception as e:
            logger.error(f"Failed to track build: {e}")
            return {"error": str(e)}


# Global instance
_ci_visibility: Optional[CIVisibilityIntegration] = None


def get_ci_visibility() -> CIVisibilityIntegration:
    """Get or create global CIVisibilityIntegration instance."""
    global _ci_visibility
    if _ci_visibility is None:
        _ci_visibility = CIVisibilityIntegration()
    return _ci_visibility

