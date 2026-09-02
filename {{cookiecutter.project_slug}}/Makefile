.PHONY: install dev test openapi docker-build up down{% if cookiecutter.database != "none" %} migrate revision{% endif %}

install:
	uv sync

dev:
	uv run python -m app

test:
	uv run pytest

openapi:
	uv run python scripts/export_openapi.py

docker-build:
	docker build -t {{ cookiecutter.project_slug }}:local --build-arg APP_VERSION=local .

up:
	docker compose up --build

down:
	docker compose down -v
{%- if cookiecutter.database != "none" %}

migrate:
	uv run alembic upgrade head

revision:
	uv run alembic revision --autogenerate -m "$(m)"
{%- endif %}
