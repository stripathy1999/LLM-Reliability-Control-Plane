"""
ML Model Training Utilities

Utilities for training and updating ML models with historical data.
This should be run periodically to keep models up-to-date.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from .ml_cost_predictor import CostPredictor
from .ml_quality_predictor import QualityPredictor

logger = logging.getLogger(__name__)


def prepare_training_data(
    metrics_history: List[Dict[str, Any]]
) -> List[Dict[str, float]]:
    """
    Prepare historical metrics for ML model training.
    
    Converts raw metrics into training format with time-based features.
    """
    training_data = []
    
    for metric in metrics_history:
        timestamp = metric.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        training_point = {
            'hour_of_day': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'request_count': metric.get('request_count', 0),
            'avg_input_tokens': metric.get('avg_input_tokens', 0),
            'avg_output_tokens': metric.get('avg_output_tokens', 0),
            'error_rate': metric.get('error_rate', 0),
            'retry_rate': metric.get('retry_rate', 0),
            'avg_latency_ms': metric.get('avg_latency_ms', 0),
            'cost_usd': metric.get('cost_usd', 0),
        }
        
        training_data.append(training_point)
    
    return training_data


def train_all_models(historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Train all ML models on historical data.
    
    This should be called periodically (e.g., daily) to update models.
    """
    results = {}
    
    # Prepare training data
    training_data = prepare_training_data(historical_data)
    
    if len(training_data) < 10:
        return {
            "error": "Not enough training data",
            "required": 10,
            "provided": len(training_data),
        }
    
    # Train cost predictor
    cost_predictor = CostPredictor()
    if cost_predictor.enabled:
        cost_result = cost_predictor.train(training_data)
        results['cost_predictor'] = cost_result
        logger.info(f"Cost predictor trained: {cost_result}")
    else:
        results['cost_predictor'] = {"error": "Cost predictor not enabled"}
    
    # Establish quality baseline
    quality_predictor = QualityPredictor()
    if quality_predictor.enabled:
        # Extract reference responses
        reference_responses = [
            d.get('response_text', '')
            for d in historical_data
            if d.get('response_text')
        ][:20]
        
        if len(reference_responses) >= 5:
            baseline_result = quality_predictor.establish_baseline(reference_responses)
            results['quality_predictor'] = baseline_result
            logger.info(f"Quality baseline established: {baseline_result}")
        else:
            results['quality_predictor'] = {"error": "Not enough reference responses"}
    else:
        results['quality_predictor'] = {"error": "Quality predictor not enabled"}
    
    return {
        "status": "completed",
        "training_samples": len(training_data),
        "results": results,
        "timestamp": datetime.now().isoformat(),
    }


def generate_synthetic_training_data(days: int = 7) -> List[Dict[str, Any]]:
    """
    Generate synthetic training data for initial model training.
    
    In production, this would come from actual historical metrics.
    """
    import random
    from datetime import datetime, timedelta
    
    data = []
    base_time = datetime.now() - timedelta(days=days)
    
    for i in range(days * 24):  # Hourly data points
        timestamp = base_time + timedelta(hours=i)
        
        # Simulate realistic patterns
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Higher traffic during business hours
        request_count = 50 + (30 if 9 <= hour <= 17 else 10) + random.randint(-10, 10)
        
        # Vary tokens based on time
        avg_input_tokens = 500 + random.randint(-100, 200)
        avg_output_tokens = 1000 + random.randint(-200, 400)
        
        # Calculate cost
        cost_usd = (
            (avg_input_tokens / 1_000_000) * 1.25 +
            (avg_output_tokens / 1_000_000) * 5.00
        ) * request_count
        
        data.append({
            'timestamp': timestamp.isoformat(),
            'hour_of_day': hour,
            'day_of_week': day_of_week,
            'request_count': request_count,
            'avg_input_tokens': avg_input_tokens,
            'avg_output_tokens': avg_output_tokens,
            'error_rate': random.uniform(0.01, 0.05),
            'retry_rate': random.uniform(0.02, 0.08),
            'avg_latency_ms': random.uniform(600, 1200),
            'cost_usd': cost_usd,
            'response_text': f"Sample response {i}",  # For quality baseline
        })
    
    return data


