import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class Channel(Base):
    """A store's account on one messaging app. Webhooks find their organization through it."""

    __tablename__ = "channels"
    __table_args__ = (CheckConstraint("type IN ('rahulcoolgram')", name="type_valid"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    type: Mapped[str]  # ChannelType
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
