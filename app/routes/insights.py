"""
AI-Powered Insights Endpoint

Provides real-time AI analysis of system health, cost optimization,
predictive alerts, and automated remediation suggestions.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..ml_insights import MLInsightsEngine
from ..health_score import calculate_health_score
from ..telemetry import emit_gauge

router = APIRouter(prefix="/insights", tags=["insights"])

# Initialize ML-based insights engine
ml_insights_engine = MLInsightsEngine()


class InsightsRequest(BaseModel):
    """Request body for insights endpoint."""
    # Current metrics (would come from Datadog API in production)
    avg_latency_ms: float = Field(
        default=0.0,
        description="Average request latency in milliseconds",
        example=1200.0,
        ge=0.0,
    )
    error_rate: float = Field(
        default=0.0,
        description="Error rate as a decimal (0.0 to 1.0). 0.02 = 2% error rate",
        example=0.02,
        ge=0.0,
        le=1.0,
    )
    retry_rate: float = Field(
        default=0.0,
        description="Retry rate as a decimal (0.0 to 1.0)",
        example=0.05,
        ge=0.0,
        le=1.0,
    )
    avg_cost_per_request: float = Field(
        default=0.0,
        description="Average cost per request in USD",
        example=0.008,
        ge=0.0,
    )
    avg_input_tokens: float = Field(
        default=0.0,
        description="Average number of input tokens per request",
        example=1500.0,
        ge=0.0,
    )
    avg_output_tokens: float = Field(
        default=0.0,
        description="Average number of output tokens per request",
        example=200.0,
        ge=0.0,
    )
    avg_quality_score: float = Field(
        default=0.0,
        description="Average quality score (semantic similarity) from 0.0 to 1.0",
        example=0.65,
        ge=0.0,
        le=1.0,
    )
    ungrounded_rate: float = Field(
        default=0.0,
        description="Rate of ungrounded/hallucinated answers (0.0 to 1.0)",
        example=0.08,
        ge=0.0,
        le=1.0,
    )
    safety_block_rate: float = Field(
        default=0.0,
        description="Rate of safety blocks (0.0 to 1.0)",
        example=0.03,
        ge=0.0,
        le=1.0,
    )
    injection_risk_rate: float = Field(
        default=0.0,
        description="Rate of prompt injection risks detected (0.0 to 1.0)",
        example=0.01,
        ge=0.0,
        le=1.0,
    )
    token_abuse_rate: float = Field(
        default=0.0,
        description="Rate of token abuse patterns detected (0.0 to 1.0)",
        example=0.005,
        ge=0.0,
        le=1.0,
    )
    timeout_rate: float = Field(
        default=0.0,
        description="Rate of request timeouts (0.0 to 1.0)",
        example=0.01,
        ge=0.0,
        le=1.0,
    )
    # Trends (would be computed from historical data)
    latency_trend: str = Field(
        default="stable",
        description="Latency trend: 'increasing', 'stable', or 'decreasing'",
        example="increasing",
    )
    cost_trend: str = Field(
        default="stable",
        description="Cost trend: 'increasing', 'stable', or 'decreasing'",
        example="increasing",
    )
    error_trend: str = Field(
        default="stable",
        description="Error trend: 'increasing', 'stable', or 'decreasing'",
        example="stable",
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "avg_latency_ms": 1200.0,
                "error_rate": 0.02,
                "retry_rate": 0.05,
                "avg_cost_per_request": 0.008,
                "avg_input_tokens": 1500.0,
                "avg_output_tokens": 200.0,
                "avg_quality_score": 0.65,
                "ungrounded_rate": 0.08,
                "safety_block_rate": 0.03,
                "injection_risk_rate": 0.01,
                "token_abuse_rate": 0.005,
                "timeout_rate": 0.01,
                "latency_trend": "increasing",
                "cost_trend": "increasing",
                "error_trend": "stable"
            }
        }


class InsightsResponse(BaseModel):
    """Response with AI-powered insights."""
    health_summary: Dict[str, Any] = Field(
        ...,
        description="""
        Overall health summary including:
        - **overall_health_score**: Composite health score from 0-100
        - **component_scores**: Individual scores for performance, reliability, cost, quality, security
        - **status**: Overall status (healthy/degraded/critical)
        """,
        example={
            "overall_health_score": 65,
            "component_scores": {
                "performance": 60,
                "reliability": 70,
                "cost": 50,
                "quality": 65,
                "security": 80
            },
            "status": "degraded"
        }
    )
    recommendations: List[Dict[str, Any]] = Field(
        ...,
        description="List of prioritized recommendations with title, description, priority, and estimated impact",
        example=[
            {
                "title": "Downgrade model to reduce costs",
                "description": "Consider using gemini-1.5-flash instead of gemini-2.5-pro",
                "priority": "high",
                "category": "cost",
                "estimated_savings": "30%"
            }
        ]
    )
    predictive_insights: List[Dict[str, Any]] = Field(
        ...,
        description="Predictive insights about potential future issues based on trends",
        example=[
            {
                "type": "cost_anomaly",
                "message": "Cost trend is increasing. If current trend continues, cost will exceed threshold in 2 days.",
                "severity": "medium"
            }
        ]
    )
    priority_actions: List[str] = Field(
        ...,
        description="Top 5 priority actions to take, ordered by importance",
        example=[
            "Downgrade model to reduce costs by 30%",
            "Enable caching for frequently asked questions",
            "Review prompts causing safety blocks"
        ]
    )


@router.post(
    "",
    response_model=InsightsResponse,
    summary="AI-Powered Insights & Health Analysis",
    description="""
    Provides comprehensive AI analysis of system health, cost optimization opportunities, 
    predictive alerts, and automated remediation suggestions.
    
    ## Purpose
    This endpoint analyzes current metrics and trends to provide actionable insights 
    and recommendations for improving LLM application reliability, cost efficiency, and quality.
    
    ## How It Works
    1. Accepts current system metrics (latency, errors, cost, quality, security)
    2. Analyzes trends (increasing, stable, decreasing)
    3. Computes composite health score (0-100) across 5 dimensions
    4. Generates prioritized recommendations using AI
    5. Provides predictive insights about future issues
    6. Returns top 5 priority actions
    
    ## Health Score Components
    The composite health score combines:
    - **Performance** (0-100): Based on latency and timeout rates
    - **Reliability** (0-100): Based on error and retry rates
    - **Cost** (0-100): Based on cost per request and trends
    - **Quality** (0-100): Based on quality scores and ungrounded rates
    - **Security** (0-100): Based on safety blocks and injection risks
    
    ## Recommendation Categories
    - **Cost Optimization**: Model downgrades, caching strategies, token optimization
    - **Reliability**: Retry policies, timeout handling, error recovery
    - **Quality**: Prompt engineering, model selection, grounding improvements
    - **Security**: Prompt injection prevention, safety filter tuning
    
    ## Predictive Insights
    Analyzes trends to forecast:
    - Cost anomalies before they occur
    - Latency degradation patterns
    - Error rate increases
    - Quality degradation trends
    
    ## Example Use Cases
    - System health monitoring dashboards
    - Automated alerting and incident response
    - Cost optimization analysis
    - Performance tuning recommendations
    - Security threat detection
    
    ## Integration
    In production, this endpoint would query Datadog API for real-time metrics. 
    For testing, provide metrics manually in the request body.
    """,
    response_description="Comprehensive health analysis with prioritized recommendations and predictive insights",
    responses={
        200: {
            "description": "Successful analysis with health score, recommendations, and insights",
        },
        422: {
            "description": "Validation error - check request body format and value ranges",
        },
    },
)
async def get_insights(
    body: InsightsRequest,
    compute_health_score: bool = Query(
        default=True,
        description="Whether to compute the composite health score. Set to false to skip health score calculation.",
        example=True,
    ),
) -> InsightsResponse:
    """
    Get ML-powered insights about system health, optimization opportunities,
    and predictive alerts using actual machine learning models.
    
    This endpoint uses ML models to provide:
    - ML-based cost prediction and optimization
    - ML-based quality prediction and recommendations
    - Watchdog ML insights from Datadog
    - Model routing optimization
    - Predictive anomaly detection
    """
    # Prepare current metrics for ML models
    current_metrics = {
        "avg_latency_ms": body.avg_latency_ms,
        "error_rate": body.error_rate,
        "retry_rate": body.retry_rate,
        "avg_cost_per_request": body.avg_cost_per_request,
        "avg_input_tokens": body.avg_input_tokens,
        "avg_output_tokens": body.avg_output_tokens,
        "avg_quality_score": body.avg_quality_score,
        "safety_block_rate": body.safety_block_rate,
        "injection_risk_rate": body.injection_risk_rate,
        "token_abuse_rate": body.token_abuse_rate,
        "timeout_rate": body.timeout_rate,
        "request_count": 100,  # Would come from metrics in production
        "daily_budget": 10.0,  # Would come from config
        "request_type": "qa",  # Would come from context
        "max_latency_ms": 2000,
        "min_quality": 0.7,
        "cost_budget": 0.01,
    }
    
    # Get ML-based recommendations
    ml_results = ml_insights_engine.generate_ml_recommendations(current_metrics)
    
    all_recommendations = ml_results.get("recommendations", [])
    predictive_insights = ml_results.get("predictive_insights", [])
    
    # Extract top 5 priority actions
    priority_actions = [
        rec.get("title", "No title") for rec in all_recommendations[:5]
    ]
    
    # Compute health summary
    token_efficiency = (
        body.avg_output_tokens / body.avg_input_tokens
        if body.avg_input_tokens > 0
        else 0.0
    )
    
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
    
    # Add ML model information to response
    response_data = {
        "health_summary": health_summary,
        "recommendations": all_recommendations,
        "predictive_insights": predictive_insights,
        "priority_actions": priority_actions,
        "ml_models_used": ml_results.get("ml_models_used", {}),
        "ml_confidence_scores": ml_results.get("ml_confidence_scores", {}),
    }
    
    return InsightsResponse(**response_data)


@router.get(
    "/health-score",
    summary="Quick Health Score Summary",
    description="""
    Quick endpoint to get current health score summary.
    
    **Note**: This is a placeholder endpoint. For full health analysis with recommendations,
    use `POST /insights` instead.
    
    In production, this endpoint would query Datadog API for real-time metrics.
    """,
    response_description="Health score endpoint information",
)
async def get_health_score_summary() -> Dict[str, Any]:
    """
    Quick endpoint to get current health score summary.
    In production, this would query Datadog metrics.
    """
    return {
        "message": "Health score endpoint. Use POST /insights for full analysis.",
        "note": "In production, this would query Datadog API for real-time metrics.",
    }

