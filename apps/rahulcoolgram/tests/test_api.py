import json

import httpx
import pytest
from fastapi.testclient import TestClient

import main
from settings import settings

KEY = {"X-RahulCoolGram-Key": "dev-secret"}


class FakeOmnichannelAPI:
    """Stands in for our omnichannel API: records what RahulCoolGram forwards to it."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.down = False

    def handle(self, request: httpx.Request) -> httpx.Response:
        if self.down:
            raise httpx.ConnectError("connection refused")
        self.requests.append(request)
        return httpx.Response(200)


@pytest.fixture
def omnichannel(monkeypatch):
    fake = FakeOmnichannelAPI()

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        main.httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(fake.handle), **kwargs),
    )
    return fake


@pytest.fixture
def client(tmp_path, monkeypatch, omnichannel):
    monkeypatch.setattr(settings, "database_path", str(tmp_path / "test.db"))
    monkeypatch.setattr(settings, "rahulcoolgram_api_key", "dev-secret")
    with TestClient(main.app) as test_client:  # "with" runs startup, which creates the DB
        yield test_client


def test_home_page_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "RahulCoolGram" in response.text


def test_lists_seeded_customers(client):
    customers = client.get("/api/customers").json()
    assert len(customers) == 5
    assert customers[0] == {
        "id": "sujan",
        "name": "Sujan Maharjan",
        "username": "sujan.mhj",
        "avatar": "/static/avatars/sujan.svg",
    }


def test_customer_message_is_saved_and_forwarded(client, omnichannel):
    response = client.post("/api/customers/bikash/messages", json={"text": "dai yo kati ho?"})
    assert response.status_code == 201
    message = response.json()
    assert message["sender"] == "customer"

    history = client.get("/api/customers/bikash/messages").json()
    assert len(history) == 1
    assert history[0]["text"] == "dai yo kati ho?"

    [request] = omnichannel.requests
    assert str(request.url) == settings.omnichannel_webhook_url
    assert request.headers["X-RahulCoolGram-Key"] == "dev-secret"
    assert json.loads(request.content) == {
        "message_id": message["id"],
        "customer": {"id": "bikash", "name": "Bikash Thapa", "username": "bikash_thapa"},
        "text": "dai yo kati ho?",
        "sent_at": message["sent_at"],
    }


def test_message_is_kept_when_omnichannel_api_is_down(client, omnichannel):
    omnichannel.down = True
    response = client.post("/api/customers/sujan/messages", json={"text": "hello?"})
    assert response.status_code == 201
    assert len(client.get("/api/customers/sujan/messages").json()) == 1


def test_store_reply_shows_up_in_the_chat(client):
    response = client.post(
        "/api/store/messages", json={"customer_id": "sujan", "text": "Namaste!"}, headers=KEY
    )
    assert response.status_code == 201
    message_id = response.json()["message_id"]

    [message] = client.get("/api/customers/sujan/messages").json()
    assert message["id"] == message_id
    assert message["sender"] == "store"
    assert message["text"] == "Namaste!"


def test_store_reply_needs_the_right_key(client):
    body = {"customer_id": "sujan", "text": "hi"}
    assert client.post("/api/store/messages", json=body).status_code == 401
    wrong = {"X-RahulCoolGram-Key": "nope"}
    assert client.post("/api/store/messages", json=body, headers=wrong).status_code == 401


def test_unknown_customer_is_404(client):
    assert client.get("/api/customers/nobody/messages").status_code == 404
    body = {"customer_id": "nobody", "text": "hi"}
    assert client.post("/api/store/messages", json=body, headers=KEY).status_code == 404


def test_empty_message_is_rejected(client):
    assert client.post("/api/customers/sujan/messages", json={"text": ""}).status_code == 422
