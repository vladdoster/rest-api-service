# rest-api-service

Cookiecutter template for REST API services on the platform (`Starwake-Prototypes/platform-infra`),
the REST-only sibling of `service-gen`: same conventions, no frontend option.

It generates a GitHub-ready service repo that contains:

- FastAPI backend: Python 3.13, uv, pydantic v2, pytest. In dev, the service serves
  OpenAPI docs under the ingress prefix, and `make openapi` exports them.
- Optional database layer: SQLAlchemy 2 and alembic wired to the platform's
  injected `DB_*` variables, with an example `Item` model, its initial migration,
  and a `/items` CRUD router. The container applies migrations at start, and
  tests run against a throwaway Postgres 17 (testcontainers).
- `Dockerfile`, `docker-compose.yml`, `Makefile`, and a fully documented `service.yaml`.
- GitHub workflows that call the platform's reusable `service-deploy.yml@main`
  and `service-release.yml@main` (test on PR, deploy on push to main,
  releases via reno).
- A first signed-off commit on `main` (`chore: scaffold <slug>`). The
  post-generation hook makes it when `git` is available.

Requires cookiecutter >= 2.6.

## Usage

```sh
uvx cookiecutter /path/to/rest-api-service
# or, once this repo is pushed:
uvx cookiecutter gh:Starwake-Prototypes/rest-api-service
```

## Variables

| Variable | Default | Purpose |
|---|---|---|
| `project_slug` | `my-new-service` | Service, repo, and `service.yaml` name (lowercase alphanumerics joined by single hyphens, max 40 chars) |
| `project_description` | ... | One-liner used in README and pyproject |
| `path_prefix` | `/<slug>` | Ingress path prefix (`/orders`). Independent of the name |
| `port` | `8080` | Container port |
| `cpu` / `memory` | `256` / `512` | Fargate task size. The hook checks the pair against the sizes ECS accepts |
| `scaling_min` / `scaling_max` | `1` / `4` | Task count bounds |
| `database` | `none` | `none`, `shared`, or `dedicated`. A non-none value adds SQLAlchemy, alembic, the `Item` example, compose Postgres, and testcontainers tests |
| `deploy_environments` | `dev` | `dev` or `dev-staging-prod` promotion pipeline |

The template does not prompt for `secrets`, `allowedClients`, `spot`, `architecture`,
`ingress.priority`, or `executeCommand`, but emits them in the generated
`service.yaml` as commented reference blocks. The GitHub org is fixed to
`Starwake-Prototypes`. Generated workflows call that org's `platform-infra`
reusable workflows. Static frontends are out of scope. Use `service-gen` for a
service with a frontend.

## Development

```sh
make install   # uv sync
make test      # bake-matrix tests (pytest-cookies); needs git on PATH
make smoke     # bake both variants and run their own test suites; needs Docker for the database variant
```

Generated repos intentionally omit `VERSION`, `CHANGELOG.md`, lockfiles, and
`openapi.json`. The release pipeline writes the first two, `make install`
creates the lockfile, and `make openapi` derives the schema.
