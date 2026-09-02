"""Process entrypoint (`python -m app`): apply pending migrations, then serve."""

import uvicorn

from .config import get_settings
{%- if cookiecutter.database != "none" %}
from .db import run_migrations
{%- endif %}

if __name__ == "__main__":
    settings = get_settings()
{%- if cookiecutter.database != "none" %}
    # fail fast: a task that cannot migrate must not serve traffic
    run_migrations()
{%- endif %}
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, log_level=settings.log_level.lower())
