import json
import logging

from core.logs import JsonFormatter, RequestIdFilter, request_id_var


def test_response_has_a_request_id(client):
    response = client.get("/health")

    assert len(response.headers["X-Request-ID"]) == 32


def test_incoming_request_id_is_reused(client):
    response = client.get("/health", headers={"X-Request-ID": "trace-from-rahulcoolgram"})

    assert response.headers["X-Request-ID"] == "trace-from-rahulcoolgram"


def test_every_request_is_logged(client, caplog):
    caplog.set_level(logging.INFO, logger="api.request")

    client.get("/conversations")

    [record] = [r for r in caplog.records if r.message == "request finished"]
    assert (record.method, record.path, record.status) == ("GET", "/conversations", 200)


def test_log_line_is_json_with_the_request_id():
    token = request_id_var.set("abc123")
    try:
        record = logging.makeLogRecord({"name": "test", "msg": "hello", "levelname": "INFO"})
        record.order_id = 42
        RequestIdFilter().filter(record)
        line = json.loads(JsonFormatter().format(record))
    finally:
        request_id_var.reset(token)

    assert line["message"] == "hello"
    assert line["request_id"] == "abc123"
    assert line["order_id"] == 42
