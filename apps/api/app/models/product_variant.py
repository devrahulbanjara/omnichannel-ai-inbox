import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, utc_now


class ProductVariant(Base):
    """One buyable version of a product, e.g. the black 24-inch suitcase. Has its own SKU."""

    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("org_id", "sku"),
        CheckConstraint("price >= 0", name="price_not_negative"),
        CheckConstraint("stock >= 0", name="stock_not_negative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid7)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), index=True)
    sku: Mapped[str]  # stock keeping unit, the store's code for this variant
    options: Mapped[dict[str, str]] = mapped_column(JSONB)  # e.g. {"color": "Black", "size": "M"}
    price: Mapped[int]  # NPR, whole rupees
    stock: Mapped[int]  # units on hand
    created_at: Mapped[datetime] = mapped_column(default=utc_now, server_default=func.now())
