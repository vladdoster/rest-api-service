from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)
settings = get_settings()


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_under_ingress_prefix() -> None:
    response = client.get(f"{settings.api_prefix}/")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "hello"
    assert body["service"] == settings.service_name


def test_docs_enabled_in_dev() -> None:
    assert settings.environment == "dev", "unset ENVIRONMENT (and .env) to run the docs test"
    assert client.get(f"{settings.api_prefix}/docs").status_code == 200
