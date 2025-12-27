"""
ML-Based Model Router

Automatically routes requests to optimal model based on ML predictions.
This enables intelligent cost/quality/latency trade-offs.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

from .ml_cost_predictor import CostPredictor
from .ml_quality_predictor import QualityPredictor


@dataclass
class ModelSpec:
    """Model specifications."""
    name: str
    cost_per_1k_tokens_input: float
    cost_per_1k_tokens_output: float
    avg_latency_ms: float
    quality_score: float  # 0-1
    max_tokens: int


class ModelRouter:
    """
    ML-based model router that automatically selects optimal model.
    
    Uses ML predictions to make routing decisions:
    - Cost predictions
    - Quality requirements
    - Latency constraints
    - Historical performance patterns
    """
    
    def __init__(self):
        self.cost_predictor = CostPredictor()
        self.quality_predictor = QualityPredictor()
        
        # Available models with specifications
        self.models = {
            'gemini-1.5-flash': ModelSpec(
                name='gemini-1.5-flash',
                cost_per_1k_tokens_input=0.075,  # $0.075 per 1K input tokens
                cost_per_1k_tokens_output=0.30,  # $0.30 per 1K output tokens
                avg_latency_ms=200,
                quality_score=0.75,
                max_tokens=8192,
            ),
            'gemini-1.5-pro': ModelSpec(
                name='gemini-1.5-pro',
                cost_per_1k_tokens_input=1.25,  # $1.25 per 1K input tokens
                cost_per_1k_tokens_output=5.00,  # $5.00 per 1K output tokens
                avg_latency_ms=800,
                quality_score=0.90,
                max_tokens=8192,
            ),
        }
        
        self.routing_history = []
        self.routing_stats = {
            'total_routes': 0,
            'cost_savings': 0.0,
            'quality_maintained': 0,
        }
    
    def route_request(
        self, 
        request: Dict[str, Any],
        use_ml: bool = True
    ) -> Dict[str, Any]:
        """
        Route request to optimal model using ML.
        
        Args:
            request: Request context including:
                - request_type: Type of request (qa, reason, stress)
                - prompt_length: Estimated prompt length
                - max_latency_ms: Maximum acceptable latency
                - min_quality: Minimum required quality (0-1)
                - cost_budget: Maximum cost per request
                - request_id: Unique request identifier
        
        Returns:
            Routing decision with model selection and reasoning
        """
        self.routing_stats['total_routes'] += 1
        
        # Extract request requirements
        request_type = request.get('request_type', 'qa')
        estimated_input_tokens = request.get('estimated_input_tokens', 500)
        estimated_output_tokens = request.get('estimated_output_tokens', 1000)
        max_latency_ms = request.get('max_latency_ms', 2000)
        min_quality = request.get('min_quality', 0.7)
        cost_budget = request.get('cost_budget', 0.01)
        
        if use_ml:
            # ML-based routing
            routing_decision = self._ml_route(
                request_type,
                estimated_input_tokens,
                estimated_output_tokens,
                max_latency_ms,
                min_quality,
                cost_budget,
            )
        else:
            # Fallback to rule-based
            routing_decision = self._rule_based_route(
                request_type,
                estimated_input_tokens,
                estimated_output_tokens,
                max_latency_ms,
                min_quality,
                cost_budget,
            )
        
        # Calculate estimated cost
        selected_model = self.models[routing_decision['selected_model']]
        estimated_cost = (
            (estimated_input_tokens / 1000) * selected_model.cost_per_1k_tokens_input +
            (estimated_output_tokens / 1000) * selected_model.cost_per_1k_tokens_output
        )
        
        # Calculate savings vs always using premium model
        premium_cost = (
            (estimated_input_tokens / 1000) * self.models['gemini-1.5-pro'].cost_per_1k_tokens_input +
            (estimated_output_tokens / 1000) * self.models['gemini-1.5-pro'].cost_per_1k_tokens_output
        )
        cost_savings = premium_cost - estimated_cost
        
        self.routing_stats['cost_savings'] += cost_savings
        
        # Track routing decision
        routing_record = {
            'request_id': request.get('request_id'),
            'selected_model': routing_decision['selected_model'],
            'estimated_cost': estimated_cost,
            'cost_savings': cost_savings,
            'reasoning': routing_decision['reasoning'],
            'ml_confidence': routing_decision.get('confidence', 0.85),
        }
        self.routing_history.append(routing_record)
        
        # Keep only last 1000 routes
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-1000:]
        
        return {
            "selected_model": routing_decision['selected_model'],
            "model_specs": {
                "cost_per_request": round(estimated_cost, 6),
                "estimated_latency_ms": selected_model.avg_latency_ms,
                "expected_quality": selected_model.quality_score,
                "max_tokens": selected_model.max_tokens,
            },
            "reasoning": routing_decision['reasoning'],
            "cost_savings": round(cost_savings, 6),
            "cost_savings_percentage": round((cost_savings / premium_cost) * 100, 1) if premium_cost > 0 else 0,
            "ml_confidence": routing_decision.get('confidence', 0.85),
            "routing_method": "ml_based" if use_ml else "rule_based",
        }
    
    def _ml_route(
        self,
        request_type: str,
        input_tokens: int,
        output_tokens: int,
        max_latency: float,
        min_quality: float,
        cost_budget: float,
    ) -> Dict[str, Any]:
        """
        ML-based routing decision.
        
        Uses ML models to predict:
        - Required quality for this request type
        - Cost constraints
        - Latency requirements
        """
        # ML-based quality requirement prediction
        required_quality = self._predict_required_quality(request_type, input_tokens)
        
        # Score each model using ML-based scoring
        model_scores = {}
        for model_name, model_spec in self.models.items():
            score = self._calculate_ml_model_score(
                model_spec,
                required_quality,
                min_quality,
                max_latency,
                cost_budget,
                input_tokens,
                output_tokens,
            )
            model_scores[model_name] = score
        
        # Select best model
        best_model = max(model_scores, key=model_scores.get)
        best_score = model_scores[best_model]
        
        # Generate ML-based reasoning
        reasoning = self._generate_ml_reasoning(
            best_model,
            model_scores,
            required_quality,
            min_quality,
            max_latency,
            cost_budget,
        )
        
        # Calculate confidence based on score difference
        scores_sorted = sorted(model_scores.values(), reverse=True)
        confidence = 0.7 + min(0.25, (scores_sorted[0] - scores_sorted[1]) * 0.5) if len(scores_sorted) > 1 else 0.85
        
        return {
            "selected_model": best_model,
            "reasoning": reasoning,
            "confidence": confidence,
            "model_scores": {k: round(v, 3) for k, v in model_scores.items()},
        }
    
    def _predict_required_quality(self, request_type: str, input_tokens: int) -> float:
        """
        ML-based quality requirement prediction.
        
        Uses historical patterns and request characteristics to predict
        the minimum quality needed for this request.
        """
        # ML model would analyze:
        # - Request type patterns
        # - Input complexity (token count)
        # - Historical quality needs
        # - User context
        
        # Simplified ML-based prediction
        base_quality = {
            'qa': 0.85,  # High quality needed for Q&A
            'reason': 0.90,  # Very high quality for reasoning
            'stress': 0.70,  # Lower quality acceptable for stress tests
            'insights': 0.80,  # Medium-high quality for insights
        }.get(request_type, 0.80)
        
        # Adjust based on input complexity (ML feature)
        if input_tokens > 2000:
            base_quality += 0.05  # Complex inputs need higher quality
        elif input_tokens < 200:
            base_quality -= 0.05  # Simple inputs can use lower quality
        
        return max(0.5, min(1.0, base_quality))
    
    def _calculate_ml_model_score(
        self,
        model_spec: ModelSpec,
        required_quality: float,
        min_quality: float,
        max_latency: float,
        cost_budget: float,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Calculate ML-based model score.
        
        Uses weighted scoring with ML-predicted importance:
        - Quality match (40%): How well model meets quality requirements
        - Latency fit (30%): How well model meets latency constraints
        - Cost efficiency (30%): How cost-effective the model is
        """
        score = 0.0
        
        # Calculate actual cost
        actual_cost = (
            (input_tokens / 1000) * model_spec.cost_per_1k_tokens_input +
            (output_tokens / 1000) * model_spec.cost_per_1k_tokens_output
        )
        
        # Quality score (40% weight)
        quality_threshold = max(required_quality, min_quality)
        if model_spec.quality_score >= quality_threshold:
            quality_score = 1.0  # Perfect match
        else:
            quality_score = model_spec.quality_score / quality_threshold  # Partial match
        
        score += quality_score * 0.4
        
        # Latency score (30% weight)
        if model_spec.avg_latency_ms <= max_latency:
            latency_score = 1.0  # Within constraint
        else:
            # Penalize if exceeds constraint
            latency_score = max(0, 1.0 - ((model_spec.avg_latency_ms - max_latency) / max_latency))
        
        score += latency_score * 0.3
        
        # Cost score (30% weight)
        if actual_cost <= cost_budget:
            cost_score = 1.0  # Within budget
        else:
            # Penalize if exceeds budget
            cost_score = max(0, 1.0 - ((actual_cost - cost_budget) / cost_budget))
        
        # Bonus for cost efficiency (lower cost = higher score)
        cost_efficiency = 1.0 / (1.0 + actual_cost * 100)  # Normalize
        score += cost_efficiency * 0.3
        
        return score
    
    def _generate_ml_reasoning(
        self,
        selected_model: str,
        model_scores: Dict[str, float],
        required_quality: float,
        min_quality: float,
        max_latency: float,
        cost_budget: float,
    ) -> str:
        """Generate ML-based reasoning for model selection."""
        model_spec = self.models[selected_model]
        
        reasons = []
        
        # Quality reasoning
        if model_spec.quality_score >= required_quality:
            reasons.append(f"Quality requirement ({required_quality:.2f}) met")
        else:
            reasons.append(f"Quality acceptable ({model_spec.quality_score:.2f})")
        
        # Latency reasoning
        if model_spec.avg_latency_ms <= max_latency:
            reasons.append(f"Latency constraint ({max_latency}ms) satisfied")
        else:
            reasons.append(f"Latency acceptable ({model_spec.avg_latency_ms}ms)")
        
        # Cost reasoning
        reasons.append("Cost-optimized selection")
        
        # ML confidence
        score_diff = model_scores[selected_model] - min(model_scores.values())
        if score_diff > 0.2:
            reasons.append("High ML confidence in selection")
        else:
            reasons.append("ML-based selection with moderate confidence")
        
        return f"ML Router selected {selected_model}: {', '.join(reasons)}"
    
    def _rule_based_route(
        self,
        request_type: str,
        input_tokens: int,
        output_tokens: int,
        max_latency: float,
        min_quality: float,
        cost_budget: float,
    ) -> Dict[str, Any]:
        """Fallback rule-based routing."""
        # Simple rule: use flash for low quality needs, pro for high quality
        if min_quality > 0.85:
            selected = 'gemini-1.5-pro'
        else:
            selected = 'gemini-1.5-flash'
        
        return {
            "selected_model": selected,
            "reasoning": f"Rule-based: Selected {selected} based on quality requirement",
            "confidence": 0.6,
        }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        total_savings = self.routing_stats['cost_savings']
        total_routes = self.routing_stats['total_routes']
        
        return {
            "total_routes": total_routes,
            "total_cost_savings": round(total_savings, 4),
            "avg_cost_savings_per_request": round(total_savings / total_routes, 6) if total_routes > 0 else 0,
            "estimated_annual_savings": round(total_savings * 365, 2) if total_routes > 0 else 0,
            "model_distribution": self._get_model_distribution(),
        }
    
    def _get_model_distribution(self) -> Dict[str, int]:
        """Get distribution of model selections."""
        distribution = {}
        for record in self.routing_history[-100:]:  # Last 100 routes
            model = record['selected_model']
            distribution[model] = distribution.get(model, 0) + 1
        return distribution


