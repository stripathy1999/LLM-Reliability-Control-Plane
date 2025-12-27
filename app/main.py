from __future__ import annotations

import os
import sys
from pathlib import Path

# Startup logging
print("=" * 60, file=sys.stderr)
print("Starting LLM Reliability Control Plane", file=sys.stderr)
print(f"Python version: {sys.version}", file=sys.stderr)
print(f"Working directory: {os.getcwd()}", file=sys.stderr)
print("=" * 60, file=sys.stderr)

# Datadog APM auto-instrumentation - MUST be imported before FastAPI
# This enables distributed tracing, automatic span creation, and trace correlation
if os.getenv("DD_TRACE_ENABLED", "true").lower() == "true":
    try:
        import ddtrace
        from ddtrace import patch_all

        # For Cloud Run agentless mode, ddtrace uses environment variables automatically
        # Set DD_AGENT_HOST and DD_TRACE_AGENT_PORT via environment variables
        # For agentless mode (Cloud Run), leave DD_AGENT_HOST empty or unset
        
        # Auto-instrument all supported libraries (FastAPI, httpx, etc.)
        patch_all()
        print("Datadog APM initialized successfully", file=sys.stderr)
        
        # Configure tracer settings (if needed for agentless mode, this is handled via env vars)
        # For Cloud Run with agentless mode, DD_LLMOBS_AGENTLESS_ENABLED=1 handles this
    except ImportError:
        print("Warning: ddtrace not installed, continuing without APM", file=sys.stderr)
        pass  # ddtrace not installed, continue without APM
    except Exception as e:
        # Log but don't fail startup if Datadog config has issues
        print(f"Warning: Datadog APM initialization had issues: {e}", file=sys.stderr)
        pass

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from .config import settings
from .routes import insights, qa, reason, stress, streaming, incidents, optimization, datadog_integrations

app = FastAPI(
    title=settings.project_name,
    version=settings.datadog_version,
    description="""
    # 🚀 LLM Reliability Control Plane
    
    A comprehensive observability and reliability platform for Large Language Model (LLM) applications, 
    built for the Datadog Hackathon. This API provides real-time monitoring, AI-powered insights, and 
    automated failure detection for LLM workloads.
    
    ## 🎯 Key Features
    
    - **🎯 Composite Health Score (0-100)**: Single metric combining performance, reliability, cost, quality, and security
    - **💡 AI-Powered Cost Optimization**: Intelligent recommendations with estimated savings
    - **🔮 Predictive Anomaly Detection**: Forecasts issues before they happen
    - **🛡️ Automated Security Recommendations**: Detects attacks and suggests remediation
    - **📊 Real-time Quality Analysis**: Semantic similarity and hallucination detection
    - **🔍 Comprehensive Observability**: Full integration with Datadog APM, metrics, logs, and traces
    
    ## 📚 API Endpoints
    
    ### Core LLM Endpoints
    - **`POST /qa`**: Question & Answer over documents (quality degradation detection)
    - **`POST /reason`**: Reasoning-style prompts (latency and retry behavior)
    - **`POST /stress`**: High-token requests (cost and token explosion scenarios)
    
    ### Observability Endpoints
    - **`POST /insights`**: AI-powered system health analysis and recommendations
    - **`GET /health`**: Health check endpoint
    
    ## 🧪 Testing Failure Scenarios
    
    All LLM endpoints support query parameters to simulate failure scenarios:
    
    - `?simulate_latency=true` - Simulates high latency (triggers latency SLO monitor)
    - `?simulate_retry=true` - Simulates retry behavior (triggers error burst monitor)
    - `?simulate_bad_prompt=true` - Simulates safety blocks (triggers security monitor)
    - `?simulate_long_context=true` - Simulates context explosion (triggers cost anomaly monitor)
    
    ## 📖 Getting Started
    
    1. **Test an endpoint**: Click on any endpoint below, then click "Try it out"
    2. **Use examples**: Each endpoint includes example request bodies
    3. **View responses**: See detailed metadata including tokens, cost, latency, and quality scores
    4. **Trigger failures**: Add query parameters to simulate production incidents
    
    ## 🔗 Related Resources
    
    - **Failure Theater UI**: http://localhost:3000 (one-click failure scenarios)
    - **Datadog Dashboard**: View metrics, traces, and incidents in your Datadog account
    - **ReDoc Documentation**: http://127.0.0.1:8000/redoc (alternative API documentation)
    """,
    terms_of_service="https://example.com/terms/",
    contact={
        "name": "LLM Reliability Control Plane",
        "url": "https://github.com/your-repo",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    tags_metadata=[
        {
            "name": "qa",
            "description": """
            **Question & Answer Endpoint**
            
            Performs Q&A over small static documents. This endpoint is primarily used for 
            **quality degradation detection** through semantic similarity scoring.
            
            **Use Cases:**
            - Document-based Q&A
            - Quality assurance testing
            - Semantic similarity validation
            
            **Metrics Tracked:**
            - Quality scores (semantic similarity)
            - Ungrounded answer detection
            - Response relevance
            """,
        },
        {
            "name": "reason",
            "description": """
            **Reasoning Endpoint**
            
            Handles reasoning-style prompts that require complex thinking. Used to observe 
            **latency** and **retry** behavior patterns.
            
            **Use Cases:**
            - Complex reasoning tasks
            - Multi-step problem solving
            - Latency monitoring
            
            **Metrics Tracked:**
            - Request latency (p50, p95, p99)
            - Retry counts
            - Timeout rates
            """,
        },
        {
            "name": "stress",
            "description": """
            **Stress Testing Endpoint**
            
            Generates long-context, high-token requests to trigger **token & cost explosions**. 
            Perfect for testing cost anomaly detection and token abuse monitoring.
            
            **Use Cases:**
            - Cost anomaly testing
            - Token usage monitoring
            - Context window stress testing
            
            **Metrics Tracked:**
            - Token counts (input/output)
            - Cost per request
            - Context length
            """,
        },
        {
            "name": "insights",
            "description": """
            **AI-Powered Insights Endpoint**
            
            Provides comprehensive AI analysis of system health, cost optimization opportunities, 
            predictive alerts, and automated remediation suggestions.
            
            **Features:**
            - Composite health score calculation
            - Cost optimization recommendations
            - Predictive anomaly detection
            - Security recommendations
            - Quality improvement suggestions
            
            **Returns:**
            - Health summary with component scores
            - Prioritized recommendations
            - Predictive insights
            - Top 5 priority actions
            """,
        },
        {
            "name": "health",
            "description": "Health check and system status endpoints",
        },
    ],
)

# Include routers with error handling
try:
    app.include_router(qa.router)
    app.include_router(reason.router)
    app.include_router(stress.router)
    app.include_router(insights.router)
    app.include_router(streaming.router)
    app.include_router(incidents.router)
    app.include_router(optimization.router)
    app.include_router(datadog_integrations.router)
    print("All routes loaded successfully", file=sys.stderr)
except Exception as e:
    print(f"Warning: Some routes failed to load: {e}", file=sys.stderr)
    # Continue anyway - at least health endpoint will work

print("FastAPI app initialized successfully", file=sys.stderr)

# Mount static files for custom Swagger UI assets
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get(
    "/health",
    tags=["health"],
    summary="Health Check",
    description="""
    Simple health check endpoint to verify the API is running.
    
    **Returns:**
    - `status: "ok"` if the service is healthy
    
    **Use Cases:**
    - Load balancer health checks
    - Monitoring system probes
    - Service discovery
    """,
    response_description="Service health status",
)
async def health() -> dict[str, str]:
    """
    Health check endpoint.
    
    Returns a simple status indicator to verify the API is operational.
    """
    return {"status": "ok"}


@app.get(
    "/",
    tags=["health"],
    summary="Root Endpoint",
    description="Root endpoint with API information and links to documentation.",
    response_description="Welcome message with API information",
)
async def root() -> dict[str, str]:
    """
    Root endpoint providing API information.
    """
    return {"message": "LLM Reliability Control Plane – see /docs for API schema."}


def custom_openapi():
    """Custom OpenAPI schema with enhanced documentation."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom styling and branding
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Add custom extensions for enhanced UI
    openapi_schema["info"]["x-tagGroups"] = [
        {
            "name": "Core LLM Endpoints",
            "tags": ["qa", "reason", "stress"]
        },
        {
            "name": "Observability",
            "tags": ["insights", "health"]
        }
    ]
    
    # Add more examples to schema
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    if "examples" not in openapi_schema["components"]:
        openapi_schema["components"]["examples"] = {}
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    """Custom Swagger UI with enhanced styling and interactivity."""
    from fastapi.openapi.docs import get_swagger_ui_html
    
    html_response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Enhanced API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        init_oauth=app.swagger_ui_init_oauth,
    )
    
    # Inject custom CSS and JS
    css_file = static_dir / "swagger-ui-custom.css"
    js_file = static_dir / "swagger-ui-custom.js"
    
    # Get the HTML content
    html_content = html_response.body.decode('utf-8')
    
    # Inject custom CSS before closing head tag
    if css_file.exists():
        html_content = html_content.replace('</head>', 
            f'<link rel="stylesheet" type="text/css" href="/static/swagger-ui-custom.css" />\n</head>')
    
    # Inject custom JS before closing body tag
    if js_file.exists():
        html_content = html_content.replace('</body>', 
            f'<script src="/static/swagger-ui-custom.js"></script>\n</body>')
    
    return HTMLResponse(content=html_content)


