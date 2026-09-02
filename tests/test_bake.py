"""Bake-matrix tests: both variants render, YAML parses, no Jinja leaks, one scaffold commit."""

import os
import subprocess
from pathlib import Path

import pytest
import yaml

FULL_CONTEXT = {"database": "dedicated", "deploy_environments": "dev-staging-prod"}
# mirrors DB_ONLY in hooks/post_gen_project.py, expanded to files so presence can be asserted
DB_ONLY = (
    "alembic.ini",
    "migrations/env.py",
    "migrations/script.py.mako",
    "migrations/versions/9f3c2a1b7e4d_create_items.py",
    "app/db.py",
    "app/models.py",
    "app/schemas.py",
    "app/routers/items.py",
    "tests/conftest.py",
    "tests/test_items.py",
)


@pytest.fixture(autouse=True)
def git_identity(monkeypatch):
    """Hermetic git for the hook's commit: fixed identity, no user/system config (signing, hooks)."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for key in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
        monkeypatch.setenv(key, "Bake Test")
    for key in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        monkeypatch.setenv(key, "bake@example.com")


def git(project: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(project), *args], check=True, capture_output=True, text=True).stdout.strip()


def read(project: Path, relative: str) -> str:
    return (project / relative).read_text()


def workflow_texts(project: Path) -> dict[str, str]:
    return {p.name: p.read_text() for p in (project / ".github" / "workflows").glob("*.yml")}


def assert_fully_rendered(text: str, name: str) -> None:
    assert "{%" not in text, name
    assert "{{ cookiecutter" not in text, name


def assert_scaffold_commit(project: Path, slug: str) -> None:
    assert git(project, "rev-list", "--count", "HEAD") == "1"
    assert git(project, "branch", "--show-current") == "main"
    assert git(project, "status", "--porcelain") == "", "hook deletions must land before the commit"
    message = git(project, "log", "-1", "--format=%B")
    assert message.splitlines()[0] == f"chore: scaffold {slug}"
    assert "Signed-off-by: Bake Test <bake@example.com>" in message
    assert "co-authored-by" not in message.lower()


def assert_common(project: Path, slug: str) -> None:
    for name, text in workflow_texts(project).items():
        assert_fully_rendered(text, name)
        yaml.safe_load(text)
    for path in project.rglob("*.py"):
        assert_fully_rendered(path.read_text(), str(path.relative_to(project)))
    for missing in ("frontend", "VERSION", "CHANGELOG.md", "openapi.json", "uv.lock"):
        assert not (project / missing).exists(), missing
    assert "frontend" not in yaml.safe_load(read(project, "service.yaml"))
    assert "frontend_artifact" not in read(project, ".github/workflows/deploy.yml")
    assert_scaffold_commit(project, slug)


def test_default_bake(cookies):
    result = cookies.bake()
    assert result.exit_code == 0
    project = result.project_path
    assert_common(project, "my-new-service")
    for missing in (*DB_ONLY, "migrations"):
        assert not (project / missing).exists(), missing
    assert (project / ".dockerignore").exists()
    spec = yaml.safe_load(read(project, "service.yaml"))
    assert spec["name"] == "my-new-service"
    assert spec["database"] == "none"
    assert spec["ingress"]["pathPrefix"] == "/my-new-service"
    assert "deploy-staging" not in read(project, ".github/workflows/deploy.yml")
    compose = yaml.safe_load(read(project, "docker-compose.yml"))
    assert "postgres" not in compose["services"]
    pyproject = read(project, "pyproject.toml")
    assert "alembic" not in pyproject
    assert "testcontainers" not in pyproject
    assert "items" not in read(project, "app/main.py")
    assert "run_migrations" not in read(project, "app/__main__.py")
    assert "alembic" not in read(project, "Dockerfile")
    assert "migrations" not in read(project, ".dockerignore")


@pytest.mark.parametrize("database", ["shared", "dedicated"])
def test_database_bake(cookies, database):
    result = cookies.bake(extra_context={**FULL_CONTEXT, "database": database})
    assert result.exit_code == 0
    project = result.project_path
    assert_common(project, "my-new-service")
    for present in DB_ONLY:
        assert (project / present).exists(), present
    assert not (project / "migrations" / "versions" / ".gitkeep").exists()
    # without this, `alembic` cannot import the app package (env.py imports app.db)
    assert "prepend_sys_path = ." in read(project, "alembic.ini")
    spec = yaml.safe_load(read(project, "service.yaml"))
    assert spec["database"] == database
    compose = yaml.safe_load(read(project, "docker-compose.yml"))
    assert "postgres" in compose["services"]
    pyproject = read(project, "pyproject.toml")
    assert "alembic" in pyproject
    assert "testcontainers" in pyproject
    dockerfile = read(project, "Dockerfile")
    assert "COPY alembic.ini ./" in dockerfile
    assert "COPY migrations/ migrations/" in dockerfile
    dockerignore = read(project, ".dockerignore")
    assert "!alembic.ini" in dockerignore
    assert "!migrations" in dockerignore
    assert "run_migrations" in read(project, "app/__main__.py")
    assert "items.router" in read(project, "app/main.py")
    deploy = read(project, ".github/workflows/deploy.yml")
    assert "deploy-staging" in deploy
    assert "deploy-prod" in deploy
    assert deploy.count("service-deploy.yml@main") == 3
    # testcontainers starts its own Postgres; a GitHub service container would be redundant
    assert "services:" not in read(project, ".github/workflows/test.yml")


def test_bake_without_git_warns(cookies, monkeypatch, tmp_path, capfd):
    # hooks run under sys.executable, so an empty PATH only hides git
    monkeypatch.setenv("PATH", str(tmp_path))
    result = cookies.bake()
    assert result.exit_code == 0
    assert not (result.project_path / ".git").exists()
    assert "WARNING: git not found" in capfd.readouterr().out


@pytest.mark.parametrize(
    "context",
    [
        {"project_slug": "My_Service"},
        {"project_slug": "escrow-"},
        {"project_slug": "es--crow"},
        {"path_prefix": "escrow"},
        {"path_prefix": "/escrow/"},
        {"path_prefix": "/"},
        {"scaling_min": 5, "scaling_max": 2},
        {"port": "http"},
        {"cpu": "999"},
        {"memory": "4096"},
    ],
)
def test_invalid_input_fails(cookies, context):
    result = cookies.bake(extra_context=context)
    assert result.exit_code != 0
