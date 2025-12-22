import asyncio
import random
from typing import Literal

import httpx


BASE_URL = "http://localhost:8000"


async def send_qa(client: httpx.AsyncClient, phase: str) -> None:
    params = {}
    if phase == "quality_drop":
        params["simulate_bad_prompt"] = "true"
    body = {
        "question": "What is Datadog?",
        "document": "Datadog is an observability platform for logs, metrics, traces, and more.",
    }
    await client.post(f"{BASE_URL}/qa", json=body, params=params)


async def send_reason(client: httpx.AsyncClient, phase: str) -> None:
    params = {}
    if phase == "latency_spike":
        params["simulate_latency"] = "true"
        params["simulate_retry"] = "true"
    body = {"prompt": "Explain the golden signals of SRE and why they matter for LLMs."}
    await client.post(f"{BASE_URL}/reason", json=body, params=params)


async def send_stress(client: httpx.AsyncClient, phase: str) -> None:
    params = {}
    repetitions = 5
    if phase == "cost_spike":
        params["simulate_long_context"] = "true"
        repetitions = 40
    body = {
        "prompt": "Summarize the last 100 production incidents and propose improvements.",
        "repetitions": repetitions,
    }
    await client.post(f"{BASE_URL}/stress", json=body, params=params)


async def run_phase(client: httpx.AsyncClient, phase: Literal["normal", "cost_spike", "quality_drop", "latency_spike"]) -> None:
    tasks = []
    for _ in range(20):
        choice = random.choice(["qa", "reason", "stress"])
        if choice == "qa":
            tasks.append(send_qa(client, phase))
        elif choice == "reason":
            tasks.append(send_reason(client, phase))
        else:
            tasks.append(send_stress(client, phase))
    await asyncio.gather(*tasks)


async def get_insights(client: httpx.AsyncClient) -> None:
    """Demonstrate AI-powered insights endpoint."""
    print("\n🔍 Fetching AI-powered insights...")
    insights_body = {
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
        "error_trend": "stable",
    }
    try:
        response = await client.post(f"{BASE_URL}/insights", json=insights_body)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Score: {data['health_summary']['overall_health_score']}/100")
            print(f"   Status: {data['health_summary']['status']}")
            print(f"   Top Priority Actions: {len(data['priority_actions'])} recommendations")
            print(f"   Predictive Insights: {len(data['predictive_insights'])} alerts")
    except Exception as e:
        print(f"⚠️  Insights endpoint not available: {e}")


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        print("=" * 60)
        print("LLM Reliability Control Plane - Traffic Generator")
        print("Demonstrating detection rules and AI-powered insights")
        print("=" * 60)
        
        print("\nPhase 1: Normal traffic")
        await run_phase(client, "normal")
        await asyncio.sleep(10)
        await get_insights(client)

        print("\nPhase 2: Cost spike via long prompts")
        await run_phase(client, "cost_spike")
        await asyncio.sleep(10)
        await get_insights(client)

        print("\nPhase 3: Bad prompts causing safety blocks / quality issues")
        await run_phase(client, "quality_drop")
        await asyncio.sleep(10)
        await get_insights(client)

        print("\nPhase 4: Latency and retry spike")
        await run_phase(client, "latency_spike")
        await asyncio.sleep(10)
        await get_insights(client)
        
        print("\n" + "=" * 60)
        print("Traffic generation complete!")
        print("Check Datadog for:")
        print("  - Health score metrics")
        print("  - Triggered monitors")
        print("  - Auto-created incidents")
        print("  - AI-powered insights")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


