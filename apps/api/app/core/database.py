"""Async engine and per-request session."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

# NullPool in tests: asyncpg connections are bound to the event loop that created them.
_pool_options = {"poolclass": NullPool} if settings.environment == "test" else {}
engine = create_async_engine(settings.database_url, **_pool_options)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
