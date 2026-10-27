import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Conversation, Message
from app.schemas.conversation import ConversationRead
from app.schemas.error import ERROR_RESPONSES
from app.schemas.message import MessageCreate, MessageRead
from app.services.conversation import ConversationService
from app.services.message import MessageService
from app.services.organization import OrganizationService

router = APIRouter(prefix="/conversations", tags=["inbox"], responses=ERROR_RESPONSES)


@router.get("", response_model=list[ConversationRead])
async def list_conversations(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[Conversation]:
    organization_service = OrganizationService(session)
    conversation_service = ConversationService(session)

    org = await organization_service.get_current()
    return await conversation_service.list_recent(org)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
async def list_messages(
    conversation_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[Message]:
    organization_service = OrganizationService(session)
    conversation_service = ConversationService(session)
    message_service = MessageService(session)

    org = await organization_service.get_current()
    conversation = await conversation_service.get(org, conversation_id)
    return await message_service.list_for(conversation)


@router.post("/{conversation_id}/messages", status_code=201, response_model=MessageRead)
async def send_staff_reply(
    conversation_id: uuid.UUID,
    body: MessageCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    idempotency_key: Annotated[
        str | None,
        Header(
            max_length=100,
            description="Any unique string per reply. Resending with the same key "
            "returns the first message instead of creating a second one",
        ),
    ] = None,
) -> Message:
    organization_service = OrganizationService(session)
    conversation_service = ConversationService(session)
    message_service = MessageService(session)

    org = await organization_service.get_current()
    conversation = await conversation_service.get(org, conversation_id)
    return await message_service.send_staff_reply(conversation, body.text, idempotency_key)
