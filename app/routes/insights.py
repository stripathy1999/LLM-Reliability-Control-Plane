"""
AI-Powered Insights Endpoint

Provides real-time AI analysis of system health, cost optimization,
predictive alerts, and automated remediation suggestions.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Query
from pydantic import BaseModel

from ..insights import (
    generate_cost_optimization_recommendations,
    generate_predictive_insights,
    generate_quality_recommendations,
    generate_reliability_recommendations,
    generate_security_recommendations,
)
from ..telemetry import emit_gauge

router = APIRouter(prefix="/insights", tags=["insights"])


class InsightsRequest(BaseModel):
    """Request body for insights endpoint."""
    # Current metrics (would come from Datadog API in production)
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    retry_rate: float = 0.0
    avg_cost_per_request: float = 0.0
    avg_input_tokens: float = 0.0
    avg_output_tokens: float = 0.0
    avg_quality_score: float = 0.0
    ungrounded_rate: float = 0.0
    safety_block_rate: float = 0.0
    injection_risk_rate: float = 0.0
    token_abuse_rate: float = 0.0
    timeout_rate: float = 0.0
    # Trends (would be computed from historical data)
    latency_trend: str = "stable"  # "increasing", "stable", "decreasing"
    cost_trend: str = "stable"
    error_trend: str = "stable"


class InsightsResponse(BaseModel):
    """Response with AI-powered insights."""
    health_summary: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    predictive_insights: List[Dict[str, Any]]
    priority_actions: List[str]


@router.post("", response_model=InsightsResponse)
async def get_insights(
    body: InsightsRequest,
    compute_health_score: bool = Query(default=True),
) -> InsightsResponse:
    """
    Get AI-powered insights about system health, optimization opportunities,
    and predictive alerts.
    
    This endpoint analyzes current metrics and trends to provide:
    - Cost optimization recommendations
    - Reliability improvement suggestions
    - Quality enhancement strategies
    - Security recommendations
    - Predictive anomaly detection
    """
    # Generate all recommendations
    cost_recs = generate_cost_optimization_recommendations(
        avg_cost_per_request=body.avg_cost_per_request,
        avg_input_tokens=body.avg_input_tokens,
        avg_output_tokens=body.avg_output_tokens,
        cost_trend=body.cost_trend,
        token_ratio=body.avg_output_tokens / body.avg_input_tokens if body.avg_input_tokens > 0 else 0.0,
    )
    
    reliability_recs = generate_reliability_recommendations(
        error_rate=body.error_rate,
        retry_rate=body.retry_rate,
        avg_latency_ms=body.avg_latency_ms,
        timeout_rate=body.timeout_rate,
    )
    
    quality_recs = generate_quality_recommendations(
        avg_quality_score=body.avg_quality_score,
        ungrounded_rate=body.ungrounded_rate,
    )
    
    security_recs = generate_security_recommendations(
        safety_block_rate=body.safety_block_rate,
        injection_risk_rate=body.injection_risk_rate,
        token_abuse_rate=body.token_abuse_rate,
    )
    
    predictive = generate_predictive_insights(
        latency_trend=body.latency_trend,
        cost_trend=body.cost_trend,
        error_trend=body.error_trend,
    )
    
    # Combine all recommendations
    all_recommendations = cost_recs + reliability_recs + quality_recs + security_recs
    
    # Sort by priority (critical > high > medium > low)
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
    
    # Extract top 5 priority actions
    priority_actions = [
        rec["title"] for rec in all_recommendations[:5]
    ]
    
    # Compute health summary
    token_efficiency = (
        body.avg_output_tokens / body.avg_input_tokens
        if body.avg_input_tokens > 0
        else 0.0
    )
    
    # Import health score calculator
    from ..health_score import calculate_health_score
    
    health_score_data = calculate_health_score(
        latency_ms=body.avg_latency_ms,
        error_rate=body.error_rate,
        retry_rate=body.retry_rate,
        cost_per_request=body.avg_cost_per_request,
        quality_score=body.avg_quality_score,
        safety_block_rate=body.safety_block_rate,
        token_efficiency=token_efficiency,
    )
    
    # Emit health score as metric
    emit_gauge(
        "llm.health_score",
        health_score_data["health_score"],
        tags={"service": "llm-reliability-control-plane"},
    )
    
    health_summary = {
        "overall_health_score": health_score_data["health_score"],
        "component_scores": {
            "performance": health_score_data["performance_score"],
            "reliability": health_score_data["reliability_score"],
            "cost": health_score_data["cost_score"],
            "quality": health_score_data["quality_score"],
            "security": health_score_data["security_score"],
        },
        "status": (
            "healthy" if health_score_data["health_score"] >= 80
            else "degraded" if health_score_data["health_score"] >= 60
            else "critical"
        ),
    }
    
    return InsightsResponse(
        health_summary=health_summary,
        recommendations=all_recommendations,
        predictive_insights=predictive,
        priority_actions=priority_actions,
    )


@router.get("/health-score")
async def get_health_score_summary() -> Dict[str, Any]:
    """
    Quick endpoint to get current health score summary.
    In production, this would query Datadog metrics.
    """
    return {
        "message": "Health score endpoint. Use POST /insights for full analysis.",
        "note": "In production, this would query Datadog API for real-time metrics.",
    }

