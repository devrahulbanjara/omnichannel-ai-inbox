from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, Product, ProductVariant


class ProductService:
    """Product queries, always within one organization."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search(
        self,
        org: Organization,
        query: str,
        max_price: int | None = None,
        in_stock_only: bool = False,
        limit: int = 30,
    ) -> list[tuple[Product, ProductVariant]]:
        """Variants where every word of the query appears in the product's name, category,
        description or the variant's options. Ordered by product name, then price."""
        searchable_text = func.lower(
            func.concat_ws(
                " ",
                Product.name,
                Product.category,
                Product.description,
                cast(ProductVariant.options, String),
            )
        )
        statement = (
            select(Product, ProductVariant)
            .join(ProductVariant, ProductVariant.product_id == Product.id)
            .where(Product.org_id == org.id)
        )
        for word in query.lower().split():
            # autoescape: a "%" or "_" typed by the customer is matched literally
            statement = statement.where(searchable_text.contains(word, autoescape=True))
        if max_price is not None:
            statement = statement.where(ProductVariant.price <= max_price)
        if in_stock_only:
            statement = statement.where(ProductVariant.stock > 0)
        statement = statement.order_by(Product.name, ProductVariant.price).limit(limit)

        result = await self.session.execute(statement)
        return list(result)
