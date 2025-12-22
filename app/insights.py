"""
AI-Powered Insights Engine

Analyzes telemetry data to provide:
- Cost optimization recommendations
- Predictive anomaly detection
- Automated remediation suggestions
- Root cause analysis
"""

from typing import Any, Dict, List


def generate_cost_optimization_recommendations(
    *,
    avg_cost_per_request: float,
    avg_input_tokens: float,
    avg_output_tokens: float,
    cost_trend: str,  # "increasing", "stable", "decreasing"
    token_ratio: float,  # output/input
) -> List[Dict[str, Any]]:
    """Generate AI-powered cost optimization recommendations."""
    recommendations = []
    
    # High cost per request
    if avg_cost_per_request > 0.01:
        recommendations.append({
            "priority": "high",
            "category": "cost",
            "title": "High Cost Per Request Detected",
            "description": f"Average cost per request is ${avg_cost_per_request:.4f}, exceeding optimal threshold.",
            "recommendations": [
                "Consider downgrading to a smaller model (e.g., gemini-1.5-flash) for non-critical requests",
                "Implement response caching for repeated queries",
                "Add prompt length limits to reduce input token usage",
                "Review and optimize prompt templates to reduce token count",
            ],
            "estimated_savings": f"${avg_cost_per_request * 0.3:.2f} per request (30% reduction potential)",
        })
    
    # High input token usage
    if avg_input_tokens > 2000:
        recommendations.append({
            "priority": "medium",
            "category": "tokens",
            "title": "High Input Token Usage",
            "description": f"Average input tokens: {avg_input_tokens:.0f}. Consider context optimization.",
            "recommendations": [
                "Implement context compression or summarization",
                "Use RAG (Retrieval Augmented Generation) to reduce context size",
                "Add context length limits per request type",
                "Review document chunking strategy",
            ],
            "estimated_savings": "20-40% token reduction possible",
        })
    
    # Low token efficiency
    if token_ratio < 0.1:
        recommendations.append({
            "priority": "medium",
            "category": "efficiency",
            "title": "Low Token Efficiency",
            "description": f"Output/input ratio: {token_ratio:.2f}. Model may be underutilized.",
            "recommendations": [
                "Review prompt engineering - prompts may be too verbose",
                "Consider if shorter responses would suffice",
                "Implement response length limits",
            ],
            "estimated_savings": "10-20% cost reduction possible",
        })
    
    # Increasing cost trend
    if cost_trend == "increasing":
        recommendations.append({
            "priority": "high",
            "category": "trend",
            "title": "Cost Trend Alert",
            "description": "Cost is trending upward. Investigate recent changes.",
            "recommendations": [
                "Review recent deployments or model changes",
                "Check for prompt engineering changes that increased token usage",
                "Investigate if traffic patterns changed",
                "Consider implementing cost budgets and alerts",
            ],
            "estimated_savings": "Prevent future cost overruns",
        })
    
    return recommendations


def generate_reliability_recommendations(
    *,
    error_rate: float,
    retry_rate: float,
    avg_latency_ms: float,
    timeout_rate: float,
) -> List[Dict[str, Any]]:
    """Generate reliability improvement recommendations."""
    recommendations = []
    
    if error_rate > 0.05:  # 5% error rate
        recommendations.append({
            "priority": "critical",
            "category": "reliability",
            "title": "High Error Rate Detected",
            "description": f"Error rate: {error_rate*100:.1f}%. System reliability is compromised.",
            "recommendations": [
                "Implement circuit breaker pattern to prevent cascade failures",
                "Review upstream service health (Vertex AI status)",
                "Add exponential backoff for retries",
                "Implement request queuing to handle bursts",
                "Review authentication and API key rotation",
            ],
            "impact": "High - User experience degradation",
        })
    
    if retry_rate > 0.1:  # 10% retry rate
        recommendations.append({
            "priority": "high",
            "category": "retries",
            "title": "High Retry Rate",
            "description": f"Retry rate: {retry_rate*100:.1f}%. Many requests require retries.",
            "recommendations": [
                "Investigate root cause of initial failures",
                "Implement smarter retry logic with jitter",
                "Add retry budget limits",
                "Consider failover to backup model",
            ],
            "impact": "Medium - Increased latency and cost",
        })
    
    if avg_latency_ms > 1500:
        recommendations.append({
            "priority": "high",
            "category": "performance",
            "title": "High Latency Detected",
            "description": f"Average latency: {avg_latency_ms:.0f}ms exceeds SLO threshold.",
            "recommendations": [
                "Consider model downgrade for latency-sensitive requests",
                "Implement request caching",
                "Review network connectivity to Vertex AI",
                "Add request timeout configuration",
                "Consider async processing for non-critical requests",
            ],
            "impact": "High - User experience degradation",
        })
    
    return recommendations


def generate_quality_recommendations(
    *,
    avg_quality_score: float,
    ungrounded_rate: float,
) -> List[Dict[str, Any]]:
    """Generate quality improvement recommendations."""
    recommendations = []
    
    if avg_quality_score < 0.5:
        recommendations.append({
            "priority": "high",
            "category": "quality",
            "title": "Quality Degradation Detected",
            "description": f"Average quality score: {avg_quality_score:.2f} is below acceptable threshold.",
            "recommendations": [
                "Review prompt engineering - prompts may need refinement",
                "Check for model drift or version changes",
                "Implement quality monitoring and alerting",
                "Consider A/B testing different prompt strategies",
                "Review training data quality if using fine-tuned models",
            ],
            "impact": "High - User trust and satisfaction",
        })
    
    if ungrounded_rate > 0.1:  # 10% ungrounded answers
        recommendations.append({
            "priority": "medium",
            "category": "hallucination",
            "title": "High Ungrounded Answer Rate",
            "description": f"Ungrounded answer rate: {ungrounded_rate*100:.1f}%. Model may be hallucinating.",
            "recommendations": [
                "Implement citation requirements in prompts",
                "Add fact-checking layer for critical responses",
                "Review RAG implementation if using retrieval",
                "Consider adding confidence scores to responses",
            ],
            "impact": "Medium - Potential misinformation",
        })
    
    return recommendations


def generate_security_recommendations(
    *,
    safety_block_rate: float,
    injection_risk_rate: float,
    token_abuse_rate: float,
) -> List[Dict[str, Any]]:
    """Generate security improvement recommendations."""
    recommendations = []
    
    if safety_block_rate > 0.05:  # 5% safety blocks
        recommendations.append({
            "priority": "high",
            "category": "security",
            "title": "High Safety Block Rate",
            "description": f"Safety block rate: {safety_block_rate*100:.1f}%. Potential security issues.",
            "recommendations": [
                "Review input validation and sanitization",
                "Implement rate limiting per user/IP",
                "Add prompt injection detection",
                "Review safety filter configuration",
                "Investigate user behavior patterns",
            ],
            "impact": "High - Security and compliance risk",
        })
    
    if injection_risk_rate > 0.02:  # 2% injection risk
        recommendations.append({
            "priority": "critical",
            "category": "security",
            "title": "Prompt Injection Risk Detected",
            "description": f"Injection risk rate: {injection_risk_rate*100:.1f}%. Potential attacks detected.",
            "recommendations": [
                "Immediately review and block suspicious patterns",
                "Implement input validation with allowlists",
                "Add prompt injection detection rules",
                "Consider using prompt templates with strict formatting",
                "Review and audit recent requests",
            ],
            "impact": "Critical - Security breach risk",
        })
    
    if token_abuse_rate > 0.01:  # 1% token abuse
        recommendations.append({
            "priority": "medium",
            "category": "abuse",
            "title": "Token Abuse Detected",
            "description": f"Token abuse rate: {token_abuse_rate*100:.1f}%. Unusual token usage patterns.",
            "recommendations": [
                "Implement token usage limits per user",
                "Add request size limits",
                "Review and block abusive patterns",
                "Consider implementing usage quotas",
            ],
            "impact": "Medium - Cost and resource abuse",
        })
    
    return recommendations


def generate_predictive_insights(
    *,
    latency_trend: str,
    cost_trend: str,
    error_trend: str,
) -> List[Dict[str, Any]]:
    """Generate predictive insights based on trends."""
    insights = []
    
    if latency_trend == "increasing":
        insights.append({
            "type": "prediction",
            "severity": "warning",
            "title": "Latency Trend Alert",
            "description": "Latency is trending upward. May breach SLO within 24 hours.",
            "recommended_action": "Investigate root cause and consider proactive scaling or model optimization.",
            "timeframe": "24-48 hours",
        })
    
    if cost_trend == "increasing":
        insights.append({
            "type": "prediction",
            "severity": "warning",
            "title": "Cost Trend Alert",
            "description": "Cost is trending upward. May exceed budget if trend continues.",
            "recommended_action": "Review token usage patterns and consider cost optimization measures.",
            "timeframe": "7 days",
        })
    
    if error_trend == "increasing":
        insights.append({
            "type": "prediction",
            "severity": "critical",
            "title": "Error Trend Alert",
            "description": "Error rate is trending upward. System may become unstable.",
            "recommended_action": "Immediately investigate and implement circuit breaker or failover.",
            "timeframe": "2-4 hours",
        })
    
    return insights

