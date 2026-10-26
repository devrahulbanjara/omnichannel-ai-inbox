"""Seed demo data for local development: `uv run python -m scripts.seed`."""

import asyncio
from datetime import timedelta

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.models import Contact, Conversation, Message, Organization
from app.models.base import utc_now
from app.models.enums import Direction, SenderType

DEMO_CHATS = [
    ("Sujan Maharjan", "Do you have the 24-inch suitcase in black?", 30),
    ("Anisha Karki", "What is the price of the travel backpack?", 5),
]


async def seed_demo_data(session: AsyncSession) -> None:
    org = Organization(name="Himal Luggage Co.")
    session.add(org)
    await session.flush()  # assigns org.id

    for name, text, minutes_ago in DEMO_CHATS:
        at = utc_now() - timedelta(minutes=minutes_ago)
        contact = Contact(org_id=org.id, name=name)
        session.add(contact)
        await session.flush()
        conversation = Conversation(
            org_id=org.id,
            contact_id=contact.id,
            channel="rahulcoolgram",
            last_message_at=at,
        )
        session.add(conversation)
        await session.flush()
        session.add(
            Message(
                org_id=org.id,
                conversation_id=conversation.id,
                direction=Direction.IN,
                sender_type=SenderType.CONTACT,
                text=text,
                created_at=at,
            )
        )


async def main() -> None:
    async with SessionLocal() as session:
        if await session.scalar(select(func.count()).select_from(Organization)):
            logger.info("Database already has data, nothing to seed")
            return
        await seed_demo_data(session)
        await session.commit()
        logger.info("Seeded {} demo conversations", len(DEMO_CHATS))


if __name__ == "__main__":
    asyncio.run(main())
