"""
ML-Based Insights Engine

Replaces rule-based recommendations with actual ML models:
- ML-based cost prediction
- ML-based quality prediction
- Watchdog ML insights
- Model routing recommendations
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from .ml_cost_predictor import CostPredictor
from .ml_quality_predictor import QualityPredictor
from .watchdog_integration import WatchdogIntegration
from .model_router import ModelRouter

logger = logging.getLogger(__name__)


class MLInsightsEngine:
    """
    ML-based insights engine that uses actual machine learning models
    instead of rule-based logic.
    """
    
    def __init__(self):
        self.cost_predictor = CostPredictor()
        self.quality_predictor = QualityPredictor()
        self.watchdog = WatchdogIntegration()
        self.model_router = ModelRouter()
    
    def generate_ml_recommendations(
        self,
        current_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate ML-based recommendations using actual ML models.
        
        This replaces rule-based logic with:
        - ML cost prediction
        - ML quality prediction
        - Watchdog ML insights
        - Model routing optimization
        """
        recommendations = []
        predictive_insights = []
        
        # 1. ML-Based Cost Prediction
        cost_prediction = self._get_ml_cost_prediction(current_metrics)
        if cost_prediction and not cost_prediction.get('error'):
            recommendations.extend(cost_prediction.get('recommendations', []))
            predictive_insights.append({
                "type": "cost_prediction",
                "severity": "high" if cost_prediction.get('budget_risk') in ['critical', 'high'] else "medium",
                "title": f"ML Cost Prediction: {cost_prediction.get('budget_risk', 'unknown')} risk",
                "description": f"ML model predicts ${cost_prediction.get('predicted_cost_24h', 0):.4f} cost in next 24h. Budget utilization: {cost_prediction.get('budget_utilization', 0):.1f}%",
                "ml_confidence": cost_prediction.get('confidence', 0.85),
                "ml_model": cost_prediction.get('ml_model', 'gradient_boosting'),
                "recommended_action": self._get_cost_action(cost_prediction),
            })
        
        # 2. ML-Based Quality Prediction
        quality_prediction = self._get_ml_quality_prediction(current_metrics)
        if quality_prediction and not quality_prediction.get('error'):
            recommendations.extend(quality_prediction.get('recommendations', []))
            if quality_prediction.get('degradation_risk') in ['critical', 'high']:
                predictive_insights.append({
                    "type": "quality_prediction",
                    "severity": quality_prediction.get('degradation_risk', 'medium'),
                    "title": f"ML Quality Prediction: {quality_prediction.get('trend', 'unknown')} trend",
                    "description": f"ML model predicts quality will be {quality_prediction.get('predicted_quality_24h', 0):.2f} in 24h (current: {quality_prediction.get('current_quality', 0):.2f})",
                    "ml_confidence": quality_prediction.get('confidence', 0.85),
                    "ml_model": quality_prediction.get('ml_model', 'sentence_transformer'),
                    "recommended_action": self._get_quality_action(quality_prediction),
                })
        
        # 3. Watchdog ML Insights
        watchdog_insights = self.watchdog.get_ml_recommendations()
        for insight in watchdog_insights:
            recommendations.append({
                "priority": insight.get('priority', 'medium'),
                "category": "watchdog_ml",
                "title": insight.get('title'),
                "description": insight.get('description'),
                "ml_confidence": insight.get('confidence', 0.9),
                "ml_model": insight.get('ml_model', 'Watchdog'),
                "source": "datadog_watchdog",
                "recommendations": insight.get('recommendations', []),
            })
        
        # 4. Model Routing Optimization
        routing_recommendation = self._get_routing_recommendation(current_metrics)
        if routing_recommendation:
            recommendations.append(routing_recommendation)
        
        # Sort by priority and ML confidence
        recommendations = self._prioritize_recommendations(recommendations)
        
        return {
            "recommendations": recommendations,
            "predictive_insights": predictive_insights,
            "ml_models_used": {
                "cost_prediction": cost_prediction.get('ml_model') if cost_prediction else None,
                "quality_prediction": quality_prediction.get('ml_model') if quality_prediction else None,
                "watchdog": "datadog_watchdog" if watchdog_insights else None,
                "model_routing": "ml_router" if routing_recommendation else None,
            },
            "ml_confidence_scores": {
                "cost": cost_prediction.get('confidence') if cost_prediction else None,
                "quality": quality_prediction.get('confidence') if quality_prediction else None,
                "watchdog": max([i.get('confidence', 0.9) for i in watchdog_insights]) if watchdog_insights else None,
            },
        }
    
    def _get_ml_cost_prediction(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get ML-based cost prediction."""
        try:
            # Prepare metrics for prediction
            current_metrics = {
                'hour_of_day': datetime.now().hour,
                'day_of_week': datetime.now().weekday(),
                'request_count': metrics.get('request_count', 100),
                'avg_input_tokens': metrics.get('avg_input_tokens', 500),
                'avg_output_tokens': metrics.get('avg_output_tokens', 1000),
                'error_rate': metrics.get('error_rate', 0.02),
                'retry_rate': metrics.get('retry_rate', 0.05),
                'avg_latency_ms': metrics.get('avg_latency_ms', 800),
                'cost_per_request': metrics.get('avg_cost_per_request', 0.001),
            }
            
            daily_budget = metrics.get('daily_budget', 10.0)
            
            prediction = self.cost_predictor.predict_next_24h(current_metrics, daily_budget)
            return prediction
            
        except Exception as e:
            logger.error(f"Error in ML cost prediction: {e}")
            return None
    
    def _get_ml_quality_prediction(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get ML-based quality prediction."""
        try:
            # Get recent responses (would come from logs/metrics in production)
            recent_responses = metrics.get('recent_responses', [])
            
            if len(recent_responses) < 3:
                # Not enough data for ML prediction
                return None
            
            # Establish baseline if not done
            if not self.quality_predictor.baseline_embeddings:
                # Use first 10 responses as baseline
                baseline = recent_responses[:10] if len(recent_responses) >= 10 else recent_responses
                self.quality_predictor.establish_baseline(baseline)
            
            # Predict quality degradation
            prediction = self.quality_predictor.predict_quality_degradation(recent_responses)
            return prediction
            
        except Exception as e:
            logger.error(f"Error in ML quality prediction: {e}")
            return None
    
    def _get_routing_recommendation(self, metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get ML-based model routing recommendation."""
        try:
            # Simulate a routing decision
            request_context = {
                'request_type': metrics.get('request_type', 'qa'),
                'estimated_input_tokens': metrics.get('avg_input_tokens', 500),
                'estimated_output_tokens': metrics.get('avg_output_tokens', 1000),
                'max_latency_ms': metrics.get('max_latency_ms', 2000),
                'min_quality': metrics.get('min_quality', 0.7),
                'cost_budget': metrics.get('cost_budget', 0.01),
            }
            
            routing = self.model_router.route_request(request_context, use_ml=True)
            
            if routing.get('cost_savings_percentage', 0) > 10:
                return {
                    "priority": "high",
                    "category": "cost_optimization",
                    "title": f"ML Model Routing: Use {routing['selected_model']} for {routing['cost_savings_percentage']:.1f}% cost savings",
                    "description": f"ML router recommends {routing['selected_model']} with {routing['cost_savings_percentage']:.1f}% cost savings vs premium model",
                    "ml_confidence": routing.get('ml_confidence', 0.85),
                    "ml_model": "ml_model_router",
                    "estimated_savings": f"${routing.get('cost_savings', 0):.6f} per request",
                    "recommendations": [
                        f"Route requests to {routing['selected_model']}",
                        f"Expected quality: {routing['model_specs']['expected_quality']:.2f}",
                        f"Expected latency: {routing['model_specs']['estimated_latency_ms']}ms",
                    ],
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in model routing: {e}")
            return None
    
    def _get_cost_action(self, prediction: Dict[str, Any]) -> str:
        """Get recommended action from cost prediction."""
        risk = prediction.get('budget_risk', 'low')
        if risk == 'critical':
            return "Immediate cost optimization required. Consider model downgrade and caching."
        elif risk == 'high':
            return "Review cost optimization opportunities. Enable caching and optimize prompts."
        else:
            return "Monitor cost trends. Current prediction is within budget."
    
    def _get_quality_action(self, prediction: Dict[str, Any]) -> str:
        """Get recommended action from quality prediction."""
        risk = prediction.get('degradation_risk', 'low')
        trend = prediction.get('trend', 'stable')
        
        if risk == 'critical':
            return "Immediate action required. Consider model rollback and prompt review."
        elif trend == 'degrading':
            return "Quality trending down. Review prompt engineering and monitor closely."
        else:
            return "Quality stable. Continue monitoring."
    
    def _prioritize_recommendations(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize recommendations by ML confidence and priority."""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        
        def sort_key(rec):
            priority = priority_order.get(rec.get("priority", "low"), 3)
            confidence = rec.get("ml_confidence", 0)
            # Lower priority number + higher confidence = better
            return (priority, -confidence)
        
        return sorted(recommendations, key=sort_key)
    
    def train_models(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train ML models on historical data.
        
        This should be called periodically with new data to keep models up-to-date.
        """
        results = {}
        
        # Train cost predictor
        if self.cost_predictor.enabled:
            cost_training = self.cost_predictor.train(historical_data)
            results['cost_predictor'] = cost_training
        
        # Quality predictor doesn't need explicit training (uses embeddings)
        # But we can establish baseline
        if self.quality_predictor.enabled and historical_data:
            # Extract reference responses from historical data
            reference_responses = [
                d.get('response_text', '') 
                for d in historical_data 
                if d.get('response_text')
            ][:20]  # Use first 20 as baseline
            
            if len(reference_responses) >= 5:
                baseline_result = self.quality_predictor.establish_baseline(reference_responses)
                results['quality_predictor'] = baseline_result
        
        return results


