"""SQLAlchemy declarative base."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for ORM models (analytics view mappings)."""

    pass
