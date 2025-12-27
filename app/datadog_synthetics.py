"""
Datadog Synthetics Integration

Deep integration with Datadog Synthetics for API testing and monitoring.
Creates and manages synthetic tests programmatically.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from datadog import api
    DD_API_AVAILABLE = True
except ImportError:
    DD_API_AVAILABLE = False
    logger.warning("Datadog API not available. Install: pip install datadog")


class SyntheticsIntegration:
    """
    Deep integration with Datadog Synthetics.
    
    Creates, manages, and monitors synthetic API tests.
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
    
    def create_api_test(
        self,
        name: str,
        url: str,
        method: str = "GET",
        body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        assertions: Optional[List[Dict[str, Any]]] = None,
        locations: List[str] = None,
        frequency: int = 300,  # 5 minutes
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a synthetic API test.
        
        Args:
            name: Test name
            url: URL to test
            method: HTTP method
            body: Request body (for POST/PUT)
            headers: Request headers
            assertions: Assertions to validate response
            locations: Locations to run test from
            frequency: Test frequency in seconds
            tags: Tags for the test
        """
        if not self.enabled:
            logger.warning("Synthetics integration disabled: Missing API keys")
            return {"error": "Synthetics integration disabled"}
        
        if locations is None:
            locations = ["aws:us-east-1", "aws:eu-west-1"]
        
        if assertions is None:
            assertions = [
                {"type": "statusCode", "operator": "is", "target": 200},
                {"type": "responseTime", "operator": "lessThan", "target": 2000},
            ]
        
        if tags is None:
            tags = ["llm", "api", "synthetic"]
        
        try:
            # Create API test configuration
            test_config = {
                "name": name,
                "type": "api",
                "config": {
                    "request": {
                        "method": method,
                        "url": url,
                        "headers": headers or {},
                    },
                    "assertions": assertions,
                },
                "locations": locations,
                "options": {
                    "tick_every": frequency,
                    "min_failure_duration": 0,
                    "min_location_failed": 1,
                    "follow_redirects": True,
                    "retry": {
                        "count": 2,
                        "interval": 1000,
                    },
                },
                "message": f"🚨 **Synthetic Test Failed: {name}**\n\n**What failed?** API test failed for {url}\n\n**Why did it fail?** Possible causes:\n- Service is down or unreachable\n- Response time exceeded threshold\n- Response status code is not 200\n- Network connectivity issues\n\n**What should the engineer do next?**\n1. Check service health endpoint\n2. Review recent deployments\n3. Check network connectivity\n4. Review response time trends\n\n**Test Details:**\n- URL: {url}\n- Method: {method}\n- Locations: {', '.join(locations)}",
                "tags": tags,
            }
            
            if body:
                test_config["config"]["request"]["body"] = body
            
            # Create test via API
            response = api.Synthetics.create_test(**test_config)
            
            logger.info(f"Created synthetic API test: {name} (ID: {response.get('public_id')})")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create synthetic test: {e}")
            return {"error": str(e)}
    
    def create_health_check_test(self, service_url: str) -> Dict[str, Any]:
        """Create a health check synthetic test."""
        return self.create_api_test(
            name="LLM Control Plane Health Check",
            url=f"{service_url}/health",
            method="GET",
            assertions=[
                {"type": "statusCode", "operator": "is", "target": 200},
                {"type": "body", "operator": "contains", "target": "healthy"},
                {"type": "responseTime", "operator": "lessThan", "target": 1000},
            ],
            frequency=60,  # Every minute
            tags=["llm", "health", "critical"],
        )
    
    def create_qa_endpoint_test(self, service_url: str) -> Dict[str, Any]:
        """Create a test for the QA endpoint."""
        return self.create_api_test(
            name="LLM QA Endpoint Test",
            url=f"{service_url}/qa",
            method="POST",
            body='{"question": "What is Datadog?", "document": "Datadog is a monitoring platform."}',
            headers={"Content-Type": "application/json"},
            assertions=[
                {"type": "statusCode", "operator": "is", "target": 200},
                {"type": "body", "operator": "validatesJSONPath", "target": "$.answer"},
                {"type": "responseTime", "operator": "lessThan", "target": 5000},
            ],
            frequency=300,  # Every 5 minutes
            tags=["llm", "qa", "endpoint"],
        )
    
    def create_latency_test(self, service_url: str) -> Dict[str, Any]:
        """Create a latency-focused test."""
        return self.create_api_test(
            name="LLM Latency SLO Test",
            url=f"{service_url}/reason",
            method="POST",
            body='{"prompt": "Explain observability"}',
            headers={"Content-Type": "application/json"},
            assertions=[
                {"type": "statusCode", "operator": "is", "target": 200},
                {"type": "responseTime", "operator": "lessThan", "target": 2000},  # SLO threshold
            ],
            frequency=180,  # Every 3 minutes
            tags=["llm", "latency", "slo"],
        )
    
    def get_test_results(
        self,
        test_id: str,
        from_timestamp: Optional[int] = None,
        to_timestamp: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get results for a synthetic test."""
        if not self.enabled:
            return {"error": "Synthetics integration disabled"}
        
        try:
            if from_timestamp is None:
                from_timestamp = int((datetime.now().timestamp() - 3600))  # Last hour
            if to_timestamp is None:
                to_timestamp = int(datetime.now().timestamp())
            
            response = api.Synthetics.get_test_results(
                public_id=test_id,
                from_ts=from_timestamp,
                to_ts=to_timestamp,
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to get test results: {e}")
            return {"error": str(e)}
    
    def list_all_tests(self) -> List[Dict[str, Any]]:
        """List all synthetic tests."""
        if not self.enabled:
            return []
        
        try:
            response = api.Synthetics.list_tests()
            return response.get("tests", [])
        except Exception as e:
            logger.error(f"Failed to list tests: {e}")
            return []
    
    def pause_test(self, test_id: str) -> Dict[str, Any]:
        """Pause a synthetic test."""
        if not self.enabled:
            return {"error": "Synthetics integration disabled"}
        
        try:
            response = api.Synthetics.pause_test(public_id=test_id)
            logger.info(f"Paused synthetic test: {test_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to pause test: {e}")
            return {"error": str(e)}
    
    def resume_test(self, test_id: str) -> Dict[str, Any]:
        """Resume a synthetic test."""
        if not self.enabled:
            return {"error": "Synthetics integration disabled"}
        
        try:
            response = api.Synthetics.start_test(public_id=test_id)
            logger.info(f"Resumed synthetic test: {test_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to resume test: {e}")
            return {"error": str(e)}
    
    def create_monitor_from_test(self, test_id: str) -> Dict[str, Any]:
        """
        Create a monitor that triggers when synthetic test fails.
        This demonstrates deep integration between Synthetics and Monitors.
        """
        if not self.enabled:
            return {"error": "Synthetics integration disabled"}
        
        try:
            # Create monitor that watches synthetic test
            monitor_config = {
                "name": f"Synthetic Test Failure: {test_id}",
                "type": "synthetics alert",
                "query": f"synthetics.test({test_id}).over('*')",
                "message": f"🚨 **Synthetic Test Failed**\n\n**What failed?** Synthetic test {test_id} is failing.\n\n**Why did it fail?** Possible causes:\n- Service is down\n- Response time exceeded threshold\n- Network connectivity issues\n\n**What should the engineer do next?**\n1. Check synthetic test results in Datadog\n2. Review service health\n3. Check recent deployments\n4. Investigate network issues",
                "tags": ["synthetic", "llm", "critical"],
                "options": {
                    "notify_audit": True,
                    "notify_no_data": False,
                    "renotify_interval": 0,
                },
                "incident_config": {
                    "create_incident": True,
                    "incident_severity": "SEV-2",
                },
            }
            
            response = api.Monitor.create(**monitor_config)
            logger.info(f"Created monitor from synthetic test: {test_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create monitor from test: {e}")
            return {"error": str(e)}


# Global instance
_synthetics: Optional[SyntheticsIntegration] = None


def get_synthetics() -> SyntheticsIntegration:
    """Get or create global SyntheticsIntegration instance."""
    global _synthetics
    if _synthetics is None:
        _synthetics = SyntheticsIntegration()
    return _synthetics

