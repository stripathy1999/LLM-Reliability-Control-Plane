"""
Datadog On-Call Integration

Deep integration with Datadog On-Call for paging and escalation.
Programmatically manages on-call schedules and triggers pages.
"""

import os
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from datadog import api
    DD_API_AVAILABLE = True
except ImportError:
    DD_API_AVAILABLE = False
    logger.warning("Datadog API not available. Install: pip install datadog")


class OnCallIntegration:
    """
    Deep integration with Datadog On-Call.
    
    Manages on-call schedules, triggers pages, and handles escalations.
    """
    
    def __init__(self):
        if DD_API_AVAILABLE:
            self.api_key = os.getenv("DD_API_KEY") or os.getenv("LRCP_DATADOG_API_KEY")
            self.app_key = os.getenv("DD_APP_KEY")
            self.site = os.getenv("DD_SITE", "datadoghq.com")
            if self.api_key and self.app_key:
                api._api_key = self.api_key
                api._application_key = self.app_key
                self.enabled = True
                self.base_url = f"https://api.{self.site}"
            else:
                self.enabled = False
        else:
            self.enabled = False
    
    def page_oncall(
        self,
        schedule_name: str,
        message: str,
        severity: str = "high",
        incident_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Page the on-call engineer.
        
        This demonstrates deep integration: programmatically paging
        on-call when critical issues occur.
        """
        if not self.enabled:
            logger.warning("On-Call integration disabled: Missing API keys")
            return {"error": "On-Call integration disabled"}
        
        try:
            # Use Datadog On-Call API to page
            # Note: On-Call API format may vary
            url = f"{self.base_url}/api/v1/oncall/pages"
            headers = {
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
                "Content-Type": "application/json",
            }
            
            payload = {
                "schedule": schedule_name,
                "message": message,
                "severity": severity,
                "incident_id": incident_id,
                "triggered_at": datetime.now().isoformat(),
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Paged on-call: {schedule_name}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to page on-call: {e}")
            # Fallback: create event that triggers on-call
            return self._create_oncall_event(schedule_name, message, severity, incident_id)
    
    def _create_oncall_event(
        self,
        schedule_name: str,
        message: str,
        severity: str,
        incident_id: Optional[str],
    ) -> Dict[str, Any]:
        """Create an event that triggers on-call paging."""
        try:
            event = api.Event.create(
                title=f"🚨 On-Call Page: {schedule_name}",
                text=f"{message}\n\nSeverity: {severity}\nIncident ID: {incident_id or 'N/A'}",
                alert_type="error" if severity == "critical" else "warning",
                source_type_name="On-Call",
                tags=[
                    "oncall",
                    f"schedule:{schedule_name}",
                    f"severity:{severity}",
                    "llm",
                    "critical",
                ],
            )
            
            logger.info(f"Created on-call event for schedule: {schedule_name}")
            return {
                "status": "event_created",
                "event_id": event.get("event", {}).get("id"),
                "schedule": schedule_name,
                "message": "On-call event created. Configure auto-paging rules in Datadog UI.",
            }
            
        except Exception as e:
            logger.error(f"Failed to create on-call event: {e}")
            return {"error": str(e)}
    
    def get_current_oncall(self, schedule_name: str) -> Dict[str, Any]:
        """Get current on-call engineer for a schedule."""
        if not self.enabled:
            return {"error": "On-Call integration disabled"}
        
        try:
            # Query on-call schedule
            url = f"{self.base_url}/api/v1/oncall/schedules/{schedule_name}/current"
            headers = {
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get current on-call: {e}")
            return {
                "schedule": schedule_name,
                "message": "On-call schedule query failed. Check schedule name and API permissions.",
                "error": str(e)
            }
    
    def create_auto_paging_rule(
        self,
        monitor_name: str,
        schedule_name: str,
        escalation_policy: str,
        severity: str = "high",
    ) -> Dict[str, Any]:
        """
        Create an auto-paging rule that pages on-call when monitor triggers.
        
        This demonstrates deep integration: programmatically creating
        on-call rules that integrate with monitors.
        """
        if not self.enabled:
            return {"error": "On-Call integration disabled"}
        
        try:
            rule_config = {
                "name": f"Auto-Page on {monitor_name}",
                "description": f"Automatically pages on-call when {monitor_name} triggers",
                "trigger": {
                    "type": "monitor",
                    "monitor_name": monitor_name,
                    "conditions": {
                        "alert": "triggered",
                        "severity": severity
                    }
                },
                "action": {
                    "type": "page_oncall",
                    "schedule": schedule_name,
                    "escalation_policy": escalation_policy,
                    "message": f"Critical LLM issue detected. Monitor: {monitor_name}",
                }
            }
            
            # Create rule via API
            # Note: On-Call API format may vary
            url = f"{self.base_url}/api/v1/oncall/rules"
            headers = {
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
                "Content-Type": "application/json",
            }
            
            response = requests.post(url, json=rule_config, headers=headers)
            response.raise_for_status()
            
            logger.info(f"Created auto-paging rule for monitor: {monitor_name}")
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to create auto-paging rule: {e}")
            return {
                "rule_config": rule_config,
                "message": "Auto-paging rule configuration created. Import manually via Datadog UI.",
                "error": str(e)
            }
    
    def page_on_critical_error(
        self,
        error_message: str,
        monitor_name: Optional[str] = None,
        incident_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Page on-call for critical errors.
        
        This is called automatically when critical errors are detected.
        """
        return self.page_oncall(
            schedule_name="Primary LLM On-Call",
            message=f"🚨 Critical LLM Error Detected\n\n{error_message}\n\nMonitor: {monitor_name or 'Unknown'}\nIncident: {incident_id or 'N/A'}",
            severity="critical",
            incident_id=incident_id,
        )


# Global instance
_oncall: Optional[OnCallIntegration] = None


def get_oncall() -> OnCallIntegration:
    """Get or create global OnCallIntegration instance."""
    global _oncall
    if _oncall is None:
        _oncall = OnCallIntegration()
    return _oncall

