"""
Datadog Log Pipelines Integration

Deep integration with Datadog Log Pipelines for log processing, enrichment, and redaction.
Programmatically manages log pipelines.
"""

import os
import logging
import requests
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

try:
    from datadog import api
    DD_API_AVAILABLE = True
except ImportError:
    DD_API_AVAILABLE = False
    logger.warning("Datadog API not available. Install: pip install datadog")


class LogPipelinesIntegration:
    """
    Deep integration with Datadog Log Pipelines.
    
    Creates and manages log pipelines for processing, enrichment, and redaction.
    """
    
    def __init__(self):
        if DD_API_AVAILABLE:
            self.api_key = os.getenv("DD_API_KEY") or os.getenv("LRCP_DATADOG_API_KEY")
            self.app_key = os.getenv("DD_APP_KEY")
            self.site = os.getenv("DD_SITE", "datadoghq.com")
            if self.api_key and self.app_key:
                api._api_key = self.api_key
                api._application_key = self.app_key
                self.enabled = True
                self.base_url = f"https://api.{self.site}"
            else:
                self.enabled = False
        else:
            self.enabled = False
    
    def create_llm_request_pipeline(self) -> Dict[str, Any]:
        """
        Create a log pipeline for processing LLM request logs.
        
        This demonstrates deep integration: programmatically creating
        pipelines that process and enrich LLM logs.
        """
        if not self.enabled:
            return {"error": "Log Pipelines integration disabled"}
        
        try:
            pipeline_config = {
                "name": "LLM Request Pipeline",
                "filter": {
                    "query": "service:llm-reliability-control-plane source:python"
                },
                "processors": [
                    {
                        "type": "grok_parser",
                        "name": "Parse LLM Request Logs",
                        "is_enabled": True,
                        "samples": [],
                        "grok": {
                            "support_rules": "",
                            "match_rules": "rule LLM_REQUEST %{DATA:timestamp} %{WORD:level} %{DATA:message}"
                        },
                        "source": "message"
                    },
                    {
                        "type": "attribute_remapper",
                        "name": "Remap LLM Attributes",
                        "is_enabled": True,
                        "sources": [
                            {
                                "source": "llm.provider",
                                "source_type": "attribute"
                            },
                            {
                                "source": "llm.model",
                                "source_type": "attribute"
                            }
                        ],
                        "target": "llm.provider",
                        "target_type": "tag",
                        "preserve_source": False,
                        "override_on_conflict": False
                    },
                    {
                        "type": "url_parser",
                        "name": "Parse Request URLs",
                        "is_enabled": True,
                        "sources": ["http.url"],
                        "target": "http.url_details",
                        "normalize_ending_slashes": True
                    }
                ],
                "is_enabled": True
            }
            
            # Create pipeline via API
            url = f"{self.base_url}/api/v1/logs/config/pipelines"
            headers = {
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
                "Content-Type": "application/json",
            }
            
            response = requests.post(url, json=pipeline_config, headers=headers)
            response.raise_for_status()
            
            logger.info("Created LLM request log pipeline")
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to create log pipeline: {e}")
            return {
                "pipeline_config": pipeline_config,
                "message": "Log pipeline configuration created. Import manually via Datadog UI.",
                "error": str(e)
            }
    
    def create_cost_log_pipeline(self) -> Dict[str, Any]:
        """Create a pipeline for processing cost-related logs."""
        if not self.enabled:
            return {"error": "Log Pipelines integration disabled"}
        
        try:
            pipeline_config = {
                "name": "LLM Cost Pipeline",
                "filter": {
                    "query": "service:llm-reliability-control-plane cost"
                },
                "processors": [
                    {
                        "type": "grok_parser",
                        "name": "Parse Cost Logs",
                        "is_enabled": True,
                        "grok": {
                            "match_rules": "rule COST_LOG %{NUMBER:cost_usd:float} %{WORD:currency}"
                        },
                        "source": "message"
                    },
                    {
                        "type": "arithmetic_processor",
                        "name": "Calculate Cost Metrics",
                        "is_enabled": True,
                        "expression": "cost_usd * 100",
                        "target": "cost_cents",
                        "is_replace_missing": False
                    }
                ],
                "is_enabled": True
            }
            
            url = f"{self.base_url}/api/v1/logs/config/pipelines"
            headers = {
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
                "Content-Type": "application/json",
            }
            
            response = requests.post(url, json=pipeline_config, headers=headers)
            response.raise_for_status()
            
            logger.info("Created cost log pipeline")
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to create cost pipeline: {e}")
            return {
                "pipeline_config": pipeline_config,
                "message": "Cost pipeline configuration created. Import manually.",
                "error": str(e)
            }
    
    def create_security_redaction_pipeline(self) -> Dict[str, Any]:
        """
        Create a pipeline that redacts sensitive information from logs.
        
        This demonstrates security-focused log processing.
        """
        if not self.enabled:
            return {"error": "Log Pipelines integration disabled"}
        
        try:
            pipeline_config = {
                "name": "LLM Security Redaction Pipeline",
                "filter": {
                    "query": "service:llm-reliability-control-plane prompt"
                },
                "processors": [
                    {
                        "type": "string_builder_processor",
                        "name": "Redact Sensitive Prompts",
                        "is_enabled": True,
                        "template": "{{#if prompt}}[REDACTED: Prompt contains sensitive data]{{else}}{{message}}{{/if}}",
                        "target": "message",
                        "is_replace_missing": False
                    },
                    {
                        "type": "category_processor",
                        "name": "Categorize Security Events",
                        "is_enabled": True,
                        "target": "security.category",
                        "categories": [
                            {
                                "filter": {
                                    "query": "injection"
                                },
                                "name": "prompt_injection"
                            },
                            {
                                "filter": {
                                    "query": "abuse"
                                },
                                "name": "token_abuse"
                            }
                        ]
                    }
                ],
                "is_enabled": True
            }
            
            url = f"{self.base_url}/api/v1/logs/config/pipelines"
            headers = {
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
                "Content-Type": "application/json",
            }
            
            response = requests.post(url, json=pipeline_config, headers=headers)
            response.raise_for_status()
            
            logger.info("Created security redaction pipeline")
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to create security pipeline: {e}")
            return {
                "pipeline_config": pipeline_config,
                "message": "Security pipeline configuration created. Import manually.",
                "error": str(e)
            }
    
    def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all log pipelines."""
        if not self.enabled:
            return []
        
        try:
            url = f"{self.base_url}/api/v1/logs/config/pipelines"
            headers = {
                "DD-API-KEY": self.api_key,
                "DD-APPLICATION-KEY": self.app_key,
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json().get("pipelines", [])
            
        except Exception as e:
            logger.error(f"Failed to list pipelines: {e}")
            return []


# Global instance
_log_pipelines: Optional[LogPipelinesIntegration] = None


def get_log_pipelines() -> LogPipelinesIntegration:
    """Get or create global LogPipelinesIntegration instance."""
    global _log_pipelines
    if _log_pipelines is None:
        _log_pipelines = LogPipelinesIntegration()
    return _log_pipelines

