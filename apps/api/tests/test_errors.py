import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.errors import add_error_handlers
from app.main import create_app


def test_unknown_conversation_has_error_shape(client):
    response = client.get(f"/conversations/{uuid.uuid4()}/messages")

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": "Conversation not found"}}


def test_unknown_url_has_error_shape(client):
    response = client.get("/no-such-page")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


def test_invalid_body_lists_the_bad_fields(client):
    conversation_id = client.get("/conversations").json()[0]["id"]

    response = client.post(f"/conversations/{conversation_id}/messages", json={"text": ""})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["details"][0]["field"] == "body.text"


def test_unexpected_error_hides_internal_details():
    app = FastAPI()
    add_error_handlers(app)

    @app.get("/boom")
    def boom():
        raise RuntimeError("database password is hunter2")

    response = TestClient(app, raise_server_exceptions=False).get("/boom")

    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "message": "Something went wrong on our side"}
    }


def test_unexpected_error_still_has_a_request_id():
    app = create_app()

    @app.get("/boom")
    def boom():
        raise RuntimeError("bug")

    response = TestClient(app, raise_server_exceptions=False).get("/boom")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert len(response.headers["X-Request-ID"]) == 32
