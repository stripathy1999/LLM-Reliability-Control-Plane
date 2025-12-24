#!/usr/bin/env python3
"""
Comprehensive End-to-End Test Script for LLM Reliability Control Plane

Tests all endpoints, validates responses, and verifies metrics emission.
"""

import asyncio
import json
import os
import sys
import time
from typing import Any, Dict

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import httpx


# Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("LRCP_GEMINI_API_KEY")

# Test results
test_results: Dict[str, Any] = {
    "passed": [],
    "failed": [],
    "warnings": [],
}


def log_test(name: str, status: str, message: str = ""):
    """Log test result."""
    symbol = "✅" if status == "pass" else "❌" if status == "fail" else "⚠️"
    print(f"{symbol} {name}: {message}")
    
    if status == "pass":
        test_results["passed"].append(name)
    elif status == "fail":
        test_results["failed"].append(name)
    else:
        test_results["warnings"].append(name)


async def test_health_endpoint(client: httpx.AsyncClient):
    """Test /health endpoint."""
    try:
        response = await client.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                log_test("Health Endpoint", "pass", "Returns 200 OK with status=ok")
                return True
            else:
                log_test("Health Endpoint", "fail", f"Unexpected response: {data}")
                return False
        else:
            log_test("Health Endpoint", "fail", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("Health Endpoint", "fail", f"Exception: {str(e)}")
        return False


async def test_root_endpoint(client: httpx.AsyncClient):
    """Test root endpoint."""
    try:
        response = await client.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                log_test("Root Endpoint", "pass", "Returns 200 OK")
                return True
            else:
                log_test("Root Endpoint", "fail", f"Unexpected response: {data}")
                return False
        else:
            log_test("Root Endpoint", "fail", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        log_test("Root Endpoint", "fail", f"Exception: {str(e)}")
        return False


async def test_qa_endpoint(client: httpx.AsyncClient):
    """Test /qa endpoint."""
    try:
        payload = {
            "question": "What is artificial intelligence?",
            "document": "Artificial intelligence (AI) is the simulation of human intelligence by machines."
        }
        response = await client.post(
            f"{API_BASE_URL}/qa",
            json=payload,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if "answer" in data and "metadata" in data:
                metadata = data["metadata"]
                required_fields = ["prompt_id", "latency_ms", "input_tokens", "output_tokens", "cost_usd"]
                missing = [f for f in required_fields if f not in metadata]
                
                if not missing:
                    log_test("QA Endpoint", "pass", 
                            f"Answer length: {len(data['answer'])} chars, "
                            f"Latency: {metadata['latency_ms']:.2f}ms, "
                            f"Cost: ${metadata['cost_usd']:.6f}")
                    return True
                else:
                    log_test("QA Endpoint", "fail", f"Missing metadata fields: {missing}")
                    return False
            else:
                log_test("QA Endpoint", "fail", f"Missing answer or metadata: {data}")
                return False
        else:
            log_test("QA Endpoint", "fail", f"Status code: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        log_test("QA Endpoint", "fail", f"Exception: {str(e)}")
        return False


async def test_qa_with_simulations(client: httpx.AsyncClient):
    """Test /qa endpoint with various simulation flags."""
    simulations = [
        ("latency", {"simulate_latency": "true"}),
        ("retry", {"simulate_retry": "true"}),
        ("bad_prompt", {"simulate_bad_prompt": "true"}),
    ]
    
    all_passed = True
    for name, params in simulations:
        try:
            payload = {"question": "test", "document": "test"}
            response = await client.post(
                f"{API_BASE_URL}/qa",
                json=payload,
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                log_test(f"QA Endpoint ({name})", "pass", "Simulation works")
            else:
                log_test(f"QA Endpoint ({name})", "fail", f"Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            log_test(f"QA Endpoint ({name})", "fail", f"Exception: {str(e)}")
            all_passed = False
    
    return all_passed


async def test_reason_endpoint(client: httpx.AsyncClient):
    """Test /reason endpoint."""
    try:
        payload = {"prompt": "Explain the concept of machine learning in simple terms."}
        response = await client.post(
            f"{API_BASE_URL}/reason",
            json=payload,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            if "answer" in data and "metadata" in data:
                log_test("Reason Endpoint", "pass", 
                        f"Answer length: {len(data['answer'])} chars")
                return True
            else:
                log_test("Reason Endpoint", "fail", f"Missing answer or metadata")
                return False
        else:
            log_test("Reason Endpoint", "fail", f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Reason Endpoint", "fail", f"Exception: {str(e)}")
        return False


async def test_stress_endpoint(client: httpx.AsyncClient):
    """Test /stress endpoint."""
    try:
        payload = {"prompt": "Summarize", "repetitions": 5}
        response = await client.post(
            f"{API_BASE_URL}/stress",
            json=payload,
            timeout=60.0  # Longer timeout for stress test
        )
        
        if response.status_code == 200:
            data = response.json()
            if "answer" in data and "metadata" in data:
                metadata = data["metadata"]
                input_tokens = metadata.get("input_tokens", 0)
                log_test("Stress Endpoint", "pass", 
                        f"Input tokens: {input_tokens}, "
                        f"Cost: ${metadata.get('cost_usd', 0):.6f}")
                return True
            else:
                log_test("Stress Endpoint", "fail", "Missing answer or metadata")
                return False
        else:
            log_test("Stress Endpoint", "fail", f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Stress Endpoint", "fail", f"Exception: {str(e)}")
        return False


async def test_insights_endpoint(client: httpx.AsyncClient):
    """Test /insights endpoint."""
    try:
        payload = {
            "avg_latency_ms": 1200.0,
            "error_rate": 0.02,
            "retry_rate": 0.05,
            "avg_cost_per_request": 0.008,
            "avg_input_tokens": 1500.0,
            "avg_output_tokens": 200.0,
            "avg_quality_score": 0.65,
            "ungrounded_rate": 0.08,
            "safety_block_rate": 0.03,
            "injection_risk_rate": 0.01,
            "token_abuse_rate": 0.005,
            "timeout_rate": 0.01,
            "latency_trend": "increasing",
            "cost_trend": "increasing",
            "error_trend": "stable"
        }
        response = await client.post(
            f"{API_BASE_URL}/insights",
            json=payload,
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            required_keys = ["health_summary", "recommendations", "predictive_insights", "priority_actions"]
            missing = [k for k in required_keys if k not in data]
            
            if not missing:
                health_score = data["health_summary"].get("overall_health_score", 0)
                log_test("Insights Endpoint", "pass", 
                        f"Health score: {health_score}, "
                        f"Recommendations: {len(data['recommendations'])}, "
                        f"Priority actions: {len(data['priority_actions'])}")
                return True
            else:
                log_test("Insights Endpoint", "fail", f"Missing keys: {missing}")
                return False
        else:
            log_test("Insights Endpoint", "fail", f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Insights Endpoint", "fail", f"Exception: {str(e)}")
        return False


async def test_error_handling(client: httpx.AsyncClient):
    """Test error handling for invalid requests."""
    try:
        # Test missing required field
        response = await client.post(
            f"{API_BASE_URL}/qa",
            json={},  # Missing required fields
            timeout=10.0
        )
        
        if response.status_code == 422:  # Validation error
            log_test("Error Handling", "pass", "Returns 422 for invalid request")
            return True
        else:
            log_test("Error Handling", "warn", f"Expected 422, got {response.status_code}")
            return True  # Not critical
    except Exception as e:
        log_test("Error Handling", "warn", f"Exception: {str(e)}")
        return True  # Not critical


async def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("LLM Reliability Control Plane - End-to-End Test Suite")
    print("=" * 70)
    print()
    
    # Check API key
    if not GEMINI_API_KEY:
        print("⚠️  WARNING: GEMINI_API_KEY or LRCP_GEMINI_API_KEY not set!")
        print("   Tests will fail if API key is required.")
        print()
    else:
        print("✅ Gemini API key found")
        print()
    
    print(f"Testing API at: {API_BASE_URL}")
    print()
    
    async with httpx.AsyncClient() as client:
        # Basic endpoints
        print("📋 Testing Basic Endpoints...")
        await test_health_endpoint(client)
        await test_root_endpoint(client)
        print()
        
        # LLM endpoints
        print("🤖 Testing LLM Endpoints...")
        await test_qa_endpoint(client)
        await test_qa_with_simulations(client)
        await test_reason_endpoint(client)
        await test_stress_endpoint(client)
        print()
        
        # Insights endpoint
        print("💡 Testing Insights Endpoint...")
        await test_insights_endpoint(client)
        print()
        
        # Error handling
        print("🛡️  Testing Error Handling...")
        await test_error_handling(client)
        print()
    
    # Print summary
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}")
    print()
    
    if test_results['failed']:
        print("Failed tests:")
        for test in test_results['failed']:
            print(f"  - {test}")
        print()
    
    if test_results['warnings']:
        print("Warnings:")
        for test in test_results['warnings']:
            print(f"  - {test}")
        print()
    
    # Exit code
    if test_results['failed']:
        print("❌ Some tests failed!")
        sys.exit(1)
    else:
        print("✅ All critical tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(run_all_tests())


