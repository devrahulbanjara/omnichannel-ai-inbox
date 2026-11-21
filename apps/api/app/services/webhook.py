from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import events
from app.core.exceptions import NotFoundError
from app.models import Channel, Customer, CustomerIdentity, WebhookEvent
from app.models.base import utc_now
from app.models.enums import ChannelType
from app.schemas.webhook import RahulCoolGramCustomer, RahulCoolGramWebhook
from app.services.conversation import ConversationService


class WebhookService:
    """Turns channel webhooks into customers, conversations and messages."""

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

        customer = await self._get_or_create_customer(channel, body.customer)
        conversation = await ConversationService(self.session).get_or_start(customer, channel)
        self.session.add(conversation.receive_from_customer(body.text, body.message_id))
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

    async def _get_or_create_customer(
        self, channel: Channel, account: RahulCoolGramCustomer
    ) -> Customer:
        identity = await self.session.scalar(
            select(CustomerIdentity).where(
                CustomerIdentity.channel_id == channel.id,
                CustomerIdentity.external_user_id == account.id,
            )
        )
        if identity is not None:
            return await self.session.get_one(Customer, identity.customer_id)

        customer = Customer(org_id=channel.org_id, name=account.name)
        self.session.add(customer)
        await self.session.flush()  # assigns customer.id
        self.session.add(
            CustomerIdentity(
                org_id=channel.org_id,
                customer_id=customer.id,
                channel_id=channel.id,
                external_user_id=account.id,
                username=account.username,
            )
        )
        return customer
