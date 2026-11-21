"""Conversation owner: the AI or staff answers, never both."""

import uuid

from app.core.database import SessionLocal
from app.models.enums import ConversationOwner
from app.services.conversation import ConversationService
from app.services.organization import OrganizationService
from tests.test_replies import assign_to_staff, conversation_id_of
from tests.test_webhooks import KEY, webhook_body


def set_owner(client, conversation_id: str, owner: str):
    return client.put(f"/conversations/{conversation_id}/owner", json={"owner": owner})


def post_customer_message(client, text: str):
    body = webhook_body(customer_id="sujan", name="Sujan Maharjan", text=text)
    return client.post("/webhooks/rahulcoolgram", json=body, headers=KEY)


def last_message(client, conversation_id: str) -> dict:
    return client.get(f"/conversations/{conversation_id}/messages").json()[-1]


def test_new_conversation_is_owned_by_the_ai(client):
    client.post("/webhooks/rahulcoolgram", json=webhook_body(text="Namaste"), headers=KEY)

    newest = client.get("/conversations").json()[0]
    assert newest["owner"] == "ai"


def test_ai_stays_quiet_when_staff_owns_the_conversation(client, llm, rahulcoolgram):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")
    assign_to_staff(client, conversation_id)

    post_customer_message(client, "Black suitcase?")

    assert llm.calls == []
    assert rahulcoolgram.sent == []
    assert last_message(client, conversation_id)["text"] == "Black suitcase?"


def test_staff_cannot_reply_while_the_ai_owns_the_conversation(client):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    response = client.post(f"/conversations/{conversation_id}/messages", json={"text": "Hi"})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


def test_handing_back_to_the_ai_makes_it_answer_again(client, llm):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")
    assign_to_staff(client, conversation_id)

    response = set_owner(client, conversation_id, "ai")
    post_customer_message(client, "Black suitcase?")

    assert response.json()["owner"] == "ai"
    assert last_message(client, conversation_id)["sender_type"] == "ai"
    staff_reply = client.post(f"/conversations/{conversation_id}/messages", json={"text": "Hi"})
    assert staff_reply.status_code == 409


def test_other_dashboards_hear_about_an_owner_change(client):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    with client.websocket_connect("/live") as live:
        assign_to_staff(client, conversation_id)

        event = live.receive_json()

    assert event == {"type": "conversation.updated", "conversation_id": conversation_id}


def test_unknown_owner_is_rejected_with_422(client):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    response = set_owner(client, conversation_id, "nobody")

    assert response.status_code == 422


def test_ai_answer_is_dropped_when_staff_takes_over_while_it_thinks(client, llm, rahulcoolgram):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    async def staff_takes_over():
        async with SessionLocal() as session:
            org = await OrganizationService(session).get_current()
            conversation_service = ConversationService(session)
            conversation = await conversation_service.get(org, uuid.UUID(conversation_id))
            await conversation_service.set_owner(conversation, ConversationOwner.STAFF)

    llm.while_thinking = staff_takes_over

    response = post_customer_message(client, "Black suitcase?")

    assert response.json() == {"status": "saved"}
    assert len(llm.calls) == 1  # the agent did answer
    assert rahulcoolgram.sent == []  # but its answer was not sent
    assert last_message(client, conversation_id)["text"] == "Black suitcase?"


def test_setting_the_same_owner_twice_is_safe(client):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    first = set_owner(client, conversation_id, "staff")
    second = set_owner(client, conversation_id, "staff")

    assert first.json()["owner"] == "staff"
    assert second.json()["owner"] == "staff"
