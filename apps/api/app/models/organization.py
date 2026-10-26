import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class Organization(Base):
    """A tenant: a store using the inbox."""

    __tablename__ = "organizations"

    # UUIDv7: time-ordered, so inserts stay index-friendly.
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
