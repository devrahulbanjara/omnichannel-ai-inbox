import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import set_committed_value

from app.core.events import events
from app.core.exceptions import NotFoundError
from app.models import Channel, Conversation, Customer, Organization
from app.models.base import utc_now
from app.models.enums import ConversationOwner


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

    async def mark_read(self, conversation: Conversation) -> Conversation:
        """Mark the conversation as seen and tell every dashboard. Safe to repeat."""
        if conversation.mark_read():
            await self.session.commit()
            await events.publish("conversation.updated", conversation_id=str(conversation.id))
        return conversation

    async def lock_owner(self, conversation: Conversation) -> str:
        """Lock the conversation row until the next commit or rollback, and return its current
        owner.

        The owner can change while a reply is being written (the agent takes seconds). Owner
        changes and replies both take this lock, so they run one after the other: a reply checks
        the owner under the lock right before it is saved.
        """
        owner = await self.session.scalar(
            select(Conversation.owner).where(Conversation.id == conversation.id).with_for_update()
        )
        if owner is None:
            raise NotFoundError("Conversation not found")
        set_committed_value(conversation, "owner", owner)  # refresh it without marking a change
        return owner

    async def set_owner(self, conversation: Conversation, owner: ConversationOwner) -> Conversation:
        """Give the conversation to the AI or to staff and tell every dashboard. Safe to repeat."""
        current_owner = await self.lock_owner(conversation)
        if current_owner == owner:
            await self.session.commit()  # nothing changed; releases the lock
            return conversation
        conversation.owner = owner
        await self.session.commit()
        await events.publish("conversation.updated", conversation_id=str(conversation.id))
        return conversation

    async def get_or_start(self, customer: Customer, channel: Channel) -> Conversation:
        """The customer's conversation on this channel, created on their first message."""
        conversation = await self.session.scalar(
            select(Conversation).where(
                Conversation.customer_id == customer.id, Conversation.channel_id == channel.id
            )
        )
        if conversation is None:
            conversation = Conversation(
                org_id=customer.org_id,
                customer=customer,
                channel=channel,
                last_message_at=utc_now(),
            )
            self.session.add(conversation)
            await self.session.flush()  # assigns conversation.id
        return conversation
