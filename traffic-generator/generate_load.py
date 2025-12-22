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


async def main() -> None:
    async with httpx.AsyncClient(timeout=30) as client:
        print("Phase 1: normal traffic")
        await run_phase(client, "normal")
        await asyncio.sleep(10)

        print("Phase 2: cost spike via long prompts")
        await run_phase(client, "cost_spike")
        await asyncio.sleep(10)

        print("Phase 3: bad prompts causing safety blocks / quality issues")
        await run_phase(client, "quality_drop")
        await asyncio.sleep(10)

        print("Phase 4: latency and retry spike")
        await run_phase(client, "latency_spike")


if __name__ == "__main__":
    asyncio.run(main())


