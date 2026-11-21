"""Unread count tests: customer messages count up, reading clears them for all staff."""

import uuid

from tests.test_webhooks import KEY, webhook_body


def send_customer_message(client, text: str) -> str:
    """Posts a message from the same new customer and returns their conversation id."""
    client.post("/webhooks/rahulcoolgram", json=webhook_body(text=text), headers=KEY)
    return client.get("/conversations").json()[0]["id"]


def unread_count_of(client, conversation_id: str) -> int:
    for conversation in client.get("/conversations").json():
        if conversation["id"] == conversation_id:
            return conversation["unread_count"]
    raise AssertionError("conversation not listed")


def test_each_customer_message_adds_one_unread(client):
    send_customer_message(client, "Namaste")
    conversation_id = send_customer_message(client, "Are you there?")

    assert unread_count_of(client, conversation_id) == 2


def test_staff_reply_does_not_count_as_unread(client):
    conversation_id = send_customer_message(client, "Namaste")

    client.post(f"/conversations/{conversation_id}/messages", json={"text": "Hello!"})

    assert unread_count_of(client, conversation_id) == 1


def test_reading_a_conversation_clears_its_unread_count(client):
    conversation_id = send_customer_message(client, "Namaste")

    response = client.post(f"/conversations/{conversation_id}/read")

    assert response.status_code == 200
    assert response.json()["unread_count"] == 0
    assert unread_count_of(client, conversation_id) == 0


def test_reading_twice_is_safe(client):
    conversation_id = send_customer_message(client, "Namaste")
    client.post(f"/conversations/{conversation_id}/read")

    response = client.post(f"/conversations/{conversation_id}/read")

    assert response.status_code == 200
    assert response.json()["unread_count"] == 0


def test_reading_unknown_conversation_is_404(client):
    response = client.post(f"/conversations/{uuid.uuid4()}/read")

    assert response.status_code == 404


def test_other_dashboards_hear_when_a_conversation_is_read(client):
    conversation_id = send_customer_message(client, "Namaste")

    with client.websocket_connect("/live") as live:
        client.post(f"/conversations/{conversation_id}/read")

        event = live.receive_json()

    assert event == {"type": "conversation.updated", "conversation_id": conversation_id}
