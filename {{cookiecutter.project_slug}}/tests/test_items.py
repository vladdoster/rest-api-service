from fastapi.testclient import TestClient

from app.config import get_settings

ITEMS = f"{get_settings().api_prefix}/items"


def test_create_then_read_item(client: TestClient) -> None:
    created = client.post(ITEMS, json={"name": "widget", "description": "round"})
    assert created.status_code == 201
    body = created.json()
    assert body["name"] == "widget"
    assert body["description"] == "round"

    fetched = client.get(f"{ITEMS}/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body


def test_list_items_starts_empty_for_each_test(client: TestClient) -> None:
    # proves the per-test rollback: rows from other tests never leak in
    assert client.get(ITEMS).json() == []
    client.post(ITEMS, json={"name": "a"})
    client.post(ITEMS, json={"name": "b"})
    assert [item["name"] for item in client.get(ITEMS).json()] == ["a", "b"]


def test_read_missing_item_is_404(client: TestClient) -> None:
    assert client.get(f"{ITEMS}/999999").status_code == 404


def test_create_item_rejects_empty_name(client: TestClient) -> None:
    assert client.post(ITEMS, json={"name": ""}).status_code == 422
