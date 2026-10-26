import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.conversation import ConversationRead
from app.schemas.message import MessageCreate, MessageRead
from app.services.conversation import ConversationService
from app.services.message import MessageService

router = APIRouter(prefix="/conversations", tags=["inbox"])


@router.get("")
async def list_conversations(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[ConversationRead]:
    conversation_service = ConversationService(session)
    return await conversation_service.list_recent()


@router.get("/{conversation_id}/messages")
async def list_messages(
    conversation_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[MessageRead]:
    conversation_service = ConversationService(session)
    message_service = MessageService(session)

    conversation = await conversation_service.get(conversation_id)
    return await message_service.list_for(conversation)


@router.post("/{conversation_id}/messages", status_code=201)
async def send_staff_reply(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MessageRead:
    conversation_service = ConversationService(session)
    message_service = MessageService(session)

    conversation = await conversation_service.get(conversation_id)
    return await message_service.send_staff_reply(conversation, body.text)
