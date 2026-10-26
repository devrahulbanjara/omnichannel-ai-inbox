"""Database tables (SQLAlchemy ORM). Every tenant table has org_id from the start."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class Organization(Base):
    """A store using the inbox (a tenant). Every tenant table points to one."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())


class Contact(Base):
    """A customer of a store."""

    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())


class Conversation(Base):
    """One thread between a contact and the store, on one channel."""

    __tablename__ = "conversations"
    __table_args__ = (CheckConstraint("status IN ('open', 'resolved')", name="status_valid"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    contact_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contacts.id"), index=True)
    channel: Mapped[str]
    status: Mapped[str] = mapped_column(default="open")
    last_message_at: Mapped[datetime] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())

    # Loaded together with the conversation (one JOIN), because the inbox always shows the name.
    contact: Mapped[Contact] = relationship(lazy="joined")

    @property
    def contact_name(self) -> str:
        return self.contact.name


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint("direction IN ('in', 'out')", name="direction_valid"),
        CheckConstraint("sender_type IN ('contact', 'staff', 'ai')", name="sender_type_valid"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), index=True)
    direction: Mapped[str]
    sender_type: Mapped[str]
    text: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
