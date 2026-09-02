# {{ cookiecutter.project_slug }}

{{ cookiecutter.project_description }} Runs on the platform (see `{{ cookiecutter.github_org }}/platform-infra`).

- API: `https://api.dev.{{ cookiecutter.domain }}{{ cookiecutter.path_prefix }}/...`
- Interactive docs (dev only): `https://api.dev.{{ cookiecutter.domain }}{{ cookiecutter.path_prefix }}/docs`
- Health check: `GET /health`
{%- if cookiecutter.database != "none" %}
- Example resource: `POST/GET {{ cookiecutter.path_prefix }}/items`, `GET {{ cookiecutter.path_prefix }}/items/{id}`
  (`app/routers/items.py`, `app/models.py`, `app/schemas.py`); replace it with your own.
- Database: `{{ cookiecutter.database }}`; the platform injects `DB_HOST`, `DB_PORT`, `DB_NAME`,
  `DB_USER`, `DB_PASSWORD`. The container runs `alembic upgrade head` before serving
  (`app/__main__.py`), under an advisory lock so tasks that start together do not race.
  Keep migrations short and additive: during a rolling deploy old tasks still run against the new schema.
{%- endif %}
- Tests run on every PR (`test` workflow); deploys on push to `main` via GitHub
  OIDC (no stored AWS keys); the image is built once, pushed to the dev ECR
  registry, and deployed by the platform's reusable workflow.
- Releases: run the `release` workflow (Actions tab) to cut `vX.Y.Z`, the
  changelog, and a GitHub Release; write a reno note with every change
  (`uvx reno new <slug>`). Never create `VERSION` or `CHANGELOG.md` by hand.
  See `docs/releasing-a-service.md` in `{{ cookiecutter.github_org }}/platform-infra`.
- Compute: Fargate. `compute: lambda` is not covered by this scaffold; write
  `service.yaml` by hand per the platform docs if you need it.

## Local development

```sh
make install       # uv sync
make dev           # serve on :{{ cookiecutter.port }}{% if cookiecutter.database != "none" %} (migrates first; start postgres with `docker compose up postgres`){% endif %}
make test          # pytest{% if cookiecutter.database != "none" %}; needs Docker (testcontainers starts Postgres 17){% endif %}
make openapi       # write openapi.json (gitignored, derived)
make up            # docker compose: api{% if cookiecutter.database != "none" %} + postgres{% endif %}
make down          # stop the stack, drop volumes
{%- if cookiecutter.database != "none" %}
make migrate       # alembic upgrade head without starting the server (uses DB_* env vars; compose defaults)
make revision m="add items"   # autogenerate a migration from app/models.py
{%- endif %}
```

## One-time setup

1. Register the service: PR adding `name: {{ cookiecutter.project_slug }}`,
   `repo: {{ cookiecutter.project_slug }}`, and `repoId` to `services.yaml` in
   `{{ cookiecutter.github_org }}/platform-infra`
   (`gh api repos/{{ cookiecutter.github_org }}/{{ cookiecutter.project_slug }} --jq .id`).
1. Run the `service-onboard` workflow in `{{ cookiecutter.github_org }}/platform-infra`
   for this repo and each environment: it creates the GitHub environment and
   installs the `AWS_ACCOUNT_ID_*`, `AWS_REGION`, and `PULUMI_STATE_BUCKET`
   variables plus the `PLATFORM_REPO_TOKEN` secret.
{%- if cookiecutter.deploy_environments == "dev-staging-prod" %}
1. Add required reviewers on the `prod` environment (repo Settings > Environments).
{%- endif %}
1. Run `make install` and commit `uv.lock` on top of the scaffold commit; CI installs with locked resolution.
1. Cut the first release via the `release` workflow; it creates `VERSION` and
   `CHANGELOG.md` (the pipeline stays their only writer).
