import asyncio
import uuid

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models import WebhookEvent
from tests.test_replies import message_texts

KEY = {"X-RahulCoolGram-Key": "dev-secret"}


def webhook_body(customer_id="prabin", name="Prabin Gurung", message_id=None, text="Namaste"):
    return {
        "message_id": message_id or str(uuid.uuid4()),
        "customer": {"id": customer_id, "name": name, "username": "prabin.grg"},
        "text": text,
        "sent_at": "2026-10-26T10:00:00Z",
    }


def count_webhook_events() -> int:
    async def count():
        async with SessionLocal() as session:
            result = await session.execute(select(func.count()).select_from(WebhookEvent))
            return result.scalar_one()

    return asyncio.run(count())


def test_missing_key_is_rejected_with_401(client):
    response = client.post("/webhooks/rahulcoolgram", json=webhook_body())

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"


def test_wrong_key_is_rejected_before_the_body_is_checked(client):
    response = client.post(
        "/webhooks/rahulcoolgram", json={"bad": "body"}, headers={"X-RahulCoolGram-Key": "guess"}
    )

    assert response.status_code == 401


def test_first_message_from_a_new_customer_starts_a_conversation(client):
    response = client.post(
        "/webhooks/rahulcoolgram", json=webhook_body(text="Namaste"), headers=KEY
    )

    assert response.json() == {"status": "saved"}
    newest = client.get("/conversations").json()[0]
    assert newest["customer_name"] == "Prabin Gurung"
    assert newest["channel"] == "rahulcoolgram"
    [message, ai_reply] = client.get(f"/conversations/{newest['id']}/messages").json()
    assert message["text"] == "Namaste"
    assert message["sender_type"] == "customer"
    assert message["direction"] == "in"
    assert ai_reply["sender_type"] == "ai"


def test_known_customer_continues_their_conversation(client):
    before = len(client.get("/conversations").json())

    client.post(
        "/webhooks/rahulcoolgram",
        json=webhook_body(customer_id="sujan", name="Sujan Maharjan", text="Still there?"),
        headers=KEY,
    )

    conversations = client.get("/conversations").json()
    assert len(conversations) == before
    assert conversations[0]["customer_name"] == "Sujan Maharjan"
    texts = message_texts(client, f"/conversations/{conversations[0]['id']}/messages")
    assert "Still there?" in texts


def test_resent_webhook_saves_the_message_once_and_replies_once(client, llm):
    body = webhook_body(message_id="rcg-123")

    first = client.post("/webhooks/rahulcoolgram", json=body, headers=KEY)
    second = client.post("/webhooks/rahulcoolgram", json=body, headers=KEY)

    assert first.json() == {"status": "saved"}
    assert second.json() == {"status": "duplicate"}
    conversation_id = client.get("/conversations").json()[0]["id"]
    texts = message_texts(client, f"/conversations/{conversation_id}/messages")
    assert texts == ["Namaste", llm.answer]
    assert count_webhook_events() == 1
    assert len(llm.calls) == 1
