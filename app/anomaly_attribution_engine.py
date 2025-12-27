"""
Anomaly Attribution Engine

Not just detecting anomalies, but attributing them to causes with confidence scores.
Example: "Anomaly caused by 23% increase in token usage from /stress endpoint"
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)

try:
    from datadog import api
    DD_API_AVAILABLE = True
except ImportError:
    DD_API_AVAILABLE = False
    logger.warning("Datadog API not available. Install: pip install datadog")


@dataclass
class AnomalyAttribution:
    """Represents an anomaly with its attributed causes."""
    anomaly_id: str
    anomaly_type: str  # "cost_spike", "latency_spike", "error_burst", "quality_drop"
    detected_at: str
    severity: str  # "critical", "high", "medium", "low"
    
    # Attribution details
    primary_cause: Dict[str, Any]  # Main cause with confidence
    contributing_factors: List[Dict[str, Any]]  # Additional factors
    total_confidence: float  # Overall confidence in attribution (0-1)
    
    # Metrics
    baseline_value: float
    anomalous_value: float
    change_percentage: float
    
    # Context
    affected_endpoints: List[str]
    affected_models: List[str]
    time_window: str


class AnomalyAttributionEngine:
    """
    Analyzes anomalies and attributes them to specific causes.
    
    Features:
    - Detect anomalies in metrics
    - Attribute to endpoints, models, request types
    - Calculate confidence scores
    - Provide causal analysis
    """
    
    def __init__(self):
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
    
    def attribute_anomaly(
        self,
        metric_name: str,
        anomaly_timestamp: datetime,
        baseline_period_hours: int = 24,
        analysis_window_hours: int = 1
    ) -> AnomalyAttribution:
        """
        Analyze an anomaly and attribute it to causes.
        
        Args:
            metric_name: Name of the metric with anomaly (e.g., "llm.cost.usd")
            anomaly_timestamp: When the anomaly was detected
            baseline_period_hours: Hours to look back for baseline
            analysis_window_hours: Window around anomaly to analyze
        
        Returns:
            AnomalyAttribution with causes and confidence scores
        """
        # Calculate time windows
        analysis_start = anomaly_timestamp - timedelta(hours=analysis_window_hours)
        analysis_end = anomaly_timestamp + timedelta(hours=analysis_window_hours)
        baseline_start = analysis_start - timedelta(hours=baseline_period_hours)
        
        # Fetch metrics from Datadog
        if self.datadog_enabled:
            anomaly_value, baseline_value = self._fetch_metric_comparison(
                metric_name, baseline_start, analysis_start, analysis_end
            )
            
            # Get breakdown by dimensions
            endpoint_breakdown = self._fetch_breakdown_by_dimension(
                metric_name, "endpoint", analysis_start, analysis_end, baseline_start, analysis_start
            )
            model_breakdown = self._fetch_breakdown_by_dimension(
                metric_name, "model", analysis_start, analysis_end, baseline_start, analysis_start
            )
            request_type_breakdown = self._fetch_breakdown_by_dimension(
                metric_name, "request_type", analysis_start, analysis_end, baseline_start, analysis_start
            )
        else:
            # Fallback to simulated data
            anomaly_value, baseline_value = self._simulate_metric_comparison(metric_name)
            endpoint_breakdown = self._simulate_breakdown("endpoint")
            model_breakdown = self._simulate_breakdown("model")
            request_type_breakdown = self._simulate_breakdown("request_type")
        
        # Calculate change
        change_percentage = ((anomaly_value - baseline_value) / baseline_value * 100) if baseline_value > 0 else 0
        
        # Determine anomaly type
        anomaly_type = self._classify_anomaly_type(metric_name, change_percentage)
        
        # Find primary cause
        primary_cause, primary_confidence = self._identify_primary_cause(
            endpoint_breakdown, model_breakdown, request_type_breakdown, change_percentage
        )
        
        # Find contributing factors
        contributing_factors = self._identify_contributing_factors(
            endpoint_breakdown, model_breakdown, request_type_breakdown, primary_cause
        )
        
        # Calculate total confidence
        total_confidence = self._calculate_total_confidence(
            primary_confidence, contributing_factors, change_percentage
        )
        
        # Get affected endpoints/models
        affected_endpoints = [item['name'] for item in endpoint_breakdown if item['change_pct'] > 10]
        affected_models = [item['name'] for item in model_breakdown if item['change_pct'] > 10]
        
        # Determine severity
        severity = self._determine_severity(change_percentage, anomaly_type)
        
        attribution = AnomalyAttribution(
            anomaly_id=f"anomaly-{anomaly_timestamp.strftime('%Y%m%d-%H%M%S')}",
            anomaly_type=anomaly_type,
            detected_at=anomaly_timestamp.isoformat(),
            severity=severity,
            primary_cause=primary_cause,
            contributing_factors=contributing_factors,
            total_confidence=total_confidence,
            baseline_value=baseline_value,
            anomalous_value=anomaly_value,
            change_percentage=change_percentage,
            affected_endpoints=affected_endpoints,
            affected_models=affected_models,
            time_window=f"{analysis_window_hours}h"
        )
        
        logger.info(f"Attributed anomaly: {anomaly_type} - {primary_cause['description']} (confidence: {total_confidence:.1%})")
        return attribution
    
    def _fetch_metric_comparison(
        self,
        metric_name: str,
        baseline_start: datetime,
        baseline_end: datetime,
        anomaly_end: datetime
    ) -> Tuple[float, float]:
        """Fetch metric values for comparison."""
        try:
            # Fetch baseline
            baseline_query = f"avg:{metric_name}{{service:llm-reliability-control-plane}}"
            baseline_response = api.Metric.query(
                start=int(baseline_start.timestamp()),
                end=int(baseline_end.timestamp()),
                query=baseline_query
            )
            
            baseline_value = 0.0
            if 'series' in baseline_response:
                values = []
                for series in baseline_response['series']:
                    if 'pointlist' in series:
                        for point in series['pointlist']:
                            if point[1] is not None:
                                values.append(point[1])
                if values:
                    baseline_value = sum(values) / len(values)
            
            # Fetch anomaly period
            anomaly_query = f"avg:{metric_name}{{service:llm-reliability-control-plane}}"
            anomaly_response = api.Metric.query(
                start=int(baseline_end.timestamp()),
                end=int(anomaly_end.timestamp()),
                query=anomaly_query
            )
            
            anomaly_value = 0.0
            if 'series' in anomaly_response:
                values = []
                for series in anomaly_response['series']:
                    if 'pointlist' in series:
                        for point in series['pointlist']:
                            if point[1] is not None:
                                values.append(point[1])
                if values:
                    anomaly_value = sum(values) / len(values)
            
            return anomaly_value, baseline_value
        except Exception as e:
            logger.warning(f"Could not fetch metric comparison: {e}")
            return 0.0, 0.0
    
    def _fetch_breakdown_by_dimension(
        self,
        metric_name: str,
        dimension: str,
        analysis_start: datetime,
        analysis_end: datetime,
        baseline_start: datetime,
        baseline_end: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch metric breakdown by dimension (endpoint, model, etc.)."""
        try:
            breakdown = []
            
            # Fetch analysis period
            analysis_query = f"avg:{metric_name}{{service:llm-reliability-control-plane}} by {dimension}"
            analysis_response = api.Metric.query(
                start=int(analysis_start.timestamp()),
                end=int(analysis_end.timestamp()),
                query=analysis_query
            )
            
            # Fetch baseline period
            baseline_query = f"avg:{metric_name}{{service:llm-reliability-control-plane}} by {dimension}"
            baseline_response = api.Metric.query(
                start=int(baseline_start.timestamp()),
                end=int(baseline_end.timestamp()),
                query=baseline_query
            )
            
            # Process results
            analysis_values = {}
            if 'series' in analysis_response:
                for series in analysis_response['series']:
                    tag = series.get('tag_set', [])
                    dimension_value = next((t.split(':')[1] for t in tag if t.startswith(f"{dimension}:")), "unknown")
                    if 'pointlist' in series:
                        values = [p[1] for p in series['pointlist'] if p[1] is not None]
                        if values:
                            analysis_values[dimension_value] = sum(values) / len(values)
            
            baseline_values = {}
            if 'series' in baseline_response:
                for series in baseline_response['series']:
                    tag = series.get('tag_set', [])
                    dimension_value = next((t.split(':')[1] for t in tag if t.startswith(f"{dimension}:")), "unknown")
                    if 'pointlist' in series:
                        values = [p[1] for p in series['pointlist'] if p[1] is not None]
                        if values:
                            baseline_values[dimension_value] = sum(values) / len(values)
            
            # Calculate changes
            all_keys = set(analysis_values.keys()) | set(baseline_values.keys())
            for key in all_keys:
                analysis_val = analysis_values.get(key, 0)
                baseline_val = baseline_values.get(key, 0)
                change_pct = ((analysis_val - baseline_val) / baseline_val * 100) if baseline_val > 0 else 0
                
                breakdown.append({
                    "name": key,
                    "baseline_value": baseline_val,
                    "analysis_value": analysis_val,
                    "change_pct": change_pct,
                    "contribution_pct": (analysis_val / sum(analysis_values.values()) * 100) if sum(analysis_values.values()) > 0 else 0
                })
            
            return sorted(breakdown, key=lambda x: abs(x['change_pct']), reverse=True)
        except Exception as e:
            logger.warning(f"Could not fetch breakdown by {dimension}: {e}")
            return []
    
    def _simulate_metric_comparison(self, metric_name: str) -> Tuple[float, float]:
        """Simulate metric comparison for demo."""
        if "cost" in metric_name:
            return 0.015, 0.008  # Cost spike
        elif "latency" in metric_name:
            return 2500.0, 800.0  # Latency spike
        elif "error" in metric_name:
            return 0.15, 0.02  # Error burst
        else:
            return 100.0, 50.0
    
    def _simulate_breakdown(self, dimension: str) -> List[Dict[str, Any]]:
        """Simulate breakdown for demo."""
        if dimension == "endpoint":
            return [
                {"name": "/stress", "baseline_value": 0.002, "analysis_value": 0.008, "change_pct": 300.0, "contribution_pct": 45.0},
                {"name": "/qa", "baseline_value": 0.003, "analysis_value": 0.005, "change_pct": 66.7, "contribution_pct": 30.0},
                {"name": "/reason", "baseline_value": 0.002, "analysis_value": 0.002, "change_pct": 0.0, "contribution_pct": 15.0},
            ]
        elif dimension == "model":
            return [
                {"name": "gemini-2.5-flash", "baseline_value": 0.004, "analysis_value": 0.010, "change_pct": 150.0, "contribution_pct": 60.0},
                {"name": "gemini-1.5-pro", "baseline_value": 0.003, "analysis_value": 0.005, "change_pct": 66.7, "contribution_pct": 40.0},
            ]
        else:
            return [
                {"name": "stress", "baseline_value": 0.002, "analysis_value": 0.008, "change_pct": 300.0, "contribution_pct": 50.0},
                {"name": "qa", "baseline_value": 0.003, "analysis_value": 0.004, "change_pct": 33.3, "contribution_pct": 30.0},
            ]
    
    def _classify_anomaly_type(self, metric_name: str, change_pct: float) -> str:
        """Classify the type of anomaly."""
        if "cost" in metric_name.lower():
            return "cost_spike"
        elif "latency" in metric_name.lower():
            return "latency_spike"
        elif "error" in metric_name.lower():
            return "error_burst"
        elif "quality" in metric_name.lower():
            return "quality_drop"
        else:
            return "metric_anomaly"
    
    def _identify_primary_cause(
        self,
        endpoint_breakdown: List[Dict[str, Any]],
        model_breakdown: List[Dict[str, Any]],
        request_type_breakdown: List[Dict[str, Any]],
        total_change_pct: float
    ) -> Tuple[Dict[str, Any], float]:
        """Identify the primary cause of the anomaly."""
        # Find the dimension with the largest change
        all_changes = []
        
        for item in endpoint_breakdown:
            if abs(item['change_pct']) > 10:  # Significant change
                all_changes.append({
                    "dimension": "endpoint",
                    "name": item['name'],
                    "change_pct": item['change_pct'],
                    "contribution_pct": item['contribution_pct'],
                    "baseline": item['baseline_value'],
                    "analysis": item['analysis_value']
                })
        
        for item in model_breakdown:
            if abs(item['change_pct']) > 10:
                all_changes.append({
                    "dimension": "model",
                    "name": item['name'],
                    "change_pct": item['change_pct'],
                    "contribution_pct": item['contribution_pct'],
                    "baseline": item['baseline_value'],
                    "analysis": item['analysis_value']
                })
        
        for item in request_type_breakdown:
            if abs(item['change_pct']) > 10:
                all_changes.append({
                    "dimension": "request_type",
                    "name": item['name'],
                    "change_pct": item['change_pct'],
                    "contribution_pct": item['contribution_pct'],
                    "baseline": item['baseline_value'],
                    "analysis": item['analysis_value']
                })
        
        if not all_changes:
            return {
                "dimension": "unknown",
                "name": "unknown",
                "description": "Unable to identify primary cause",
                "change_pct": total_change_pct
            }, 0.3
        
        # Sort by absolute change
        primary = max(all_changes, key=lambda x: abs(x['change_pct']))
        
        # Calculate confidence based on contribution and change magnitude
        confidence = min(0.95, 0.5 + (primary['contribution_pct'] / 100) * 0.3 + (min(abs(primary['change_pct']), 200) / 200) * 0.15)
        
        description = f"Anomaly caused by {abs(primary['change_pct']):.1f}% {'increase' if primary['change_pct'] > 0 else 'decrease'} in {primary['dimension']} '{primary['name']}'"
        
        return {
            "dimension": primary['dimension'],
            "name": primary['name'],
            "description": description,
            "change_pct": primary['change_pct'],
            "contribution_pct": primary['contribution_pct'],
            "baseline_value": primary['baseline'],
            "analysis_value": primary['analysis']
        }, confidence
    
    def _identify_contributing_factors(
        self,
        endpoint_breakdown: List[Dict[str, Any]],
        model_breakdown: List[Dict[str, Any]],
        request_type_breakdown: List[Dict[str, Any]],
        primary_cause: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify contributing factors (secondary causes)."""
        factors = []
        
        # Exclude primary cause
        for item in endpoint_breakdown:
            if item['name'] != primary_cause.get('name') and abs(item['change_pct']) > 15:
                factors.append({
                    "dimension": "endpoint",
                    "name": item['name'],
                    "description": f"{item['name']} endpoint contributed {item['contribution_pct']:.1f}% with {item['change_pct']:.1f}% change",
                    "change_pct": item['change_pct'],
                    "contribution_pct": item['contribution_pct'],
                    "confidence": min(0.8, 0.4 + (item['contribution_pct'] / 100) * 0.4)
                })
        
        for item in model_breakdown:
            if item['name'] != primary_cause.get('name') and abs(item['change_pct']) > 15:
                factors.append({
                    "dimension": "model",
                    "name": item['name'],
                    "description": f"{item['name']} model contributed {item['contribution_pct']:.1f}% with {item['change_pct']:.1f}% change",
                    "change_pct": item['change_pct'],
                    "contribution_pct": item['contribution_pct'],
                    "confidence": min(0.8, 0.4 + (item['contribution_pct'] / 100) * 0.4)
                })
        
        return sorted(factors, key=lambda x: abs(x['change_pct']), reverse=True)[:3]
    
    def _calculate_total_confidence(
        self,
        primary_confidence: float,
        contributing_factors: List[Dict[str, Any]],
        change_pct: float
    ) -> float:
        """Calculate total confidence in the attribution."""
        # Base confidence from primary cause
        confidence = primary_confidence
        
        # Boost if we have strong contributing factors
        if contributing_factors:
            avg_factor_confidence = sum(f['confidence'] for f in contributing_factors) / len(contributing_factors)
            confidence = (confidence * 0.7) + (avg_factor_confidence * 0.3)
        
        # Boost if change is very significant (easier to attribute)
        if abs(change_pct) > 50:
            confidence = min(0.95, confidence + 0.05)
        
        return confidence
    
    def _determine_severity(self, change_pct: float, anomaly_type: str) -> str:
        """Determine severity based on change percentage."""
        abs_change = abs(change_pct)
        
        if abs_change > 200:
            return "critical"
        elif abs_change > 100:
            return "high"
        elif abs_change > 50:
            return "medium"
        else:
            return "low"
    
    def generate_attribution_report(self, attribution: AnomalyAttribution) -> Dict[str, Any]:
        """Generate a human-readable attribution report."""
        return {
            "anomaly_id": attribution.anomaly_id,
            "anomaly_type": attribution.anomaly_type,
            "detected_at": attribution.detected_at,
            "severity": attribution.severity,
            "summary": f"{attribution.primary_cause['description']} (Confidence: {attribution.total_confidence:.1%})",
            "primary_cause": {
                "description": attribution.primary_cause['description'],
                "dimension": attribution.primary_cause['dimension'],
                "name": attribution.primary_cause['name'],
                "change_percentage": attribution.primary_cause['change_pct'],
                "contribution_percentage": attribution.primary_cause.get('contribution_pct', 0),
                "confidence": attribution.total_confidence
            },
            "contributing_factors": [
                {
                    "description": factor['description'],
                    "dimension": factor['dimension'],
                    "name": factor['name'],
                    "change_percentage": factor['change_pct'],
                    "confidence": factor['confidence']
                }
                for factor in attribution.contributing_factors
            ],
            "metrics": {
                "baseline_value": attribution.baseline_value,
                "anomalous_value": attribution.anomalous_value,
                "change_percentage": attribution.change_percentage
            },
            "affected_resources": {
                "endpoints": attribution.affected_endpoints,
                "models": attribution.affected_models
            },
            "time_window": attribution.time_window
        }


# Global instance
_attribution_engine: Optional[AnomalyAttributionEngine] = None


def get_attribution_engine() -> AnomalyAttributionEngine:
    """Get or create the global attribution engine instance."""
    global _attribution_engine
    if _attribution_engine is None:
        _attribution_engine = AnomalyAttributionEngine()
    return _attribution_engine

