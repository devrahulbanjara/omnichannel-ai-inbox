"""What the inbox endpoints must do."""

import uuid

MISSING_ID = str(uuid.uuid4())  # a valid id that no conversation has


def first_conversation_id(client) -> str:
    return client.get("/conversations").json()[0]["id"]


def test_list_conversations_newest_first(client):
    response = client.get("/conversations")

    assert response.status_code == 200
    names = [c["contact_name"] for c in response.json()]
    assert names == ["Anisha Karki", "Sujan Maharjan"]


def test_list_messages_of_a_conversation(client):
    conversation_id = first_conversation_id(client)

    response = client.get(f"/conversations/{conversation_id}/messages")

    assert response.status_code == 200
    [message] = response.json()
    assert message["direction"] == "in"
    assert message["sender_type"] == "contact"


def test_list_messages_of_unknown_conversation_is_404(client):
    response = client.get(f"/conversations/{MISSING_ID}/messages")

    assert response.status_code == 404


def test_staff_reply_is_saved_as_outgoing(client):
    conversation_id = first_conversation_id(client)

    response = client.post(
        f"/conversations/{conversation_id}/messages", json={"text": "Yes, it's Rs 4,500."}
    )

    assert response.status_code == 201
    message = response.json()
    assert message["text"] == "Yes, it's Rs 4,500."
    assert message["direction"] == "out"
    assert message["sender_type"] == "staff"
    listed = client.get(f"/conversations/{conversation_id}/messages").json()
    assert listed[-1]["id"] == message["id"]


def test_reply_moves_conversation_to_the_top(client):
    older_id = client.get("/conversations").json()[1]["id"]

    client.post(f"/conversations/{older_id}/messages", json={"text": "Hi Sujan!"})

    assert first_conversation_id(client) == older_id


def test_reply_to_unknown_conversation_is_404(client):
    response = client.post(f"/conversations/{MISSING_ID}/messages", json={"text": "Hello"})

    assert response.status_code == 404


def test_empty_reply_is_rejected_with_422(client):
    conversation_id = first_conversation_id(client)

    response = client.post(f"/conversations/{conversation_id}/messages", json={"text": ""})

    assert response.status_code == 422


def test_client_cannot_choose_the_sender(client):
    """Extra fields are ignored: the server decides direction and sender, not the caller."""
    conversation_id = first_conversation_id(client)

    response = client.post(
        f"/conversations/{conversation_id}/messages",
        json={"text": "I am the AI", "sender_type": "ai", "direction": "in"},
    )

    assert response.status_code == 201
    assert response.json()["sender_type"] == "staff"
    assert response.json()["direction"] == "out"


def test_malformed_conversation_id_is_rejected_with_422(client):
    response = client.get("/conversations/not-a-uuid/messages")

    assert response.status_code == 422


def test_reply_is_still_there_in_a_new_session(client):
    """It's really in Postgres: a fresh request (new DB session) still sees it."""
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/messages", json={"text": "Saved?"})

    texts = [m["text"] for m in client.get(f"/conversations/{conversation_id}/messages").json()]

    assert texts[-1] == "Saved?"
