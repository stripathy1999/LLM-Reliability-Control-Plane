"""
Datadog Notebooks Integration

Deep integration with Datadog Notebooks for interactive analysis and documentation.
Creates notebooks programmatically for root cause analysis, cost optimization, etc.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from datadog import api
    DD_API_AVAILABLE = True
except ImportError:
    DD_API_AVAILABLE = False
    logger.warning("Datadog API not available. Install: pip install datadog")


class NotebooksIntegration:
    """
    Deep integration with Datadog Notebooks.
    
    Creates and manages notebooks for analysis and documentation.
    """
    
    def __init__(self):
        if DD_API_AVAILABLE:
            self.api_key = os.getenv("DD_API_KEY") or os.getenv("LRCP_DATADOG_API_KEY")
            self.app_key = os.getenv("DD_APP_KEY")
            if self.api_key and self.app_key:
                api._api_key = self.api_key
                api._application_key = self.app_key
                self.enabled = True
            else:
                self.enabled = False
        else:
            self.enabled = False
    
    def create_root_cause_analysis_notebook(
        self,
        incident_id: Optional[str] = None,
        incident_title: Optional[str] = None,
        time_range_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Create a notebook for root cause analysis of an incident.
        
        This demonstrates deep integration: automatically creating analysis notebooks
        when incidents occur.
        """
        if not self.enabled:
            logger.warning("Notebooks integration disabled: Missing API keys")
            return {"error": "Notebooks integration disabled"}
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_range_hours)
            
            # Create notebook with analysis cells
            notebook_data = {
                "data": {
                    "attributes": {
                        "name": f"Root Cause Analysis: {incident_title or 'Incident'}" if incident_id else "LLM Incident Root Cause Analysis",
                        "cells": [
                            {
                                "type": "markdown",
                                "attributes": {
                                    "definition": {
                                        "text": f"# 🔍 Root Cause Analysis\n\n**Incident:** {incident_title or 'Unknown'}\n**Time Range:** {start_time.isoformat()} to {end_time.isoformat()}\n\n## Analysis Overview\n\nThis notebook analyzes the root cause of the incident by examining:\n- Metrics trends\n- Trace analysis\n- Log patterns\n- Service dependencies"
                                    }
                                }
                            },
                            {
                                "type": "timeseries",
                                "attributes": {
                                    "definition": {
                                        "requests": [
                                            {
                                                "q": "avg:llm.request.latency_ms{service:llm-reliability-control-plane}",
                                                "display_type": "line",
                                                "style": {
                                                    "palette": "dog_classic",
                                                    "line_type": "solid",
                                                    "line_width": "normal"
                                                }
                                            }
                                        ],
                                        "yaxis": {
                                            "label": "Latency (ms)",
                                            "scale": "linear"
                                        },
                                        "show_legend": True,
                                        "legend_size": "0"
                                    }
                                }
                            },
                            {
                                "type": "timeseries",
                                "attributes": {
                                    "definition": {
                                        "requests": [
                                            {
                                                "q": "sum:llm.error.count{service:llm-reliability-control-plane}",
                                                "display_type": "bars",
                                                "style": {
                                                    "palette": "dog_classic",
                                                    "line_type": "solid",
                                                    "line_width": "normal"
                                                }
                                            }
                                        ],
                                        "yaxis": {
                                            "label": "Error Count",
                                            "scale": "linear"
                                        }
                                    }
                                }
                            },
                            {
                                "type": "timeseries",
                                "attributes": {
                                    "definition": {
                                        "requests": [
                                            {
                                                "q": "sum:llm.cost.usd{service:llm-reliability-control-plane}",
                                                "display_type": "line",
                                                "style": {
                                                    "palette": "green",
                                                    "line_type": "solid",
                                                    "line_width": "normal"
                                                }
                                            }
                                        ],
                                        "yaxis": {
                                            "label": "Cost (USD)",
                                            "scale": "linear"
                                        }
                                    }
                                }
                            },
                            {
                                "type": "markdown",
                                "attributes": {
                                    "definition": {
                                        "text": "## 🔎 Findings\n\n### Key Observations:\n1. **Latency Spike:** Check the latency timeseries above\n2. **Error Patterns:** Review error count trends\n3. **Cost Impact:** Analyze cost during incident period\n\n### Next Steps:\n1. Review APM traces for slow spans\n2. Check logs for error patterns\n3. Analyze service dependencies"
                                    }
                                }
                            },
                            {
                                "type": "query_value",
                                "attributes": {
                                    "definition": {
                                        "requests": [
                                            {
                                                "q": "avg:llm.health_score{service:llm-reliability-control-plane}",
                                                "aggregator": "avg"
                                            }
                                        ],
                                        "autoscale": True,
                                        "precision": 2,
                                        "text_align": "center",
                                        "title": "Health Score During Incident"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            # Create notebook via API
            # Note: Datadog Notebooks API may require different format
            # This is a conceptual implementation
            response = api.Notebooks.create(**notebook_data)
            
            logger.info(f"Created root cause analysis notebook for incident: {incident_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create notebook: {e}")
            # Fallback: return notebook structure for manual creation
            return {
                "notebook_structure": notebook_data,
                "message": "Notebook structure created. Import manually or use Datadog UI.",
                "error": str(e)
            }
    
    def create_cost_optimization_notebook(
        self,
        recommendation_id: Optional[str] = None,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Create a notebook analyzing cost optimization opportunities."""
        if not self.enabled:
            return {"error": "Notebooks integration disabled"}
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            notebook_data = {
                "data": {
                    "attributes": {
                        "name": f"Cost Optimization Analysis: {recommendation_id or 'General'}",
                        "cells": [
                            {
                                "type": "markdown",
                                "attributes": {
                                    "definition": {
                                        "text": f"# 💰 Cost Optimization Analysis\n\n**Period:** {start_time.date()} to {end_time.date()}\n\n## Overview\n\nThis notebook analyzes cost optimization opportunities for the LLM application."
                                    }
                                }
                            },
                            {
                                "type": "timeseries",
                                "attributes": {
                                    "definition": {
                                        "requests": [
                                            {
                                                "q": "sum:llm.cost.usd{service:llm-reliability-control-plane} by {endpoint}",
                                                "display_type": "bars",
                                                "style": {
                                                    "palette": "dog_classic"
                                                }
                                            }
                                        ],
                                        "yaxis": {
                                            "label": "Cost (USD)",
                                            "scale": "linear"
                                        },
                                        "title": "Cost by Endpoint"
                                    }
                                }
                            },
                            {
                                "type": "timeseries",
                                "attributes": {
                                    "definition": {
                                        "requests": [
                                            {
                                                "q": "sum:llm.tokens.input{service:llm-reliability-control-plane}",
                                                "display_type": "line"
                                            },
                                            {
                                                "q": "sum:llm.tokens.output{service:llm-reliability-control-plane}",
                                                "display_type": "line"
                                            }
                                        ],
                                        "yaxis": {
                                            "label": "Tokens",
                                            "scale": "linear"
                                        },
                                        "title": "Token Usage Trends"
                                    }
                                }
                            },
                            {
                                "type": "query_value",
                                "attributes": {
                                    "definition": {
                                        "requests": [
                                            {
                                                "q": "sum:llm.optimization.savings.total{service:llm-reliability-control-plane}",
                                                "aggregator": "sum"
                                            }
                                        ],
                                        "title": "Total Savings from Optimizations",
                                        "precision": 2,
                                        "text_align": "center"
                                    }
                                }
                            },
                            {
                                "type": "markdown",
                                "attributes": {
                                    "definition": {
                                        "text": "## 💡 Recommendations\n\n1. **High-Cost Endpoints:** Identify endpoints with highest cost\n2. **Token Optimization:** Review token usage patterns\n3. **Model Selection:** Consider model downgrades for non-critical requests\n4. **Caching:** Implement response caching for repeated queries"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            response = api.Notebooks.create(**notebook_data)
            logger.info(f"Created cost optimization notebook")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create notebook: {e}")
            return {
                "notebook_structure": notebook_data,
                "message": "Notebook structure created. Import manually.",
                "error": str(e)
            }
    
    def create_anomaly_analysis_notebook(
        self,
        anomaly_id: str,
        metric_name: str,
        attribution: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a notebook analyzing an anomaly with attribution."""
        if not self.enabled:
            return {"error": "Notebooks integration disabled"}
        
        try:
            notebook_data = {
                "data": {
                    "attributes": {
                        "name": f"Anomaly Analysis: {anomaly_id}",
                        "cells": [
                            {
                                "type": "markdown",
                                "attributes": {
                                    "definition": {
                                        "text": f"# 🚨 Anomaly Analysis\n\n**Anomaly ID:** {anomaly_id}\n**Metric:** {metric_name}\n\n## Attribution\n\n**Primary Cause:** {attribution.get('primary_cause', {}).get('description', 'Unknown')}\n**Confidence:** {attribution.get('total_confidence', 0) * 100:.1f}%\n\n**Contributing Factors:**\n" + "\n".join([
                                            f"- {factor.get('description', 'Unknown')}"
                                            for factor in attribution.get('contributing_factors', [])
                                        ])
                                    }
                                }
                            },
                            {
                                "type": "timeseries",
                                "attributes": {
                                    "definition": {
                                        "requests": [
                                            {
                                                "q": f"avg:{metric_name}{{service:llm-reliability-control-plane}}",
                                                "display_type": "line"
                                            }
                                        ],
                                        "title": f"Metric: {metric_name}",
                                        "yaxis": {
                                            "label": "Value",
                                            "scale": "linear"
                                        }
                                    }
                                }
                            },
                            {
                                "type": "markdown",
                                "attributes": {
                                    "definition": {
                                        "text": f"## 📊 Analysis\n\n**Baseline Value:** {attribution.get('baseline_value', 0)}\n**Anomalous Value:** {attribution.get('anomalous_value', 0)}\n**Change:** {attribution.get('change_percentage', 0):.1f}%\n\n**Affected Resources:**\n- Endpoints: {', '.join(attribution.get('affected_resources', {}).get('endpoints', []))}\n- Models: {', '.join(attribution.get('affected_resources', {}).get('models', []))}"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            response = api.Notebooks.create(**notebook_data)
            logger.info(f"Created anomaly analysis notebook: {anomaly_id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create notebook: {e}")
            return {
                "notebook_structure": notebook_data,
                "message": "Notebook structure created. Import manually.",
                "error": str(e)
            }


# Global instance
_notebooks: Optional[NotebooksIntegration] = None


def get_notebooks() -> NotebooksIntegration:
    """Get or create global NotebooksIntegration instance."""
    global _notebooks
    if _notebooks is None:
        _notebooks = NotebooksIntegration()
    return _notebooks

