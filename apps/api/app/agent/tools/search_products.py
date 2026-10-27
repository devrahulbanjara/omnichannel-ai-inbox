from pydantic import BaseModel, Field

from app.agent.tools.base import Tool, ToolContext
from app.models import Product, ProductVariant
from app.services.product import ProductService

MAX_RESULTS = 30


class SearchProductsArgs(BaseModel):
    query: str = Field(
        description="A few simple words that must all match, e.g. 'black suitcase' or 'jacket'. "
        "Use the singular form and leave out filler words like 'do you have'."
    )
    max_price: int | None = Field(default=None, description="Highest price in NPR, if given")
    in_stock_only: bool = Field(default=False, description="Leave out variants with no stock")


class SearchProductsTool(Tool):
    name = "search_products"
    description = (
        "Search this store's products. Returns matching variants with their SKU, options "
        "(such as color and size), price in NPR and stock. Use it before stating any product, "
        "price, option or stock. If nothing matches, try again with fewer or more general words."
    )
    args_model = SearchProductsArgs

    async def run(self, arguments: str, context: ToolContext) -> str:
        args = SearchProductsArgs.model_validate_json(arguments)
        product_service = ProductService(context.session)
        matches = await product_service.search(
            context.org,
            args.query,
            max_price=args.max_price,
            in_stock_only=args.in_stock_only,
            limit=MAX_RESULTS,
        )
        if not matches:
            return "No products matched. Try fewer or more general words."
        return self.format_matches(matches)

    @staticmethod
    def format_matches(matches: list[tuple[Product, ProductVariant]]) -> str:
        """One heading per product, one line per variant."""
        lines = []
        previous_product = None
        for product, variant in matches:
            if product is not previous_product:
                lines.append(f"{product.name} ({product.category}): {product.description}")
                previous_product = product

            options = []
            for option_name, value in variant.options.items():
                options.append(f"{option_name} {value}")
            stock = f"{variant.stock} in stock" if variant.stock > 0 else "out of stock"
            option_text = ", ".join(options)
            lines.append(f"- {variant.sku}: {option_text}, Rs {variant.price:,}, {stock}")

        if len(matches) == MAX_RESULTS:
            lines.append(f"Showing the first {MAX_RESULTS} variants. Add words to narrow it.")
        return "\n".join(lines)
