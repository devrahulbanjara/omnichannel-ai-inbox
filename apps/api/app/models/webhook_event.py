import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class WebhookEvent(Base):
    """Raw body of every accepted webhook. The unique key makes a resent webhook a no-op."""

    __tablename__ = "webhook_events"
    __table_args__ = (UniqueConstraint("channel_id", "external_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("channels.id"))
    external_id: Mapped[str]  # the channel's message id
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    received_at: Mapped[datetime] = mapped_column(default=utc_now)
    processed_at: Mapped[datetime | None]
