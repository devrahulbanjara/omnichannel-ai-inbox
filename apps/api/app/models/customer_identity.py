import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class CustomerIdentity(Base):
    """A customer's account on one channel, e.g. RahulCoolGram customer "sujan"."""

    __tablename__ = "customer_identities"
    __table_args__ = (UniqueConstraint("channel_id", "external_user_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), index=True)
    channel_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("channels.id"))
    external_user_id: Mapped[str]  # the customer's id inside the channel
    username: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
