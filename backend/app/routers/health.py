"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.session import check_db_connection
from app.schemas.common import HealthResponse

router = APIRouter(tags=["Health"])
logger = get_logger("routers.health")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
)
def health_check() -> HealthResponse:
    settings = get_settings()
    db_status = "unavailable"
    try:
        check_db_connection()
        db_status = "ok"
    except Exception:  # noqa: BLE001
        logger.exception("Health check database probe failed")

    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        app=settings.app_name,
        environment=settings.app_env,
        database=db_status,
    )
