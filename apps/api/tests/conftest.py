import os

# Must run before the app import: settings are read at import time.
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", "postgresql+asyncpg://inbox:inbox@localhost:5432/inbox_test"
)

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal, engine
from app.main import app
from app.models import Base
from scripts.seed import seed_demo_data


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session."""

    async def create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create())


@pytest.fixture(autouse=True)
def demo_data():
    """Reset the database to the demo data before each test."""

    async def reset():
        tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
        async with engine.begin() as conn:
            await conn.execute(text(f"TRUNCATE {tables}"))
        async with SessionLocal() as session:
            await seed_demo_data(session)
            await session.commit()

    asyncio.run(reset())


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
