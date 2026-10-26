import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Conversation


class ConversationService:
    """Conversation queries."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_recent(self) -> list[Conversation]:
        """Conversations ordered by latest activity."""
        result = await self.session.scalars(
            select(Conversation).order_by(Conversation.last_message_at.desc())
        )
        return list(result)

    async def get(self, conversation_id: uuid.UUID) -> Conversation:
        conversation = await self.session.get(Conversation, conversation_id)
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return conversation
