try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = "LLM Reliability Control Plane"
    environment: str = "local"

    # LLM / Gemini API
    gemini_model: str = "gemini-2.5-flash"  # Updated to valid model name
    gemini_api_key: str | None = None

    # Datadog (used later in instrumentation phase)
    datadog_api_key: str | None = None
    datadog_env: str = "local"
    datadog_service: str = "llm-reliability-control-plane"
    datadog_version: str = "0.1.0"

    # Google Cloud Vertex AI
    gcp_project_id: str | None = None
    gcp_region: str = "us-central1"
    vertex_ai_cost_endpoint: str | None = None
    vertex_ai_quality_endpoint: str | None = None
    vertex_ai_anomaly_endpoint: str | None = None
    vertex_ai_router_endpoint: str | None = None

    class Config:
        env_prefix = "LRCP_"
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from environment


settings = Settings()


