import pytest
from loguru import logger


@pytest.fixture
def logs():
    """Collect the log records written during a test."""
    records = []
    sink_id = logger.add(lambda message: records.append(message.record), level="INFO")
    yield records
    logger.remove(sink_id)


def test_response_has_a_request_id(client):
    response = client.get("/health")

    assert len(response.headers["X-Request-ID"]) == 32


def test_incoming_request_id_is_reused(client):
    response = client.get("/health", headers={"X-Request-ID": "trace-from-rahulcoolgram"})

    assert response.headers["X-Request-ID"] == "trace-from-rahulcoolgram"


def test_every_request_is_logged_with_its_id(client, logs):
    response = client.get("/conversations")

    [record] = logs
    assert record["message"].startswith("GET /conversations → 200")
    assert record["extra"]["request_id"] == response.headers["X-Request-ID"]
