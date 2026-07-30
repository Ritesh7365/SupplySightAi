"""Shared FastAPI dependencies."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.security import AuthUser, get_current_user_optional
from app.database.session import get_db

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]
OptionalUser = Annotated[AuthUser | None, Depends(get_current_user_optional)]


def get_db_session() -> Generator[Session, None, None]:
    """Alias kept for explicit imports in services/tests."""
    yield from get_db()
