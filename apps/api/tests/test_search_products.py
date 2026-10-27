import asyncio
import json

from app.agent.tools.base import ToolContext
from app.agent.tools.search_products import SearchProductsTool
from app.core.database import SessionLocal
from app.services.organization import OrganizationService


def search(**args) -> str:
    """Run search_products for the first demo store (Himal Luggage Co.)."""

    async def run() -> str:
        async with SessionLocal() as session:
            organization_service = OrganizationService(session)
            org = await organization_service.get_current()
            context = ToolContext(session=session, org=org)
            tool = SearchProductsTool()
            arguments = json.dumps(args)
            return await tool.call(arguments, context)

    return asyncio.run(run())


def test_every_word_must_match():
    result = search(query="black suitcase")

    assert "HLC-01-BLACK-24INCH: size 24 inch, color Black, Rs 5,900" in result
    assert "NAVY" not in result


def test_max_price_leaves_out_dearer_variants():
    result = search(query="black suitcase", max_price=5000)

    assert "Rs 4,900" in result
    assert "Rs 5,900" not in result


def test_in_stock_only_leaves_out_sold_out_variants():
    everything = search(query="suitcase")
    in_stock = search(query="suitcase", in_stock_only=True)

    assert "out of stock" in everything
    assert "out of stock" not in in_stock


def test_other_stores_products_are_not_found():
    result = search(query="lipstick")  # sold by Lalitpur Beauty Studio, not Himal Luggage

    assert result.startswith("No products matched")


def test_percent_sign_is_matched_literally():
    assert search(query="%").startswith("No products matched")


def test_invalid_arguments_are_explained():
    assert search(query=5).startswith("Invalid arguments.")
