"""
Environment Validation Script

Validates that all required components are configured correctly for the hackathon submission.
Run this script before demo to ensure everything is ready.

Usage:
    python scripts/validate_setup.py
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of a validation check."""
    def __init__(self, name: str, passed: bool, message: str, critical: bool = True):
        self.name = name
        self.passed = passed
        self.message = message
        self.critical = critical


def check_environment_variables() -> List[ValidationResult]:
    """Check that required environment variables are set."""
    results = []
    
    required_vars = {
        "LRCP_GEMINI_API_KEY": "Gemini API key for LLM requests",
        "LRCP_DATADOG_API_KEY": "Datadog API key for metrics/logs",
        "DD_APP_KEY": "Datadog Application key for API calls",
    }
    
    optional_vars = {
        "DD_SITE": "Datadog site (defaults to datadoghq.com)",
        "DD_AGENT_HOST": "Datadog agent host (defaults to localhost)",
        "LRCP_CONFLUENT_BOOTSTRAP_SERVERS": "Confluent Kafka bootstrap servers (optional)",
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            results.append(ValidationResult(
                f"Environment: {var}",
                True,
                f"✓ {description} is set",
                critical=True
            ))
        else:
            results.append(ValidationResult(
                f"Environment: {var}",
                False,
                f"✗ {description} is NOT set (required)",
                critical=True
            ))
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            results.append(ValidationResult(
                f"Environment: {var}",
                True,
                f"✓ {description} is set",
                critical=False
            ))
        else:
            results.append(ValidationResult(
                f"Environment: {var}",
                True,
                f"○ {description} not set (optional)",
                critical=False
            ))
    
    return results


def check_datadog_api() -> List[ValidationResult]:
    """Check that Datadog API is accessible."""
    results = []
    
    try:
        from datadog import api
        
        api_key = os.getenv("DD_API_KEY") or os.getenv("LRCP_DATADOG_API_KEY")
        app_key = os.getenv("DD_APP_KEY")
        
        if not api_key or not app_key:
            results.append(ValidationResult(
                "Datadog API Connection",
                False,
                "✗ Missing API keys for Datadog API",
                critical=True
            ))
            return results
        
        api._api_key = api_key
        api._application_key = app_key
        
        # Test API connection
        try:
            monitors = api.Monitor.get_all(page_size=1)
            results.append(ValidationResult(
                "Datadog API Connection",
                True,
                "✓ Datadog API is accessible",
                critical=True
            ))
        except Exception as e:
            results.append(ValidationResult(
                "Datadog API Connection",
                False,
                f"✗ Datadog API error: {str(e)[:100]}",
                critical=True
            ))
            
    except ImportError:
        results.append(ValidationResult(
            "Datadog API Connection",
            False,
            "✗ Datadog Python library not installed (pip install datadog)",
            critical=True
        ))
    
    return results


def check_datadog_resources() -> List[ValidationResult]:
    """Check that Datadog resources (monitors, dashboard) exist."""
    results = []
    
    try:
        from datadog import api
        
        api_key = os.getenv("DD_API_KEY") or os.getenv("LRCP_DATADOG_API_KEY")
        app_key = os.getenv("DD_APP_KEY")
        
        if not api_key or not app_key:
            return results  # Skip if API keys not set
        
        api._api_key = api_key
        api._application_key = app_key
        
        # Check monitors
        try:
            monitors = api.Monitor.get_all()
            monitor_count = len(monitors.get("monitors", []))
            
            llm_monitors = [
                m for m in monitors.get("monitors", [])
                if "llm" in str(m.get("tags", [])).lower()
            ]
            
            results.append(ValidationResult(
                "Datadog Monitors",
                len(llm_monitors) >= 3,
                f"{'✓' if len(llm_monitors) >= 3 else '⚠'} Found {len(llm_monitors)} LLM monitors (recommend 5+)",
                critical=False
            ))
        except Exception as e:
            results.append(ValidationResult(
                "Datadog Monitors",
                False,
                f"✗ Could not check monitors: {str(e)[:100]}",
                critical=False
            ))
        
        # Check dashboard
        try:
            dashboards = api.Dashboard.get_all()
            dashboard_names = [d.get("title", "") for d in dashboards.get("dashboards", [])]
            
            has_llm_dashboard = any("LLM" in name or "llm" in name.lower() for name in dashboard_names)
            
            results.append(ValidationResult(
                "Datadog Dashboard",
                has_llm_dashboard,
                f"{'✓' if has_llm_dashboard else '⚠'} LLM dashboard {'found' if has_llm_dashboard else 'not found'}",
                critical=False
            ))
        except Exception as e:
            results.append(ValidationResult(
                "Datadog Dashboard",
                False,
                f"✗ Could not check dashboard: {str(e)[:100]}",
                critical=False
            ))
            
    except ImportError:
        pass  # Skip if datadog not installed
    
    return results


def check_ml_models() -> List[ValidationResult]:
    """Check that ML models are trained and available."""
    results = []
    
    models_dir = Path(__file__).parent.parent / "models"
    
    if not models_dir.exists():
        results.append(ValidationResult(
            "ML Models Directory",
            False,
            "✗ Models directory does not exist",
            critical=False
        ))
        return results
    
    model_files = list(models_dir.glob("*.pkl"))
    
    required_models = ["cost_predictor.pkl", "cost_scaler.pkl"]
    found_models = [f.name for f in model_files]
    
    for model in required_models:
        if model in found_models:
            results.append(ValidationResult(
                f"ML Model: {model}",
                True,
                f"✓ {model} exists",
                critical=False
            ))
        else:
            results.append(ValidationResult(
                f"ML Model: {model}",
                False,
                f"⚠ {model} not found (run: python scripts/train_models.py)",
                critical=False
            ))
    
    return results


def check_application_files() -> List[ValidationResult]:
    """Check that required application files exist."""
    results = []
    
    base_dir = Path(__file__).parent.parent
    
    required_files = [
        "app/main.py",
        "app/telemetry.py",
        "app/health_score.py",
        "app/incident_manager.py",
        "datadog/monitors.json",
        "datadog/dashboard.json",
        "README.md",
    ]
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            results.append(ValidationResult(
                f"File: {file_path}",
                True,
                f"✓ {file_path} exists",
                critical=True
            ))
        else:
            results.append(ValidationResult(
                f"File: {file_path}",
                False,
                f"✗ {file_path} NOT found",
                critical=True
            ))
    
    return results


def check_python_dependencies() -> List[ValidationResult]:
    """Check that required Python packages are installed."""
    results = []
    
    required_packages = {
        "fastapi": "FastAPI framework",
        "uvicorn": "ASGI server",
        "datadog": "Datadog Python library",
        "pydantic": "Data validation",
    }
    
    for package, description in required_packages.items():
        try:
            __import__(package)
            results.append(ValidationResult(
                f"Python Package: {package}",
                True,
                f"✓ {description} is installed",
                critical=True
            ))
        except ImportError:
            results.append(ValidationResult(
                f"Python Package: {package}",
                False,
                f"✗ {description} NOT installed (pip install {package})",
                critical=True
            ))
    
    return results


def main() -> int:
    """Run all validation checks."""
    logger.info("=" * 70)
    logger.info("Environment Validation Script")
    logger.info("=" * 70)
    logger.info("")
    
    all_results: List[ValidationResult] = []
    
    # Run all checks
    logger.info("Running validation checks...")
    logger.info("")
    
    all_results.extend(check_environment_variables())
    all_results.extend(check_python_dependencies())
    all_results.extend(check_application_files())
    all_results.extend(check_ml_models())
    all_results.extend(check_datadog_api())
    all_results.extend(check_datadog_resources())
    
    # Print results
    logger.info("=" * 70)
    logger.info("Validation Results")
    logger.info("=" * 70)
    logger.info("")
    
    critical_failed = []
    warnings = []
    passed = []
    
    for result in all_results:
        if result.critical:
            if result.passed:
                logger.info(f"✓ {result.name}: {result.message}")
                passed.append(result)
            else:
                logger.error(f"✗ {result.name}: {result.message}")
                critical_failed.append(result)
        else:
            if result.passed:
                logger.info(f"  {result.message}")
                passed.append(result)
            else:
                logger.warning(f"⚠ {result.name}: {result.message}")
                warnings.append(result)
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("Summary")
    logger.info("=" * 70)
    logger.info(f"✓ Passed: {len(passed)}")
    logger.info(f"⚠ Warnings: {len(warnings)}")
    logger.info(f"✗ Critical Failures: {len(critical_failed)}")
    logger.info("")
    
    if critical_failed:
        logger.error("CRITICAL ISSUES FOUND - Please fix before demo:")
        for result in critical_failed:
            logger.error(f"  - {result.name}: {result.message}")
        logger.info("")
        return 1
    
    if warnings:
        logger.warning("Warnings (non-critical):")
        for result in warnings:
            logger.warning(f"  - {result.name}: {result.message}")
        logger.info("")
        logger.info("These warnings won't prevent the demo from working.")
        logger.info("")
    
    logger.info("=" * 70)
    logger.info("✓ All critical checks passed! Ready for demo.")
    logger.info("=" * 70)
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

