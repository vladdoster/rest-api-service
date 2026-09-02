FROM public.ecr.aws/docker/library/python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.12.7 /uv /uvx /usr/local/bin/

ARG APP_VERSION=unknown
ENV APP_VERSION=${APP_VERSION}
LABEL org.opencontainers.image.version=${APP_VERSION}

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_NO_CACHE=1 UV_PYTHON_DOWNLOADS=0
# dependency layer stays cached until the lockfile changes
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev
COPY app/ app/
{%- if cookiecutter.database != "none" %}
# `python -m app` runs `alembic upgrade head` before serving, so both must ship in the image
COPY alembic.ini ./
COPY migrations/ migrations/
{%- endif %}

ENV PATH="/app/.venv/bin:$PATH"
# /app is root-owned and the process runs as nobody: skip the __pycache__ write attempts
ENV PYTHONDONTWRITEBYTECODE=1
EXPOSE {{ cookiecutter.port }}
USER nobody
CMD ["python", "-m", "app"]
