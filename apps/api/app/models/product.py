import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now
from app.models.product_variant import ProductVariant


class Product(Base):
    """An item a store sells. Customers buy one of its variants."""

    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str]
    description: Mapped[str]
    category: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())

    variants: Mapped[list[ProductVariant]] = relationship(order_by=ProductVariant.sku)
