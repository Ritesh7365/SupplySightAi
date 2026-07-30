"""Shared Pydantic response helpers and OpenAPI error models."""

from __future__ import annotations

from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base schema that can be built from ORM / mapping rows."""

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    """Legacy combined health payload (kept for compatibility)."""

    status: str = Field(examples=["ok"])
    app: str
    environment: str
    database: str = Field(description="ok | unavailable | unknown")


class HealthStatusResponse(BaseModel):
    """Lightweight probe response."""

    status: str = Field(examples=["ok", "degraded", "unavailable"])
    detail: Optional[str] = None


class DatabaseHealthResponse(BaseModel):
    status: str = Field(examples=["ok", "unavailable"])
    database: str = Field(examples=["ok", "unavailable"])
    pool: Optional[dict[str, Any]] = None
    detail: Optional[str] = None


class ReadinessResponse(BaseModel):
    status: str = Field(examples=["ready", "not_ready"])
    checks: dict[str, str]


class LivenessResponse(BaseModel):
    status: str = Field(examples=["alive"])
    app: str
    version: str


class ErrorBody(BaseModel):
    code: str = Field(examples=["validation_error", "not_found", "internal_error"])
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard API error envelope."""

    error: ErrorBody
    request_id: Optional[str] = Field(default=None, examples=["a1b2c3d4-e5f6-7890-abcd-ef1234567890"])


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[object] = None


class ListResponse(BaseModel, Generic[T]):
    """Generic list envelope with optional total/limit metadata."""

    data: List[T]
    count: int
    limit: Optional[int] = None


# Shared OpenAPI response declarations for routers
OPENAPI_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    404: {
        "description": "Resource not found",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": {"code": "not_found", "message": "The requested resource was not found"},
                    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                }
            }
        },
    },
    422: {
        "description": "Validation error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "code": "validation_error",
                        "message": "Request validation failed",
                        "details": [{"loc": ["query", "limit"], "msg": "ensure this value is >= 1"}],
                    },
                    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                }
            }
        },
    },
    500: {
        "description": "Internal server error",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": {"code": "internal_error", "message": "An unexpected error occurred"},
                    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                }
            }
        },
    },
    503: {
        "description": "Database or dependency unavailable",
        "model": ErrorResponse,
        "content": {
            "application/json": {
                "example": {
                    "error": {
                        "code": "database_error",
                        "message": "A database error occurred while serving this request",
                    },
                    "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                }
            }
        },
    },
}
