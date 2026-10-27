import asyncio

from app.core.database import SessionLocal
from app.models import Channel, Contact, Conversation, Organization
from app.models.base import utc_now


def add_other_store_conversation() -> str:
    async def add():
        async with SessionLocal() as session:
            org = Organization(name="Other Store")
            session.add(org)
            await session.flush()
            channel = Channel(org_id=org.id, type="rahulcoolgram", name="RahulCoolGram")
            contact = Contact(org_id=org.id, name="Other Customer")
            session.add_all([channel, contact])
            await session.flush()
            conversation = Conversation(
                org_id=org.id, contact=contact, channel=channel, last_message_at=utc_now()
            )
            session.add(conversation)
            await session.commit()
            return str(conversation.id)

    return asyncio.run(add())


def test_organization_is_the_seeded_store(client):
    response = client.get("/organization")

    assert response.json()["name"] == "Himal Luggage Co."


def test_other_stores_conversations_are_invisible(client):
    other_id = add_other_store_conversation()

    names = []
    for conversation in client.get("/conversations").json():
        names.append(conversation["contact_name"])
    response = client.get(f"/conversations/{other_id}/messages")

    assert "Other Customer" not in names
    assert response.status_code == 404
