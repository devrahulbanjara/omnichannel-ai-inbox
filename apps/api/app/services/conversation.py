import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models import Channel, Contact, Conversation, Organization
from app.models.base import utc_now


class ConversationService:
    """Conversation queries, always within one organization."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_recent(self, org: Organization) -> list[Conversation]:
        """Conversations ordered by latest activity."""
        result = await self.session.scalars(
            select(Conversation)
            .where(Conversation.org_id == org.id)
            .order_by(Conversation.last_message_at.desc())
        )
        return list(result)

    async def get(self, org: Organization, conversation_id: uuid.UUID) -> Conversation:
        conversation = await self.session.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.org_id == org.id
            )
        )
        if conversation is None:
            raise NotFoundError("Conversation not found")
        return conversation

    async def get_or_start(self, contact: Contact, channel: Channel) -> Conversation:
        """The contact's conversation on this channel, created on their first message."""
        conversation = await self.session.scalar(
            select(Conversation).where(
                Conversation.contact_id == contact.id, Conversation.channel_id == channel.id
            )
        )
        if conversation is None:
            conversation = Conversation(
                org_id=contact.org_id,
                contact=contact,
                channel=channel,
                last_message_at=utc_now(),
            )
            self.session.add(conversation)
            await self.session.flush()  # assigns conversation.id
        return conversation
