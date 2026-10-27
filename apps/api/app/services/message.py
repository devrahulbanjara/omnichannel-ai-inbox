import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.channels.base import DeliveryError
from app.channels.registry import ADAPTERS
from app.core.events import events
from app.models import ContactIdentity, Conversation, Message
from app.models.enums import DeliveryStatus


class MessageService:
    """Message queries, staff replies and their delivery to the channel."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for(self, conversation: Conversation) -> list[Message]:
        """Messages in chronological order."""
        result = await self.session.scalars(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at)
        )
        return list(result)

    async def send_staff_reply(
        self, conversation: Conversation, text: str, idempotency_key: str | None = None
    ) -> Message:
        """Save the reply, then deliver it. A repeated idempotency key returns the first message."""
        conversation_id = conversation.id
        if idempotency_key:
            existing = await self._find_by_key(conversation_id, idempotency_key)
            if existing:
                return existing

        message = conversation.reply_as_staff(text)
        message.idempotency_key = idempotency_key
        self.session.add(message)
        try:
            await self.session.commit()  # message and conversation update in one transaction
        except IntegrityError:
            # The same key arrived twice at the same moment and the other request saved first.
            await self.session.rollback()
            if idempotency_key is None:  # without a key, the failure has another cause
                raise
            existing = await self._find_by_key(conversation_id, idempotency_key)
            if existing is None:
                raise
            return existing
        await events.publish("message.created", conversation_id=str(conversation_id))

        await self._deliver(conversation, message)
        return message

    async def _deliver(self, conversation: Conversation, message: Message) -> None:
        """Hand the message to the channel and record the result. Never raises."""
        try:
            identity = await self.session.scalar(
                select(ContactIdentity).where(
                    ContactIdentity.contact_id == conversation.contact_id,
                    ContactIdentity.channel_id == conversation.channel_id,
                )
            )
            if identity is None:
                raise DeliveryError("This contact has no account on the channel")
            adapter = ADAPTERS[conversation.channel.type]
            message.external_id = await adapter.send(identity.external_user_id, message.text)
            message.delivery_status = DeliveryStatus.SENT
        except DeliveryError as exc:
            message.delivery_status = DeliveryStatus.FAILED
            message.error = str(exc)
        await self.session.commit()
        await events.publish("message.updated", conversation_id=str(conversation.id))

    async def _find_by_key(self, conversation_id: uuid.UUID, key: str) -> Message | None:
        return await self.session.scalar(
            select(Message).where(
                Message.conversation_id == conversation_id, Message.idempotency_key == key
            )
        )
