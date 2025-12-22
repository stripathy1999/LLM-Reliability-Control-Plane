from __future__ import annotations

import os

from fastapi import FastAPI

# Datadog APM auto-instrumentation - MUST be imported before FastAPI
# This enables distributed tracing, automatic span creation, and trace correlation
if os.getenv("DD_TRACE_ENABLED", "true").lower() == "true":
    try:
        import ddtrace
        from ddtrace import patch_all

        # Initialize Datadog APM
        ddtrace.tracer.configure(
            hostname=os.getenv("DD_AGENT_HOST", "localhost"),
            port=int(os.getenv("DD_TRACE_AGENT_PORT", "8126")),
        )
        # Auto-instrument all supported libraries (FastAPI, httpx, etc.)
        patch_all()
    except ImportError:
        pass  # ddtrace not installed, continue without APM

from .config import settings
from .routes import qa, reason, stress

app = FastAPI(
    title=settings.project_name,
    version=settings.datadog_version,
)

app.include_router(qa.router)
app.include_router(reason.router)
app.include_router(stress.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "LLM Reliability Control Plane – see /docs for API schema."}


