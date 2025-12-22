"""
LLM Health Score Calculator

Computes a composite health score (0-100) that combines:
- Performance (latency, throughput)
- Reliability (errors, retries)
- Cost efficiency (cost per request, token efficiency)
- Quality (semantic similarity, response quality)
- Security (safety blocks, injection risks)

This single metric provides at-a-glance system health.
"""

from typing import Dict


def calculate_health_score(
    *,
    latency_ms: float,
    error_rate: float,
    retry_rate: float,
    cost_per_request: float,
    quality_score: float,
    safety_block_rate: float,
    token_efficiency: float,  # output_tokens / input_tokens
) -> Dict[str, float]:
    """
    Calculate composite LLM health score.
    
    Returns:
        {
            "health_score": 0-100,
            "performance_score": 0-100,
            "reliability_score": 0-100,
            "cost_score": 0-100,
            "quality_score": 0-100,
            "security_score": 0-100,
            "breakdown": {...}
        }
    """
    # Performance score (0-100): Based on latency
    # Target: <500ms = 100, <1000ms = 80, <1500ms = 60, >1500ms = 0
    if latency_ms < 500:
        performance_score = 100.0
    elif latency_ms < 1000:
        performance_score = 80.0 + (500 / 500) * 20  # Linear interpolation
        performance_score = max(80.0, 100.0 - ((latency_ms - 500) / 500) * 20)
    elif latency_ms < 1500:
        performance_score = 60.0 - ((latency_ms - 1000) / 500) * 60
    else:
        performance_score = max(0.0, 60.0 - ((latency_ms - 1500) / 500) * 60)
    
    # Reliability score (0-100): Based on error and retry rates
    # Lower is better: 0% errors = 100, 10% errors = 0
    reliability_score = max(0.0, 100.0 - (error_rate * 1000))
    retry_penalty = min(20.0, retry_rate * 100)  # Max 20 point penalty
    reliability_score = max(0.0, reliability_score - retry_penalty)
    
    # Cost score (0-100): Based on cost efficiency
    # Lower cost per request = higher score
    # Target: <$0.001 = 100, <$0.01 = 80, <$0.1 = 60, >$0.1 = 0
    if cost_per_request < 0.001:
        cost_score = 100.0
    elif cost_per_request < 0.01:
        cost_score = 80.0 - ((cost_per_request - 0.001) / 0.009) * 20
    elif cost_per_request < 0.1:
        cost_score = 60.0 - ((cost_per_request - 0.01) / 0.09) * 60
    else:
        cost_score = max(0.0, 60.0 - ((cost_per_request - 0.1) / 0.1) * 60)
    
    # Quality score (0-100): Direct mapping from semantic similarity
    quality_score_normalized = quality_score * 100.0
    
    # Security score (0-100): Based on safety block rate
    # 0% blocks = 100, 10% blocks = 0
    security_score = max(0.0, 100.0 - (safety_block_rate * 1000))
    
    # Token efficiency bonus (0-10 points)
    # Higher output/input ratio = better efficiency
    efficiency_bonus = min(10.0, token_efficiency * 10.0) if token_efficiency > 0 else 0.0
    
    # Weighted composite score
    weights = {
        "performance": 0.25,
        "reliability": 0.25,
        "cost": 0.20,
        "quality": 0.20,
        "security": 0.10,
    }
    
    health_score = (
        performance_score * weights["performance"]
        + reliability_score * weights["reliability"]
        + cost_score * weights["cost"]
        + quality_score_normalized * weights["quality"]
        + security_score * weights["security"]
        + efficiency_bonus
    )
    
    # Cap at 100
    health_score = min(100.0, health_score)
    
    return {
        "health_score": round(health_score, 2),
        "performance_score": round(performance_score, 2),
        "reliability_score": round(reliability_score, 2),
        "cost_score": round(cost_score, 2),
        "quality_score": round(quality_score_normalized, 2),
        "security_score": round(security_score, 2),
        "efficiency_bonus": round(efficiency_bonus, 2),
        "breakdown": {
            "latency_ms": latency_ms,
            "error_rate": error_rate,
            "retry_rate": retry_rate,
            "cost_per_request": cost_per_request,
            "quality_score": quality_score,
            "safety_block_rate": safety_block_rate,
            "token_efficiency": token_efficiency,
        },
    }

