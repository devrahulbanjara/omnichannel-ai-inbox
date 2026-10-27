"""Seed demo data for local development: `uv run python -m scripts.seed [--reset]`.

Contacts are RahulCoolGram's demo customers, linked by their RahulCoolGram ids, so new messages
from those customers land in these conversations. The seeded history exists only in the inbox.
"""

import asyncio
import sys
from datetime import timedelta

from loguru import logger
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.models import (
    Base,
    Channel,
    Contact,
    ContactIdentity,
    Conversation,
    Message,
    Organization,
)
from app.models.base import utc_now
from app.models.enums import ChannelType, DeliveryStatus, Direction, SenderType

# (RahulCoolGram id, name, username, [(minutes ago, sender, text)])
DEMO_CHATS = [
    (
        "anisha",
        "Anisha Karki",
        "anisha.k",
        [(6, "contact", "What is the price of the travel backpack?")],
    ),
    (
        "sujan",
        "Sujan Maharjan",
        "sujan.mhj",
        [
            (45, "contact", "Do you have the 24-inch suitcase in black?"),
            (42, "staff", "Yes, the Everest Hardshell 24-inch comes in black. It is Rs 5,900."),
            (30, "contact", "Can you deliver to Baneshwor?"),
        ],
    ),
    (
        "bikash",
        "Bikash Thapa",
        "bikash_thapa",
        [
            (180, "contact", "Is the duffel bag waterproof?"),
            (175, "staff", "It is water resistant, good for rain, not for full soaking."),
            (170, "contact", "Ok thank you"),
        ],
    ),
]
SENDERS = {
    "contact": (Direction.IN, SenderType.CONTACT),
    "staff": (Direction.OUT, SenderType.STAFF),
}


async def seed_demo_data(session: AsyncSession) -> None:
    org = Organization(name="Himal Luggage Co.")
    session.add(org)
    await session.flush()  # assigns org.id
    channel = Channel(org_id=org.id, type=ChannelType.RAHULCOOLGRAM, name="RahulCoolGram")
    session.add(channel)
    await session.flush()

    for external_id, name, username, messages in DEMO_CHATS:
        contact = Contact(org_id=org.id, name=name)
        session.add(contact)
        await session.flush()
        session.add(
            ContactIdentity(
                org_id=org.id,
                contact_id=contact.id,
                channel_id=channel.id,
                external_user_id=external_id,
                username=username,
            )
        )
        conversation = Conversation(
            org_id=org.id, contact=contact, channel=channel, last_message_at=utc_now()
        )
        session.add(conversation)
        await session.flush()

        for minutes_ago, sender, body in messages:
            direction, sender_type = SENDERS[sender]
            at = utc_now() - timedelta(minutes=minutes_ago)
            session.add(
                Message(
                    org_id=org.id,
                    conversation_id=conversation.id,
                    direction=direction,
                    sender_type=sender_type,
                    text=body,
                    delivery_status=DeliveryStatus.SENT if direction == Direction.OUT else None,
                    created_at=at,
                )
            )
            conversation.last_message_at = at
            conversation.last_message_text = body


async def main(reset: bool) -> None:
    async with SessionLocal() as session:
        if reset:
            table_names = []
            for table in Base.metadata.sorted_tables:
                table_names.append(table.name)
            await session.execute(text(f"TRUNCATE {', '.join(table_names)}"))
            logger.info("Deleted all data")
        elif await session.scalar(select(func.count()).select_from(Organization)):
            logger.info("Database already has data, nothing to seed. Use --reset to start over")
            return
        await seed_demo_data(session)
        await session.commit()
        logger.info("Seeded {} demo conversations", len(DEMO_CHATS))


if __name__ == "__main__":
    asyncio.run(main(reset="--reset" in sys.argv))
