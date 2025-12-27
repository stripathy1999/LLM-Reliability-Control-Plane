"""
LLM Cost Optimization Engine with ROI Calculator

Tracks savings from recommendations over time and calculates actual ROI.
Shows: "This recommendation saved $1,234 in the last 7 days"
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from datadog import api, statsd
    DD_API_AVAILABLE = True
except ImportError:
    DD_API_AVAILABLE = False
    logger.warning("Datadog API not available. Install: pip install datadog")


@dataclass
class OptimizationRecommendation:
    """Represents a cost optimization recommendation."""
    id: str
    title: str
    category: str  # "model_switch", "caching", "prompt_optimization", "routing", etc.
    description: str
    estimated_savings_per_request: float
    estimated_savings_percentage: float
    priority: str  # "high", "medium", "low"
    created_at: str
    implemented_at: Optional[str] = None
    status: str = "pending"  # "pending", "implemented", "rejected", "expired"
    implementation_cost: float = 0.0  # Cost to implement (e.g., dev time)


@dataclass
class OptimizationResult:
    """Tracks the actual results of an implemented optimization."""
    recommendation_id: str
    period_start: str
    period_end: str
    before_cost: float
    after_cost: float
    actual_savings: float
    request_count: int
    roi_percentage: float
    confidence_score: float  # How confident we are in the attribution


class CostOptimizationEngine:
    """
    Tracks cost optimization recommendations and calculates ROI.
    
    Features:
    - Track recommendation history
    - Calculate before/after costs
    - Generate ROI reports
    - Show actual savings over time periods
    """
    
    def __init__(self, storage_path: str = "data/optimization_history.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize Datadog if available
        if DD_API_AVAILABLE:
            self.api_key = os.getenv("DD_API_KEY") or os.getenv("LRCP_DATADOG_API_KEY")
            self.app_key = os.getenv("DD_APP_KEY")
            if self.api_key and self.app_key:
                api._api_key = self.api_key
                api._application_key = self.app_key
                self.datadog_enabled = True
            else:
                self.datadog_enabled = False
        else:
            self.datadog_enabled = False
        
        # Load existing history
        self.recommendations: Dict[str, OptimizationRecommendation] = {}
        self.results: List[OptimizationResult] = []
        self._load_history()
    
    def _load_history(self):
        """Load optimization history from storage."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    # Load recommendations
                    for rec_data in data.get('recommendations', []):
                        rec = OptimizationRecommendation(**rec_data)
                        self.recommendations[rec.id] = rec
                    # Load results
                    for result_data in data.get('results', []):
                        result = OptimizationResult(**result_data)
                        self.results.append(result)
                logger.info(f"Loaded {len(self.recommendations)} recommendations and {len(self.results)} results")
        except Exception as e:
            logger.warning(f"Could not load optimization history: {e}")
    
    def _save_history(self):
        """Save optimization history to storage."""
        try:
            data = {
                'recommendations': [asdict(rec) for rec in self.recommendations.values()],
                'results': [asdict(result) for result in self.results],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save optimization history: {e}")
    
    def create_recommendation(
        self,
        title: str,
        category: str,
        description: str,
        estimated_savings_per_request: float,
        estimated_savings_percentage: float,
        priority: str = "medium",
        implementation_cost: float = 0.0
    ) -> OptimizationRecommendation:
        """
        Create a new cost optimization recommendation.
        
        Returns:
            OptimizationRecommendation with generated ID
        """
        rec_id = f"opt-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{len(self.recommendations)}"
        
        recommendation = OptimizationRecommendation(
            id=rec_id,
            title=title,
            category=category,
            description=description,
            estimated_savings_per_request=estimated_savings_per_request,
            estimated_savings_percentage=estimated_savings_percentage,
            priority=priority,
            created_at=datetime.now().isoformat(),
            implementation_cost=implementation_cost
        )
        
        self.recommendations[rec_id] = recommendation
        self._save_history()
        
        # Emit metric to Datadog
        if self.datadog_enabled:
            try:
                statsd.gauge(
                    'llm.optimization.recommendation.created',
                    1,
                    tags=[f'category:{category}', f'priority:{priority}']
                )
            except Exception as e:
                logger.warning(f"Could not emit Datadog metric: {e}")
        
        logger.info(f"Created optimization recommendation: {rec_id} - {title}")
        return recommendation
    
    def implement_recommendation(
        self,
        recommendation_id: str,
        baseline_metrics: Dict[str, Any]
    ) -> OptimizationRecommendation:
        """
        Mark a recommendation as implemented and record baseline metrics.
        
        Args:
            recommendation_id: ID of the recommendation to implement
            baseline_metrics: Metrics before implementation (for comparison)
                - cost_per_request: float
                - avg_input_tokens: float
                - avg_output_tokens: float
                - request_count: int
                - period_start: str (ISO format)
        """
        if recommendation_id not in self.recommendations:
            raise ValueError(f"Recommendation {recommendation_id} not found")
        
        recommendation = self.recommendations[recommendation_id]
        recommendation.status = "implemented"
        recommendation.implemented_at = datetime.now().isoformat()
        
        # Store baseline metrics for later comparison
        recommendation.baseline_metrics = baseline_metrics
        
        self._save_history()
        
        # Emit metric to Datadog
        if self.datadog_enabled:
            try:
                statsd.gauge(
                    'llm.optimization.recommendation.implemented',
                    1,
                    tags=[f'category:{recommendation.category}', f'id:{recommendation_id}']
                )
            except Exception as e:
                logger.warning(f"Could not emit Datadog metric: {e}")
        
        logger.info(f"Implemented optimization recommendation: {recommendation_id}")
        return recommendation
    
    def record_optimization_result(
        self,
        recommendation_id: str,
        period_days: int = 7,
        before_cost: Optional[float] = None,
        after_cost: Optional[float] = None,
        request_count: Optional[int] = None,
        confidence_score: float = 0.85
    ) -> OptimizationResult:
        """
        Record the actual results of an implemented optimization.
        
        This calculates:
        - Actual savings (before_cost - after_cost)
        - ROI percentage
        - Confidence in the attribution
        
        Args:
            recommendation_id: ID of the implemented recommendation
            period_days: Number of days in the measurement period
            before_cost: Total cost before optimization (if not provided, calculated from baseline)
            after_cost: Total cost after optimization (if not provided, fetched from Datadog)
            request_count: Number of requests in the period
            confidence_score: Confidence that savings are due to this optimization (0-1)
        """
        if recommendation_id not in self.recommendations:
            raise ValueError(f"Recommendation {recommendation_id} not found")
        
        recommendation = self.recommendations[recommendation_id]
        
        if recommendation.status != "implemented":
            raise ValueError(f"Recommendation {recommendation_id} is not implemented")
        
        # Calculate period
        period_end = datetime.now()
        period_start = period_end - timedelta(days=period_days)
        
        # If costs not provided, try to fetch from Datadog or calculate
        if before_cost is None:
            baseline = getattr(recommendation, 'baseline_metrics', {})
            baseline_cost_per_request = baseline.get('cost_per_request', 0)
            if request_count:
                before_cost = baseline_cost_per_request * request_count
            else:
                # Fetch from Datadog
                before_cost = self._fetch_cost_from_datadog(period_start, period_end, before_optimization=True)
        
        if after_cost is None:
            after_cost = self._fetch_cost_from_datadog(period_start, period_end, before_optimization=False)
        
        if request_count is None:
            request_count = self._fetch_request_count_from_datadog(period_start, period_end)
        
        # Calculate actual savings
        actual_savings = before_cost - after_cost
        
        # Calculate ROI
        implementation_cost = recommendation.implementation_cost
        if implementation_cost > 0:
            roi_percentage = ((actual_savings - implementation_cost) / implementation_cost) * 100
        else:
            roi_percentage = float('inf') if actual_savings > 0 else 0.0
        
        # Create result
        result = OptimizationResult(
            recommendation_id=recommendation_id,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            before_cost=before_cost,
            after_cost=after_cost,
            actual_savings=actual_savings,
            request_count=request_count,
            roi_percentage=roi_percentage,
            confidence_score=confidence_score
        )
        
        self.results.append(result)
        self._save_history()
        
        # Emit metrics to Datadog
        if self.datadog_enabled:
            try:
                statsd.gauge('llm.optimization.savings.total', actual_savings, tags=[f'recommendation_id:{recommendation_id}'])
                statsd.gauge('llm.optimization.roi.percentage', roi_percentage, tags=[f'recommendation_id:{recommendation_id}'])
                statsd.gauge('llm.optimization.savings.confidence', confidence_score, tags=[f'recommendation_id:{recommendation_id}'])
            except Exception as e:
                logger.warning(f"Could not emit Datadog metrics: {e}")
        
        logger.info(f"Recorded optimization result: {recommendation_id} - Saved ${actual_savings:.2f} ({roi_percentage:.1f}% ROI)")
        return result
    
    def _fetch_cost_from_datadog(
        self,
        start_time: datetime,
        end_time: datetime,
        before_optimization: bool = False
    ) -> float:
        """Fetch total cost from Datadog for a time period."""
        if not self.datadog_enabled:
            return 0.0
        
        try:
            # Query Datadog for cost metrics
            query = f"sum:llm.cost.usd{{service:llm-reliability-control-plane}}"
            
            # Use Datadog API to query metrics
            response = api.Metric.query(
                start=int(start_time.timestamp()),
                end=int(end_time.timestamp()),
                query=query
            )
            
            # Sum up all cost values
            total_cost = 0.0
            if 'series' in response:
                for series in response['series']:
                    if 'pointlist' in series:
                        for point in series['pointlist']:
                            if point[1] is not None:
                                total_cost += point[1]
            
            return total_cost
        except Exception as e:
            logger.warning(f"Could not fetch cost from Datadog: {e}")
            return 0.0
    
    def _fetch_request_count_from_datadog(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> int:
        """Fetch request count from Datadog for a time period."""
        if not self.datadog_enabled:
            return 0
        
        try:
            query = f"sum:llm.request.count{{service:llm-reliability-control-plane}}"
            
            response = api.Metric.query(
                start=int(start_time.timestamp()),
                end=int(end_time.timestamp()),
                query=query
            )
            
            total_count = 0
            if 'series' in response:
                for series in response['series']:
                    if 'pointlist' in series:
                        for point in series['pointlist']:
                            if point[1] is not None:
                                total_count += int(point[1])
            
            return total_count
        except Exception as e:
            logger.warning(f"Could not fetch request count from Datadog: {e}")
            return 0
    
    def get_roi_report(
        self,
        days: int = 7,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate ROI report showing actual savings from optimizations.
        
        Returns:
            Report with:
            - Total savings
            - Savings by category
            - Top performing recommendations
            - ROI breakdown
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter results by date and category
        relevant_results = [
            r for r in self.results
            if datetime.fromisoformat(r.period_end) >= cutoff_date
            and (category is None or self.recommendations[r.recommendation_id].category == category)
        ]
        
        if not relevant_results:
            return {
                "period_days": days,
                "total_savings": 0.0,
                "total_requests": 0,
                "recommendations_count": 0,
                "top_recommendations": [],
                "savings_by_category": {},
                "average_roi": 0.0,
                "message": f"No optimization results found in the last {days} days"
            }
        
        # Calculate totals
        total_savings = sum(r.actual_savings for r in relevant_results)
        total_requests = sum(r.request_count for r in relevant_results)
        
        # Group by category
        savings_by_category: Dict[str, float] = {}
        for result in relevant_results:
            rec = self.recommendations[result.recommendation_id]
            category_name = rec.category
            savings_by_category[category_name] = savings_by_category.get(category_name, 0) + result.actual_savings
        
        # Top performing recommendations
        top_recommendations = sorted(
            relevant_results,
            key=lambda x: x.actual_savings,
            reverse=True
        )[:5]
        
        top_recommendations_list = []
        for result in top_recommendations:
            rec = self.recommendations[result.recommendation_id]
            top_recommendations_list.append({
                "id": result.recommendation_id,
                "title": rec.title,
                "category": rec.category,
                "savings": result.actual_savings,
                "roi_percentage": result.roi_percentage,
                "period_days": (datetime.fromisoformat(result.period_end) - datetime.fromisoformat(result.period_start)).days,
                "confidence": result.confidence_score,
                "message": f"This recommendation saved ${result.actual_savings:.2f} in the last {days} days"
            })
        
        # Average ROI
        rois = [r.roi_percentage for r in relevant_results if r.roi_percentage != float('inf')]
        average_roi = sum(rois) / len(rois) if rois else 0.0
        
        report = {
            "period_days": days,
            "total_savings": round(total_savings, 2),
            "total_requests": total_requests,
            "recommendations_count": len(relevant_results),
            "top_recommendations": top_recommendations_list,
            "savings_by_category": {k: round(v, 2) for k, v in savings_by_category.items()},
            "average_roi": round(average_roi, 1),
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def get_recommendation_history(self) -> List[Dict[str, Any]]:
        """Get all recommendations with their status and results."""
        history = []
        
        for rec_id, rec in self.recommendations.items():
            # Find results for this recommendation
            rec_results = [r for r in self.results if r.recommendation_id == rec_id]
            
            history.append({
                "id": rec.id,
                "title": rec.title,
                "category": rec.category,
                "description": rec.description,
                "status": rec.status,
                "priority": rec.priority,
                "created_at": rec.created_at,
                "implemented_at": rec.implemented_at,
                "estimated_savings_per_request": rec.estimated_savings_per_request,
                "estimated_savings_percentage": rec.estimated_savings_percentage,
                "total_savings": sum(r.actual_savings for r in rec_results),
                "results_count": len(rec_results),
                "latest_roi": rec_results[-1].roi_percentage if rec_results else None
            })
        
        return sorted(history, key=lambda x: x['created_at'], reverse=True)


# Global instance
_optimization_engine: Optional[CostOptimizationEngine] = None


def get_optimization_engine() -> CostOptimizationEngine:
    """Get or create the global optimization engine instance."""
    global _optimization_engine
    if _optimization_engine is None:
        _optimization_engine = CostOptimizationEngine()
    return _optimization_engine

