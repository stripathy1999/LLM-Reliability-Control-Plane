from pydantic import BaseSettings


class Settings(BaseSettings):
    project_name: str = "LLM Reliability Control Plane"
    environment: str = "local"

    # LLM / Vertex AI
    gemini_model: str = "gemini-1.5-pro"
    vertex_project_id: str = "your-gcp-project-id"
    vertex_location: str = "us-central1"

    # Datadog (used later in instrumentation phase)
    datadog_api_key: str | None = None
    datadog_env: str = "local"
    datadog_service: str = "llm-reliability-control-plane"
    datadog_version: str = "0.1.0"

    class Config:
        env_prefix = "LRCP_"
        env_file = ".env"


settings = Settings()


