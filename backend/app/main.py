"""
SupplySight AI — FastAPI application entrypoint.

Run (from the ``backend/`` directory)::

    python -m uvicorn app.main:app --reload
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

OpenAPI / Swagger UI: ``http://localhost:8000/docs``
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app import __version__
from app.api.router import build_api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging
from app.core.openapi import API_DESCRIPTION, OPENAPI_CONTACT, OPENAPI_LICENSE, OPENAPI_TAGS
from app.database.session import dispose_engine, init_db
from app.middleware import (
    RequestIdMiddleware,
    RequestTimingMiddleware,
    ResponseHeadersMiddleware,
)
from app.routers import health as health_router

logger = get_logger("main")

# GZip responses larger than this many bytes
GZIP_MINIMUM_SIZE = 1000


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
    logger.info(
        "Database pool initialized (size=%s, max_overflow=%s, recycle=%s)",
        settings.db_pool_size,
        settings.db_max_overflow,
        settings.db_pool_recycle,
    )
    yield
    dispose_engine()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Application factory with production middleware stack."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description=API_DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        debug=settings.app_debug,
        openapi_tags=OPENAPI_TAGS,
        contact=OPENAPI_CONTACT,
        license_info=OPENAPI_LICENSE,
    )

    # Middleware order: last added runs first on the request path.
    # Request enters: RequestId → Timing → ResponseHeaders → CORS → GZip → app
    app.add_middleware(GZipMiddleware, minimum_size=GZIP_MINIMUM_SIZE)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-Request-ID",
            "X-Process-Time-Ms",
            "X-API-Version",
        ],
    )
    app.add_middleware(ResponseHeadersMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RequestIdMiddleware)

    register_exception_handlers(app)

    # Orchestrator health probes at root (not under /api/v1)
    app.include_router(health_router.router)

    # Versioned business API
    app.include_router(build_api_router(), prefix=settings.api_prefix)

    @app.get("/", include_in_schema=False)
    def root() -> dict[str, str]:
        return {
            "app": settings.app_name,
            "version": __version__,
            "docs": "/docs",
            "health": "/health",
            "api_prefix": settings.api_prefix,
        }

    return app


app = create_app()
