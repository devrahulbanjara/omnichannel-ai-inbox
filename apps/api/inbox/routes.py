"""HTTP endpoints for conversations and messages. Thin: parse the request, call the service."""

import uuid

from fastapi import APIRouter, HTTPException

from core.db import SessionDep
from inbox import service
from inbox.models import Conversation
from inbox.schemas import ConversationRead, MessageCreate, MessageRead

router = APIRouter(prefix="/conversations", tags=["inbox"])


async def get_conversation_or_404(session: SessionDep, conversation_id: uuid.UUID) -> Conversation:
    conversation = await service.get_conversation(session, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.get("")
async def list_conversations(session: SessionDep) -> list[ConversationRead]:
    """All conversations, the most recently active first."""
    return await service.list_conversations(session)


@router.get("/{conversation_id}/messages")
async def list_messages(session: SessionDep, conversation_id: uuid.UUID) -> list[MessageRead]:
    """The messages of one conversation, oldest first."""
    await get_conversation_or_404(session, conversation_id)
    return await service.list_messages(session, conversation_id)


@router.post("/{conversation_id}/messages", status_code=201)
async def send_staff_reply(
    session: SessionDep, conversation_id: uuid.UUID, body: MessageCreate
) -> MessageRead:
    """A staff member replies to the customer."""
    conversation = await get_conversation_or_404(session, conversation_id)
    return await service.add_staff_reply(session, conversation, body.text)
