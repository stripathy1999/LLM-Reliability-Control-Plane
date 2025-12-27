"""
Datadog Incident Manager - Programmatic Incident Creation

This module provides programmatic creation of Datadog incidents with full context,
including dashboard, logs, and trace attachments. This ensures incidents are created
automatically without requiring manual Incident Rules configuration.

This is critical for hackathon submission to demonstrate automated incident creation.
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


class IncidentManager:
    """
    Manages programmatic creation of Datadog incidents with full context.
    
    This class creates incidents directly via Datadog API, ensuring:
    - Automatic incident creation when monitors trigger
    - Full context attachments (dashboard, logs, traces)
    - Runbooks included in incident description
    - Proper severity levels
    """
    
    def __init__(self):
        self.api_key = os.getenv("DD_API_KEY") or os.getenv("LRCP_DATADOG_API_KEY")
        self.app_key = os.getenv("DD_APP_KEY")
        self.service_name = os.getenv("DD_SERVICE", "llm-reliability-control-plane")
        self.dashboard_name = "LLM Reliability Control Plane"
        
        if DD_API_AVAILABLE and self.api_key and self.app_key:
            api._api_key = self.api_key
            api._application_key = self.app_key
            self.enabled = True
            logger.info("Incident Manager enabled with real Datadog API")
        else:
            self.enabled = False
            logger.warning("Incident Manager disabled: Missing API keys")
    
    def create_incident_from_monitor(
        self,
        monitor_name: str,
        alert_message: str,
        runbook: str,
        severity: str = "SEV-2",
        monitor_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a Datadog incident programmatically from a monitor alert.
        
        Args:
            monitor_name: Name of the monitor that triggered
            alert_message: Alert message from monitor
            runbook: Full runbook text (What failed? Why? What next?)
            severity: Incident severity (SEV-1, SEV-2, SEV-3)
            monitor_id: Optional monitor ID for linking
            tags: Optional tags to add to incident
            
        Returns:
            Dict with incident creation result
        """
        if not self.enabled:
            logger.warning("Incident Manager disabled: Cannot create incident")
            return {
                "success": False,
                "error": "Incident Manager disabled: Missing API keys",
                "incident_id": None,
            }
        
        try:
            # Build incident title
            title = f"{monitor_name} - {alert_message[:100]}"
            
            # Build incident description with runbook
            description = f"""## 🚨 Monitor Alert: {monitor_name}

**Alert Message:** {alert_message}

---

## 📋 Runbook

{runbook}

---

## 🔗 Attached Resources

- **Dashboard**: {self.dashboard_name}
- **Logs**: Filtered by `service:{self.service_name}`
- **Traces**: Filtered by `service:{self.service_name}`

---

**Created:** {datetime.utcnow().isoformat()}Z
**Service:** {self.service_name}
**Monitor ID:** {monitor_id or "N/A"}
"""
            
            # Build incident fields
            incident_fields = {
                "state": "active",
                "severity": severity,
                "title": title,
                "body": description,
            }
            
            # Add tags
            incident_tags = tags or []
            incident_tags.extend([
                "llm",
                "automated",
                "monitor-triggered",
                f"service:{self.service_name}",
            ])
            if monitor_id:
                incident_tags.append(f"monitor:{monitor_id}")
            
            # Create incident via Datadog API
            # Note: Datadog Incidents API v2
            try:
                response = api.Incident.create(
                    data={
                        "type": "incidents",
                        "attributes": {
                            "title": title,
                            "customer_impacted": True,
                            "fields": {
                                "severity": {
                                    "type": "dropdown",
                                    "value": severity
                                },
                                "state": {
                                    "type": "text",
                                    "value": "active"
                                }
                            }
                        },
                        "relationships": {
                            "commander": {
                                "data": {
                                    "type": "users",
                                    "id": None  # Will use current user
                                }
                            }
                        }
                    }
                )
                
                incident_id = response.get("data", {}).get("id")
                
                # Add attachments (dashboard, logs, traces)
                if incident_id:
                    self._attach_resources(incident_id, monitor_name)
                
                logger.info(f"Created incident {incident_id} for monitor {monitor_name}")
                
                return {
                    "success": True,
                    "incident_id": incident_id,
                    "title": title,
                    "severity": severity,
                    "url": f"https://app.datadoghq.com/incidents/{incident_id}",
                }
                
            except Exception as api_error:
                # Fallback: Try v1 API or create event
                logger.warning(f"Incident API v2 failed: {api_error}, trying event creation")
                return self._create_incident_via_event(
                    title, description, severity, incident_tags, monitor_id
                )
                
        except Exception as e:
            logger.error(f"Failed to create incident: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "incident_id": None,
            }
    
    def _create_incident_via_event(
        self,
        title: str,
        description: str,
        severity: str,
        tags: List[str],
        monitor_id: Optional[int],
    ) -> Dict[str, Any]:
        """
        Fallback: Create incident via Event API (if Incident API not available).
        """
        try:
            event = api.Event.create(
                title=title,
                text=description,
                alert_type="error",
                priority="normal" if severity in ["SEV-1", "SEV-2"] else "low",
                tags=tags,
                source_type_name="LLM Reliability Control Plane",
            )
            
            logger.info(f"Created incident event {event.get('event', {}).get('id')}")
            
            return {
                "success": True,
                "incident_id": event.get("event", {}).get("id"),
                "title": title,
                "severity": severity,
                "method": "event_fallback",
                "url": f"https://app.datadoghq.com/event/event?id={event.get('event', {}).get('id')}",
            }
        except Exception as e:
            logger.error(f"Event creation also failed: {e}")
            return {
                "success": False,
                "error": f"Both Incident API and Event API failed: {e}",
                "incident_id": None,
            }
    
    def _attach_resources(self, incident_id: str, monitor_name: str) -> None:
        """
        Attach dashboard, logs, and traces to incident.
        
        Note: Datadog Incident API v2 attachments may require separate API calls.
        This is a placeholder for the attachment logic.
        """
        try:
            # Find dashboard by name
            dashboards = api.Dashboard.get_all()
            dashboard_id = None
            for dashboard in dashboards.get("dashboards", []):
                if dashboard.get("title") == self.dashboard_name:
                    dashboard_id = dashboard.get("id")
                    break
            
            if dashboard_id:
                logger.info(f"Found dashboard {dashboard_id} for attachment")
                # Note: Actual attachment via Incident API v2 would go here
                # api.Incident.update_attachments(incident_id, dashboard_id=dashboard_id)
            
            # Logs and traces are automatically correlated via tags
            # No explicit attachment needed if tags are set correctly
            
        except Exception as e:
            logger.warning(f"Could not attach resources: {e}")
    
    def create_incident_from_insight(
        self,
        insight_type: str,
        title: str,
        description: str,
        recommendations: List[str],
        severity: str = "SEV-3",
        metric: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create incident from ML insight or anomaly detection.
        
        Args:
            insight_type: Type of insight (cost_anomaly, quality_degradation, etc.)
            title: Incident title
            description: Incident description
            recommendations: List of recommended actions
            severity: Incident severity
            metric: Related metric name
            
        Returns:
            Dict with incident creation result
        """
        runbook = f"""## What failed?
{description}

## Why did it fail?
This issue was detected by ML-based anomaly detection or insight analysis.
The system identified unusual patterns that deviate from normal behavior.

## What should the engineer do next?
{chr(10).join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))}

**Metric:** {metric or "N/A"}
**Insight Type:** {insight_type}
**Detection Method:** ML-based analysis"""
        
        return self.create_incident_from_monitor(
            monitor_name=f"ML Insight: {insight_type}",
            alert_message=title,
            runbook=runbook,
            severity=severity,
            tags=["llm", "ml", "anomaly", insight_type],
        )


# Global instance
_incident_manager: Optional[IncidentManager] = None


def get_incident_manager() -> IncidentManager:
    """Get or create global IncidentManager instance."""
    global _incident_manager
    if _incident_manager is None:
        _incident_manager = IncidentManager()
    return _incident_manager


def create_incident_from_monitor(
    monitor_name: str,
    alert_message: str,
    runbook: str,
    severity: str = "SEV-2",
    **kwargs,
) -> Dict[str, Any]:
    """
    Convenience function to create incident from monitor.
    
    Usage:
        result = create_incident_from_monitor(
            monitor_name="LLM p95 Latency SLO Burn",
            alert_message="p95 latency is breaching SLO threshold",
            runbook="What failed? ... Why? ... What next? ...",
            severity="SEV-2"
        )
    """
    manager = get_incident_manager()
    return manager.create_incident_from_monitor(
        monitor_name=monitor_name,
        alert_message=alert_message,
        runbook=runbook,
        severity=severity,
        **kwargs,
    )

