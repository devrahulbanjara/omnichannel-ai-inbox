"""Inbox business logic. Callers like the HTTP routes use these functions instead of queries."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from inbox.models import Conversation, Message, utc_now


async def list_conversations(session: AsyncSession) -> list[Conversation]:
    result = await session.scalars(
        select(Conversation).order_by(Conversation.last_message_at.desc())
    )
    return list(result)


async def get_conversation(
    session: AsyncSession, conversation_id: uuid.UUID
) -> Conversation | None:
    return await session.get(Conversation, conversation_id)


async def list_messages(session: AsyncSession, conversation_id: uuid.UUID) -> list[Message]:
    result = await session.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return list(result)


async def add_staff_reply(session: AsyncSession, conversation: Conversation, text: str) -> Message:
    now = utc_now()
    message = Message(
        org_id=conversation.org_id,
        conversation_id=conversation.id,
        direction="out",
        sender_type="staff",
        text=text,
        created_at=now,
    )
    session.add(message)
    conversation.last_message_at = now
    await session.commit()  # the message and the conversation update are saved together
    return message
