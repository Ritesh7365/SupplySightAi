"""Shared Pydantic response helpers."""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base schema that can be built from ORM / mapping rows."""

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    app: str
    environment: str
    database: str = Field(description="ok | unavailable")


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[object] = None


class ListResponse(BaseModel, Generic[T]):
    """Generic list envelope with optional total/limit metadata."""

    data: List[T]
    count: int
    limit: Optional[int] = None
