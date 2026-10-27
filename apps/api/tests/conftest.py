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

from app.channels.base import DeliveryError
from app.channels.rahulcoolgram import RahulCoolGramAdapter
from app.core.database import SessionLocal, engine
from app.main import create_app
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
        table_names = []
        for table in Base.metadata.sorted_tables:
            table_names.append(table.name)
        async with engine.begin() as conn:
            await conn.execute(text(f"TRUNCATE {', '.join(table_names)}"))
        async with SessionLocal() as session:
            await seed_demo_data(session)
            await session.commit()

    asyncio.run(reset())


@pytest.fixture
def client():
    """A fresh app per test, so dependency overrides never leak between tests."""
    with TestClient(create_app()) as client:
        yield client


class FakeRahulCoolGram:
    """Stands in for RahulCoolGram's API. Records sent messages; set `down` to fail delivery."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []
        self.down = False

    async def send(self, external_user_id: str, text: str) -> str:
        if self.down:
            raise DeliveryError("Could not reach RahulCoolGram")
        self.sent.append((external_user_id, text))
        return f"rcg-{len(self.sent)}"


@pytest.fixture(autouse=True)
def rahulcoolgram(monkeypatch) -> FakeRahulCoolGram:
    """Tests never call the real RahulCoolGram."""
    fake = FakeRahulCoolGram()
    monkeypatch.setattr(RahulCoolGramAdapter, "send", lambda _self, *args: fake.send(*args))
    return fake
