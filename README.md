# rest-api-service

Cookiecutter template for REST API services on the platform (`vladdoster/platform-infra`).
REST-only sibling of `service-gen`: same conventions, no frontend option.

Generates a GitHub-ready service repo containing:

- FastAPI backend: Python 3.13, uv, pydantic v2, pytest; OpenAPI docs served
  under the ingress prefix in dev, exportable with `make openapi`.
- Optional database layer: SQLAlchemy 2 + alembic wired to the platform's
  injected `DB_*` variables, an example `Item` model with its initial migration
  and `/items` CRUD router, migrations applied automatically at container
  start, and tests that run against a throwaway Postgres 17 (testcontainers).
- `Dockerfile`, `docker-compose.yml`, `Makefile`, fully documented `service.yaml`.
- GitHub workflows calling the platform's reusable `service-deploy.yml@main`
  and `service-release.yml@main` (test on PR, deploy on push to main,
  releases via reno).
- A first signed-off commit on `main` (`chore: scaffold <slug>`), made by the
  post-generation hook when `git` is available.

Requires cookiecutter >= 2.6.

## Usage

```sh
uvx cookiecutter /path/to/rest-api-service
# or, once this repo is pushed:
uvx cookiecutter gh:vladdoster/rest-api-service
```

## Variables

| Variable | Default | Purpose |
|---|---|---|
| `project_slug` | `my-new-service` | Service, repo, and `service.yaml` name (lowercase alphanumerics joined by single hyphens, max 40 chars) |
| `project_description` | ... | One-liner used in README and pyproject |
| `github_org` | `vladdoster` | Org hosting platform-infra and this service |
| `domain` | `vdoster.com` | Platform apex domain |
| `path_prefix` | `/<slug>` | Ingress path prefix (`/orders`); independent of the name |
| `port` | `8080` | Container port |
| `cpu` / `memory` | `256` / `512` | Fargate task size; the pair is checked against the sizes ECS accepts |
| `scaling_min` / `scaling_max` | `1` / `4` | Task count bounds |
| `database` | `none` | `none`, `shared`, or `dedicated`; non-none adds SQLAlchemy + alembic + the `Item` example + compose Postgres + testcontainers tests |
| `deploy_environments` | `dev` | `dev` or `dev-staging-prod` promotion pipeline |

Fields not prompted for (`secrets`, `allowedClients`, `spot`, `architecture`,
`ingress.priority`, `executeCommand`, `compute`) are emitted in the generated
`service.yaml` as commented reference blocks. `compute: lambda` and static
frontends are out of scope; use `service-gen` for a service with a frontend.

## Development

```sh
make install   # uv sync
make test      # bake-matrix tests (pytest-cookies); needs git on PATH
make smoke     # bake both variants and run their own test suites; needs Docker for the database variant
```

Generated repos intentionally omit `VERSION`, `CHANGELOG.md`, lockfiles, and
`openapi.json`: the release pipeline writes the first two, `make install`
creates the lockfile, and `make openapi` derives the schema.
