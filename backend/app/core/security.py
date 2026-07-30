"""
Security helpers — prepared for future JWT authentication.

Auth is disabled by default (``AUTH_ENABLED=false``). Routers may depend on
``get_current_user_optional`` today; switch to ``get_current_user`` when enabling auth.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.core.config import Settings, get_settings

# Bearer scheme does not auto-error when credentials are missing
bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthUser:
    """Placeholder authenticated principal for future JWT claims."""

    subject: str
    roles: tuple[str, ...] = ()


async def get_current_user_optional(
    settings: Annotated[Settings, Depends(get_settings)],
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials],
        Depends(bearer_scheme),
    ],
) -> Optional[AuthUser]:
    """
    Optional auth dependency.

    Returns ``None`` when auth is disabled or no bearer token is provided.
    When auth is enabled, missing/invalid tokens raise 401 (stub behavior).
    """
    if not settings.auth_enabled:
        return None

    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Future: decode JWT with settings.jwt_secret_key / jwt_algorithm
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication is enabled but JWT validation is not implemented yet",
    )


async def get_current_user(
    user: Annotated[Optional[AuthUser], Depends(get_current_user_optional)],
) -> AuthUser:
    """Required auth dependency for future protected routes."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
