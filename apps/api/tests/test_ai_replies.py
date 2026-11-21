"""AI replies: saved as sender "ai", delivered to the channel like staff replies."""

import asyncio
import uuid

from app.core.database import SessionLocal
from app.services.conversation import ConversationService
from app.services.message import MessageService
from app.services.organization import OrganizationService
from tests.test_replies import conversation_id_of


def send_ai_reply(conversation_id: str, text: str) -> None:
    async def run():
        async with SessionLocal() as session:
            org = await OrganizationService(session).get_current()
            conversation_service = ConversationService(session)
            conversation = await conversation_service.get(org, uuid.UUID(conversation_id))
            message_service = MessageService(session)
            await message_service.send_ai_reply(conversation, text)

    asyncio.run(run())


def test_ai_reply_is_saved_as_ai_and_delivered(client, rahulcoolgram):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    send_ai_reply(conversation_id, "Yes, Rs 5,900.")

    last_message = client.get(f"/conversations/{conversation_id}/messages").json()[-1]
    assert last_message["sender_type"] == "ai"
    assert last_message["text"] == "Yes, Rs 5,900."
    assert last_message["delivery_status"] == "sent"
    assert rahulcoolgram.sent == [("sujan", "Yes, Rs 5,900.")]


def test_ai_reply_is_marked_failed_when_rahulcoolgram_is_down(client, rahulcoolgram):
    rahulcoolgram.down = True
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    send_ai_reply(conversation_id, "Yes, Rs 5,900.")

    last_message = client.get(f"/conversations/{conversation_id}/messages").json()[-1]
    assert last_message["delivery_status"] == "failed"
    assert last_message["error"] == "Could not reach RahulCoolGram"


def test_other_dashboards_hear_about_an_ai_reply(client):
    conversation_id = conversation_id_of(client, "Sujan Maharjan")

    with client.websocket_connect("/live") as live:
        send_ai_reply(conversation_id, "Hello!")

        event = live.receive_json()

    assert event == {"type": "message.created", "conversation_id": conversation_id}
