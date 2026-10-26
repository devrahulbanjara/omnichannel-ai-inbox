from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import events
from app.core.exceptions import NotFoundError
from app.models import Channel, Contact, ContactIdentity, WebhookEvent
from app.models.base import utc_now
from app.models.enums import ChannelType
from app.schemas.webhook import RahulCoolGramCustomer, RahulCoolGramWebhook
from app.services.conversation import ConversationService


class WebhookService:
    """Turns channel webhooks into contacts, conversations and messages."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def receive_rahulcoolgram(self, body: RahulCoolGramWebhook) -> bool:
        """Save the customer's message. Returns False if this message_id was already received."""
        channel = await self._rahulcoolgram_channel()

        # Store the raw event first; the unique (channel_id, external_id) key turns a resend
        # into a no-op. The whole method is one transaction, so a failure stores nothing.
        event_id = await self.session.scalar(
            insert(WebhookEvent)
            .values(
                org_id=channel.org_id,
                channel_id=channel.id,
                external_id=body.message_id,
                payload=body.model_dump(mode="json"),
            )
            .on_conflict_do_nothing(index_elements=["channel_id", "external_id"])
            .returning(WebhookEvent.id)
        )
        if event_id is None:
            return False

        contact = await self._get_or_create_contact(channel, body.customer)
        conversation = await ConversationService(self.session).get_or_start(contact, channel)
        self.session.add(conversation.receive_from_contact(body.text, body.message_id))
        await self.session.execute(
            update(WebhookEvent).where(WebhookEvent.id == event_id).values(processed_at=utc_now())
        )
        await self.session.commit()

        await events.publish("message.created", conversation_id=str(conversation.id))
        return True

    async def _rahulcoolgram_channel(self) -> Channel:
        # RahulCoolGram has a single store account, so there is one RahulCoolGram channel.
        channel = await self.session.scalar(
            select(Channel)
            .where(Channel.type == ChannelType.RAHULCOOLGRAM)
            .order_by(Channel.created_at)
        )
        if channel is None:
            raise NotFoundError("No RahulCoolGram channel exists. Run the seed script")
        return channel

    async def _get_or_create_contact(
        self, channel: Channel, customer: RahulCoolGramCustomer
    ) -> Contact:
        identity = await self.session.scalar(
            select(ContactIdentity).where(
                ContactIdentity.channel_id == channel.id,
                ContactIdentity.external_user_id == customer.id,
            )
        )
        if identity is not None:
            return await self.session.get_one(Contact, identity.contact_id)

        contact = Contact(org_id=channel.org_id, name=customer.name)
        self.session.add(contact)
        await self.session.flush()  # assigns contact.id
        self.session.add(
            ContactIdentity(
                org_id=channel.org_id,
                contact_id=contact.id,
                channel_id=channel.id,
                external_user_id=customer.id,
                username=customer.username,
            )
        )
        return contact
