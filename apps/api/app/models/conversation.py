import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now
from app.models.channel import Channel
from app.models.customer import Customer
from app.models.enums import ConversationStatus, DeliveryStatus, Direction, SenderType
from app.models.message import Message


class Conversation(Base):
    """One thread between a customer and the store, on one channel."""

    __tablename__ = "conversations"
    __table_args__ = (CheckConstraint("status IN ('open', 'resolved')", name="status_valid"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), index=True)
    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("channels.id"), index=True)
    status: Mapped[str] = mapped_column(default=ConversationStatus.OPEN)
    last_message_at: Mapped[datetime] = mapped_column(index=True)
    last_message_text: Mapped[str | None]  # shown as the preview line in the inbox list
    # Customer messages no staff member has seen yet. Shared by all staff of the store.
    unread_count: Mapped[int] = mapped_column(default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())

    # Eager JOINs: every conversation listing displays the customer name and channel.
    customer: Mapped[Customer] = relationship(lazy="joined")
    channel: Mapped[Channel] = relationship(lazy="joined")

    @property
    def customer_name(self) -> str:
        return self.customer.name

    @property
    def channel_type(self) -> str:
        return self.channel.type

    def receive_from_customer(self, text: str, external_id: str) -> Message:
        """Create an incoming customer message. Not persisted; the caller adds it to the session."""
        message = self._add_message(text, Direction.IN, SenderType.CUSTOMER)
        message.external_id = external_id
        self.unread_count += 1
        return message

    def mark_read(self) -> bool:
        """Mark every message as seen. Returns False if nothing was unread."""
        if self.unread_count == 0:
            return False
        self.unread_count = 0
        return True

    def reply_as_staff(self, text: str) -> Message:
        """Create an outgoing staff message, queued for delivery. Not persisted."""
        message = self._add_message(text, Direction.OUT, SenderType.STAFF)
        message.delivery_status = DeliveryStatus.QUEUED
        return message

    def reply_as_ai(self, text: str) -> Message:
        """Create an outgoing AI agent message, queued for delivery. Not persisted."""
        message = self._add_message(text, Direction.OUT, SenderType.AI)
        message.delivery_status = DeliveryStatus.QUEUED
        return message

    def _add_message(self, text: str, direction: Direction, sender_type: SenderType) -> Message:
        message = Message(
            org_id=self.org_id,
            conversation_id=self.id,
            direction=direction,
            sender_type=sender_type,
            text=text,
            created_at=utc_now(),
        )
        self.last_message_at = message.created_at
        self.last_message_text = text
        return message
