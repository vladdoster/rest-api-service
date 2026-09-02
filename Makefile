.PHONY: install test smoke

install:
	uv sync

test:
	uv run --module pytest

# bake both variants into a temp dir and run each project's own test suite;
# the database variant starts Postgres through testcontainers, so Docker must be running
smoke:
	@set -e; TMP=$$(mktemp -d); trap 'rm -rf "$$TMP"' EXIT; \
	uv run --module cookiecutter . --no-input -o "$$TMP/default"; \
	uv run --module cookiecutter . --no-input -o "$$TMP/full" \
		database=dedicated deploy_environments=dev-staging-prod; \
	(cd "$$TMP"/default/*/ && uv sync && uv run pytest); \
	(cd "$$TMP"/full/*/ && uv sync && uv run pytest); \
	echo "smoke OK"
