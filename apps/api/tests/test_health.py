from fastapi.testclient import TestClient

from core.db import get_session
from main import app


def test_live_returns_ok(client):
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ok_when_database_is_up(client):
    response = client.get("/health/ready")

    assert response.status_code == 200


def test_ready_returns_503_when_database_is_down():
    class BrokenSession:
        async def execute(self, statement):
            raise ConnectionError("database is down")

    app.dependency_overrides[get_session] = lambda: BrokenSession()
    try:
        response = TestClient(app).get("/health/ready")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
