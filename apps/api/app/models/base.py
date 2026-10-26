"""Declarative base for all tables."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    """Declarative base. All datetime columns map to timestamptz."""

    type_annotation_map = {datetime: DateTime(timezone=True)}

    # Deterministic constraint names, so migrations can reference them.
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )
