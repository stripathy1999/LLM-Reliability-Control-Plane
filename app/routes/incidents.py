"""
Incident Management Routes

Provides endpoints for programmatic incident creation and management.
This demonstrates automated incident creation for the hackathon submission.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from ..incident_manager import get_incident_manager, create_incident_from_monitor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/incidents", tags=["incidents"])


class IncidentCreateRequest(BaseModel):
    """Request model for creating an incident."""
    monitor_name: str = Field(..., description="Name of the monitor that triggered")
    alert_message: str = Field(..., description="Alert message from monitor")
    runbook: str = Field(..., description="Full runbook text (What failed? Why? What next?)")
    severity: str = Field(default="SEV-2", description="Incident severity (SEV-1, SEV-2, SEV-3)")
    monitor_id: Optional[int] = Field(None, description="Optional monitor ID for linking")
    tags: Optional[List[str]] = Field(None, description="Optional tags to add to incident")


class InsightIncidentRequest(BaseModel):
    """Request model for creating incident from ML insight."""
    insight_type: str = Field(..., description="Type of insight (cost_anomaly, quality_degradation, etc.)")
    title: str = Field(..., description="Incident title")
    description: str = Field(..., description="Incident description")
    recommendations: List[str] = Field(..., description="List of recommended actions")
    severity: str = Field(default="SEV-3", description="Incident severity")
    metric: Optional[str] = Field(None, description="Related metric name")


@router.post("/create", summary="Create Incident from Monitor")
async def create_incident(request: IncidentCreateRequest) -> Dict[str, Any]:
    """
    Programmatically create a Datadog incident from a monitor alert.
    
    This endpoint demonstrates automated incident creation with full context,
    including runbooks and resource attachments.
    
    **Example:**
    ```json
    {
        "monitor_name": "LLM p95 Latency SLO Burn",
        "alert_message": "p95 latency is breaching SLO threshold (1500ms)",
        "runbook": "What failed? p95 latency exceeded 1500ms...",
        "severity": "SEV-2"
    }
    ```
    """
    try:
        manager = get_incident_manager()
        
        if not manager.enabled:
            raise HTTPException(
                status_code=503,
                detail="Incident Manager is disabled. Please configure Datadog API keys."
            )
        
        result = manager.create_incident_from_monitor(
            monitor_name=request.monitor_name,
            alert_message=request.alert_message,
            runbook=request.runbook,
            severity=request.severity,
            monitor_id=request.monitor_id,
            tags=request.tags,
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create incident: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "incident": result,
            "message": "Incident created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating incident: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.post("/create-from-insight", summary="Create Incident from ML Insight")
async def create_incident_from_insight(request: InsightIncidentRequest) -> Dict[str, Any]:
    """
    Create a Datadog incident from an ML insight or anomaly detection.
    
    This demonstrates how ML-based insights can automatically trigger incidents
    with actionable recommendations.
    
    **Example:**
    ```json
    {
        "insight_type": "cost_anomaly",
        "title": "Unusual Cost Pattern Detected",
        "description": "ML model detected anomalous cost spike pattern",
        "recommendations": [
            "Review token usage patterns",
            "Check for prompt engineering changes"
        ],
        "severity": "SEV-3",
        "metric": "llm.cost.usd"
    }
    ```
    """
    try:
        manager = get_incident_manager()
        
        if not manager.enabled:
            raise HTTPException(
                status_code=503,
                detail="Incident Manager is disabled. Please configure Datadog API keys."
            )
        
        result = manager.create_incident_from_insight(
            insight_type=request.insight_type,
            title=request.title,
            description=request.description,
            recommendations=request.recommendations,
            severity=request.severity,
            metric=request.metric,
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create incident: {result.get('error', 'Unknown error')}"
            )
        
        return {
            "success": True,
            "incident": result,
            "message": "Incident created from ML insight successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating incident from insight: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/status", summary="Get Incident Manager Status")
async def get_incident_manager_status() -> Dict[str, Any]:
    """
    Get the status of the Incident Manager.
    
    Returns whether the incident manager is enabled and configured correctly.
    """
    manager = get_incident_manager()
    
    return {
        "enabled": manager.enabled,
        "service_name": manager.service_name,
        "dashboard_name": manager.dashboard_name,
        "api_configured": bool(manager.api_key and manager.app_key),
        "message": "Incident Manager is ready" if manager.enabled else "Incident Manager is disabled (configure API keys)"
    }

