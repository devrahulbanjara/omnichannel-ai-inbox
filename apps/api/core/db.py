"""Database connection: one async engine for the app, one session per request."""

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import DateTime, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from core.config import settings


class Base(DeclarativeBase):
    """Parent of every table class. Every datetime column stores a time zone (timestamptz)."""

    type_annotation_map = {datetime: DateTime(timezone=True)}

    # Predictable constraint names (e.g. fk_messages_conversation_id_conversations), so later
    # migrations can drop or change a constraint by name.
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


# Tests open a new event loop per test; pooled connections can't move between loops.
_pool_options = {"poolclass": NullPool} if settings.environment == "test" else {}
engine = create_async_engine(settings.database_url, **_pool_options)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
