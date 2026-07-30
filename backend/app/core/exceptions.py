"""Application-specific exceptions and FastAPI error handlers."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

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


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


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


def _json_error(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=_error_body(
            code=code,
            message=message,
            details=details,
            request_id=_request_id(request),
        ),
        headers={"X-Request-ID": _request_id(request) or ""},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers (404, 422, 500, DB, validation)."""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "AppError request_id=%s path=%s code=%s message=%s",
            _request_id(request),
            request.url.path,
            exc.code,
            exc.message,
        )
        return _json_error(
            request,
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code_map = {
            404: "not_found",
            401: "unauthorized",
            403: "forbidden",
            405: "method_not_allowed",
            501: "not_implemented",
        }
        code = code_map.get(exc.status_code, "http_error")
        message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            message = message if message != "Not Found" else "The requested resource was not found"
            logger.info(
                "404 request_id=%s path=%s",
                _request_id(request),
                request.url.path,
            )
        else:
            logger.warning(
                "HTTPException request_id=%s status=%s path=%s detail=%s",
                _request_id(request),
                exc.status_code,
                request.url.path,
                exc.detail,
            )
        return _json_error(
            request,
            status_code=exc.status_code,
            code=code,
            message=message,
            details=exc.detail if not isinstance(exc.detail, str) else None,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.info(
            "422 validation request_id=%s path=%s errors=%s",
            _request_id(request),
            request.url.path,
            exc.errors(),
        )
        return _json_error(
            request,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="validation_error",
            message="Request validation failed",
            details=exc.errors(),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(
        request: Request,
        exc: SQLAlchemyError,
    ) -> JSONResponse:
        logger.exception(
            "Database error request_id=%s path=%s",
            _request_id(request),
            request.url.path,
        )
        return _json_error(
            request,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="database_error",
            message="A database error occurred while serving this request",
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "500 internal error request_id=%s path=%s",
            _request_id(request),
            request.url.path,
        )
        return _json_error(
            request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="internal_error",
            message="An unexpected error occurred",
        )
