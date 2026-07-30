"""Application-specific exceptions and FastAPI error handlers."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger("supplysight.api.errors")


class AppError(Exception):
    """Base application error with HTTP semantics."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "app_error",
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", **kwargs: Any) -> None:
        super().__init__(
            message,
            status_code=status.HTTP_404_NOT_FOUND,
            code="not_found",
            **kwargs,
        )


class DatabaseError(AppError):
    def __init__(self, message: str = "Database operation failed", **kwargs: Any) -> None:
        super().__init__(
            message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="database_error",
            **kwargs,
        )


def _error_body(
    *,
    code: str,
    message: str,
    details: Any = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if details is not None:
        body["error"]["details"] = details
    if request_id:
        body["request_id"] = request_id
    return body


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to the FastAPI app."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "AppError on %s %s: %s",
            request.method,
            request.url.path,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(code=exc.code, message=exc.message, details=exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.info("Validation error on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                code="validation_error",
                message="Request validation failed",
                details=exc.errors(),
            ),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        logger.exception("Database error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=_error_body(
                code="database_error",
                message="A database error occurred while serving this request",
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body(
                code="internal_error",
                message="An unexpected error occurred",
            ),
        )
