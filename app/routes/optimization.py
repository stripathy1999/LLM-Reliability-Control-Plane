"""
API Routes for Cost Optimization and ROI Tracking
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.cost_optimization_engine import (
    get_optimization_engine,
    OptimizationRecommendation
)
from app.anomaly_attribution_engine import (
    get_attribution_engine
)

router = APIRouter(prefix="/optimization", tags=["optimization"])


class CreateRecommendationRequest(BaseModel):
    title: str
    category: str
    description: str
    estimated_savings_per_request: float
    estimated_savings_percentage: float
    priority: str = "medium"
    implementation_cost: float = 0.0


class ImplementRecommendationRequest(BaseModel):
    recommendation_id: str
    baseline_metrics: Dict[str, Any]


class RecordResultRequest(BaseModel):
    recommendation_id: str
    period_days: int = 7
    before_cost: Optional[float] = None
    after_cost: Optional[float] = None
    request_count: Optional[int] = None
    confidence_score: float = 0.85


@router.post("/recommendations", response_model=Dict[str, Any])
async def create_recommendation(request: CreateRecommendationRequest):
    """
    Create a new cost optimization recommendation.
    """
    engine = get_optimization_engine()
    
    recommendation = engine.create_recommendation(
        title=request.title,
        category=request.category,
        description=request.description,
        estimated_savings_per_request=request.estimated_savings_per_request,
        estimated_savings_percentage=request.estimated_savings_percentage,
        priority=request.priority,
        implementation_cost=request.implementation_cost
    )
    
    return {
        "id": recommendation.id,
        "title": recommendation.title,
        "category": recommendation.category,
        "status": recommendation.status,
        "created_at": recommendation.created_at,
        "message": f"Recommendation created: {recommendation.title}"
    }


@router.post("/recommendations/{recommendation_id}/implement", response_model=Dict[str, Any])
async def implement_recommendation(recommendation_id: str, request: ImplementRecommendationRequest):
    """
    Mark a recommendation as implemented and record baseline metrics.
    """
    engine = get_optimization_engine()
    
    try:
        recommendation = engine.implement_recommendation(
            recommendation_id=recommendation_id,
            baseline_metrics=request.baseline_metrics
        )
        
        return {
            "id": recommendation.id,
            "status": recommendation.status,
            "implemented_at": recommendation.implemented_at,
            "message": f"Recommendation implemented: {recommendation.title}"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/recommendations/{recommendation_id}/record-result", response_model=Dict[str, Any])
async def record_optimization_result(recommendation_id: str, request: RecordResultRequest):
    """
    Record the actual results of an implemented optimization.
    Calculates ROI and actual savings.
    """
    engine = get_optimization_engine()
    
    try:
        result = engine.record_optimization_result(
            recommendation_id=recommendation_id,
            period_days=request.period_days,
            before_cost=request.before_cost,
            after_cost=request.after_cost,
            request_count=request.request_count,
            confidence_score=request.confidence_score
        )
        
        recommendation = engine.recommendations[recommendation_id]
        
        return {
            "recommendation_id": recommendation_id,
            "recommendation_title": recommendation.title,
            "period_days": request.period_days,
            "before_cost": result.before_cost,
            "after_cost": result.after_cost,
            "actual_savings": result.actual_savings,
            "roi_percentage": result.roi_percentage,
            "confidence_score": result.confidence_score,
            "message": f"This recommendation saved ${result.actual_savings:.2f} in the last {request.period_days} days"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/roi-report", response_model=Dict[str, Any])
async def get_roi_report(days: int = 7, category: Optional[str] = None):
    """
    Get ROI report showing actual savings from optimizations.
    
    Example response:
    {
        "total_savings": 1234.56,
        "top_recommendations": [
            {
                "title": "Model Switch Optimization",
                "savings": 567.89,
                "message": "This recommendation saved $567.89 in the last 7 days"
            }
        ]
    }
    """
    engine = get_optimization_engine()
    
    report = engine.get_roi_report(days=days, category=category)
    
    return report


@router.get("/recommendations", response_model=List[Dict[str, Any]])
async def get_recommendation_history():
    """
    Get all recommendations with their status and results.
    """
    engine = get_optimization_engine()
    
    history = engine.get_recommendation_history()
    
    return history


@router.get("/recommendations/{recommendation_id}", response_model=Dict[str, Any])
async def get_recommendation(recommendation_id: str):
    """
    Get details of a specific recommendation.
    """
    engine = get_optimization_engine()
    
    if recommendation_id not in engine.recommendations:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation = engine.recommendations[recommendation_id]
    results = [r for r in engine.results if r.recommendation_id == recommendation_id]
    
    return {
        "id": recommendation.id,
        "title": recommendation.title,
        "category": recommendation.category,
        "description": recommendation.description,
        "status": recommendation.status,
        "priority": recommendation.priority,
        "created_at": recommendation.created_at,
        "implemented_at": recommendation.implemented_at,
        "estimated_savings_per_request": recommendation.estimated_savings_per_request,
        "estimated_savings_percentage": recommendation.estimated_savings_percentage,
        "results": [
            {
                "period_start": r.period_start,
                "period_end": r.period_end,
                "actual_savings": r.actual_savings,
                "roi_percentage": r.roi_percentage,
                "confidence_score": r.confidence_score
            }
            for r in results
        ],
        "total_savings": sum(r.actual_savings for r in results)
    }


@router.post("/anomaly/attribute", response_model=Dict[str, Any])
async def attribute_anomaly(
    metric_name: str,
    anomaly_timestamp: Optional[str] = None,
    baseline_period_hours: int = 24,
    analysis_window_hours: int = 1
):
    """
    Analyze an anomaly and attribute it to causes with confidence scores.
    
    Example:
    POST /optimization/anomaly/attribute?metric_name=llm.cost.usd&anomaly_timestamp=2024-01-15T10:30:00
    
    Returns:
    {
        "summary": "Anomaly caused by 23% increase in token usage from /stress endpoint (Confidence: 87.5%)",
        "primary_cause": {
            "description": "Anomaly caused by 300.0% increase in endpoint '/stress'",
            "dimension": "endpoint",
            "name": "/stress",
            "change_percentage": 300.0,
            "confidence": 0.875
        },
        "contributing_factors": [...]
    }
    """
    engine = get_attribution_engine()
    
    if anomaly_timestamp:
        timestamp = datetime.fromisoformat(anomaly_timestamp.replace('Z', '+00:00'))
    else:
        timestamp = datetime.now()
    
    attribution = engine.attribute_anomaly(
        metric_name=metric_name,
        anomaly_timestamp=timestamp,
        baseline_period_hours=baseline_period_hours,
        analysis_window_hours=analysis_window_hours
    )
    
    report = engine.generate_attribution_report(attribution)
    
    return report


@router.get("/anomaly/recent", response_model=List[Dict[str, Any]])
async def get_recent_anomalies(hours: int = 24):
    """
    Get recent anomalies with attributions.
    This would typically query Datadog for recent anomalies and attribute them.
    """
    # This would integrate with Datadog to find recent anomalies
    # For now, return a placeholder
    return [
        {
            "message": "Use /optimization/anomaly/attribute endpoint to attribute specific anomalies",
            "example": "POST /optimization/anomaly/attribute?metric_name=llm.cost.usd"
        }
    ]

