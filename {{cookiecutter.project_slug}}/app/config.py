"""Application settings, created once via get_settings (FastAPI settings pattern)."""
import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _platform_environment() -> str:
    """Derive dev/staging/prod from the OTEL resource attributes the platform injects."""
    attributes = os.environ.get("OTEL_RESOURCE_ATTRIBUTES")
    if attributes is None:
        return "dev"
    for item in attributes.split(","):
        key, _, value = item.partition("=")
        if key.strip() == "deployment.environment" and value.strip():
            return value.strip()
    # deployed but unlabelled: never fall back to dev, which would expose the docs
    return "unknown"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    service_name: str = Field("{{ cookiecutter.project_slug }}", validation_alias="OTEL_SERVICE_NAME")
    app_version: str = "unknown"
    # an explicit ENVIRONMENT variable wins over the platform-derived default
    environment: str = Field(default_factory=_platform_environment)
    api_prefix: str = "{{ cookiecutter.path_prefix }}"
    port: int = {{ cookiecutter.port }}
    # set through service.yaml env; uvicorn accepts critical/error/warning/info/debug/trace
    log_level: str = "info"
    # "*" keeps ALB health checks passing; tighten via ALLOWED_HOSTS in service.yaml env
    allowed_hosts: list[str] = ["*"]
{%- if cookiecutter.database != "none" %}
    # deployed values come from the platform's DB_* variables; defaults match docker-compose.yml
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "{{ cookiecutter.project_slug.replace('-', '_') }}"
    db_user: str = "postgres"
    db_password: str = "postgres"
{%- endif %}


@lru_cache
def get_settings() -> Settings:
    return Settings()
