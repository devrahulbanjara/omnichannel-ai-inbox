import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class Contact(Base):
    """A customer of a store."""

    __tablename__ = "contacts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
