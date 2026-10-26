import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class Message(Base):
    """A message in a conversation."""

    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint("direction IN ('in', 'out')", name="direction_valid"),
        CheckConstraint("sender_type IN ('contact', 'staff', 'ai')", name="sender_type_valid"),
        CheckConstraint(
            "delivery_status IN ('queued', 'sent', 'failed')", name="delivery_status_valid"
        ),
        # A request resent with the same Idempotency-Key finds the first message.
        UniqueConstraint("conversation_id", "idempotency_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), index=True)
    direction: Mapped[str]  # Direction
    sender_type: Mapped[str]  # SenderType
    text: Mapped[str]
    external_id: Mapped[str | None]  # the channel's id for this message
    delivery_status: Mapped[str | None]  # DeliveryStatus; outgoing messages only
    error: Mapped[str | None]  # why delivery failed
    idempotency_key: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
