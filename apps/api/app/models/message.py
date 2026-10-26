import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class Message(Base):
    """A message in a conversation."""

    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint("direction IN ('in', 'out')", name="direction_valid"),
        CheckConstraint("sender_type IN ('contact', 'staff', 'ai')", name="sender_type_valid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), index=True)
    direction: Mapped[str]  # Direction
    sender_type: Mapped[str]  # SenderType
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
