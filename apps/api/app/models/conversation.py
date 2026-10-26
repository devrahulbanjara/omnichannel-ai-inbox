import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now
from app.models.contact import Contact
from app.models.enums import ConversationStatus, Direction, SenderType
from app.models.message import Message


class Conversation(Base):
    """One thread between a contact and the store, on one channel."""

    __tablename__ = "conversations"
    __table_args__ = (CheckConstraint("status IN ('open', 'resolved')", name="status_valid"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contacts.id"), index=True)
    channel: Mapped[str]
    status: Mapped[str] = mapped_column(default=ConversationStatus.OPEN)
    last_message_at: Mapped[datetime] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())

    # Eager JOIN: every conversation listing displays the contact name.
    contact: Mapped[Contact] = relationship(lazy="joined")

    @property
    def contact_name(self) -> str:
        return self.contact.name

    def reply_as_staff(self, text: str) -> Message:
        """Create an outgoing staff message. Not persisted; the caller adds it to the session."""
        return self._add_message(text, Direction.OUT, SenderType.STAFF)

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
        return message
