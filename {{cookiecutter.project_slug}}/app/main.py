from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .config import get_settings
{%- if cookiecutter.database != "none" %}
from .routers import items, root
{%- else %}
from .routers import root
{%- endif %}

settings = get_settings()
# docs are dev-only and live under the ingress prefix; the ALB forwards it unstripped
docs_enabled = settings.environment == "dev"

app = FastAPI(
    title=settings.service_name,
    version=settings.app_version,
    openapi_url=f"{settings.api_prefix}/openapi.json" if docs_enabled else None,
    docs_url=f"{settings.api_prefix}/docs" if docs_enabled else None,
    redoc_url=None,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version}


app.include_router(root.router, prefix=settings.api_prefix)
{%- if cookiecutter.database != "none" %}
app.include_router(items.router, prefix=settings.api_prefix)
{%- endif %}
