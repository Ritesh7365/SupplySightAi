"""
SupplySight AI — FastAPI application entrypoint.

Run (from ``backend/``)::

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

OpenAPI / Swagger UI: ``http://localhost:8000/docs``
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.router import build_api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.database.session import dispose_engine, init_db

logger = get_logger("main")


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Startup / shutdown hooks: logging, DB pool, graceful dispose."""
    settings = get_settings()
    setup_logging(settings)
    logger.info(
        "Starting %s (env=%s, version=%s, auth_enabled=%s)",
        settings.app_name,
        settings.app_env,
        __version__,
        settings.auth_enabled,
    )
    init_db(settings)
    logger.info("Database pool initialized")
    yield
    dispose_engine()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Application factory."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=(
            "SupplySight AI analytics API. "
            "Dashboard and chart endpoints read from the PostgreSQL "
            "``analytics`` schema (views / materialized views). "
            "Authentication is prepared but not enforced (`AUTH_ENABLED=false`)."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        debug=settings.app_debug,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    app.include_router(build_api_router(), prefix=settings.api_prefix)

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {
            "app": settings.app_name,
            "version": __version__,
            "docs": "/docs",
            "api_prefix": settings.api_prefix,
        }

    return app


app = create_app()
