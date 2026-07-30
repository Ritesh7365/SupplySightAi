"""Health, liveness, readiness, and database probe endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app import __version__
from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.session import check_db_connection, get_pool_status
from app.schemas.common import (
    OPENAPI_ERROR_RESPONSES,
    DatabaseHealthResponse,
    HealthResponse,
    HealthStatusResponse,
    LivenessResponse,
    ReadinessResponse,
)

router = APIRouter(tags=["Health"])
logger = get_logger("routers.health")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Aggregate service health",
    description="Returns overall application status including a database probe.",
    responses={503: OPENAPI_ERROR_RESPONSES[503]},
)
def health_check() -> HealthResponse | JSONResponse:
    settings = get_settings()
    db_status = "unavailable"
    try:
        check_db_connection()
        db_status = "ok"
    except Exception as exc:  # noqa: BLE001
        logger.exception("Health check database probe failed: %s", exc)

    payload = HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        app=settings.app_name,
        environment=settings.app_env,
        database=db_status,
    )
    if db_status != "ok":
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload.model_dump(),
        )
    return payload


@router.get(
    "/health/database",
    response_model=DatabaseHealthResponse,
    summary="Database connectivity probe",
    description="Executes ``SELECT 1`` and reports SQLAlchemy pool statistics.",
    responses={503: OPENAPI_ERROR_RESPONSES[503]},
)
def health_database() -> DatabaseHealthResponse | JSONResponse:
    try:
        check_db_connection()
        pool = get_pool_status()
        return DatabaseHealthResponse(status="ok", database="ok", pool=pool)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Database health probe failed")
        payload = DatabaseHealthResponse(
            status="unavailable",
            database="unavailable",
            detail=str(exc.__class__.__name__),
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload.model_dump(),
        )


@router.get(
    "/health/readiness",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    description="Ready when the process can reach PostgreSQL (use for load balancer checks).",
    responses={503: OPENAPI_ERROR_RESPONSES[503]},
)
def health_readiness() -> ReadinessResponse | JSONResponse:
    checks: dict[str, str] = {"process": "ok"}
    try:
        check_db_connection()
        checks["database"] = "ok"
    except Exception:  # noqa: BLE001
        logger.exception("Readiness database check failed")
        checks["database"] = "unavailable"

    ready = all(v == "ok" for v in checks.values())
    payload = ReadinessResponse(
        status="ready" if ready else "not_ready",
        checks=checks,
    )
    if not ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=payload.model_dump(),
        )
    return payload


@router.get(
    "/health/liveness",
    response_model=LivenessResponse,
    summary="Liveness probe",
    description="Confirms the API process is running. Does not check the database.",
)
def health_liveness() -> LivenessResponse:
    settings = get_settings()
    return LivenessResponse(
        status="alive",
        app=settings.app_name,
        version=__version__,
    )


@router.get(
    "/health/status",
    response_model=HealthStatusResponse,
    summary="Compact status",
    include_in_schema=True,
    description="Minimal status string for simple uptime monitors.",
)
def health_status() -> HealthStatusResponse:
    try:
        check_db_connection()
        return HealthStatusResponse(status="ok", detail="all checks passed")
    except Exception:  # noqa: BLE001
        return HealthStatusResponse(status="degraded", detail="database unavailable")
