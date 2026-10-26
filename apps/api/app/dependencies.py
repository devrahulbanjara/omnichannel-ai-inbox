"""Per-request dependencies. Each resolves once per request, so services share one session."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.services.conversation import ConversationService
from app.services.message import MessageService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_conversation_service(session: SessionDep) -> ConversationService:
    return ConversationService(session)


def get_message_service(session: SessionDep) -> MessageService:
    return MessageService(session)


ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]
MessageServiceDep = Annotated[MessageService, Depends(get_message_service)]
