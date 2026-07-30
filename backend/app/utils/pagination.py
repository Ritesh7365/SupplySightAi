"""Reusable pagination helpers for list endpoints."""

from __future__ import annotations

from typing import Annotated, Any, Generic, Iterable, List, Optional, Sequence, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


def clamp_limit(limit: int | None, *, default: int = 100, maximum: int = 1000) -> int:
    """Normalize limit query params into ``[1, maximum]``."""
    if limit is None:
        return default
    return max(1, min(int(limit), maximum))


def clamp_offset(offset: int | None) -> int:
    """Normalize offset to a non-negative integer."""
    if offset is None:
        return 0
    return max(0, int(offset))


def clamp_page(page: int | None) -> int:
    """Normalize 1-based page number."""
    if page is None:
        return 1
    return max(1, int(page))


class PaginationParams(BaseModel):
    """Normalized pagination state."""

    page: int = Field(ge=1, description="1-based page number")
    page_size: int = Field(ge=1, description="Items per page")
    offset: int = Field(ge=0, description="Rows to skip")

    @property
    def limit(self) -> int:
        return self.page_size


def pagination_params(
    page: Annotated[int, Query(ge=1, description="1-based page number")] = 1,
    page_size: Annotated[
        int,
        Query(ge=1, le=1000, alias="page_size", description="Items per page (max 1000)"),
    ] = 50,
    limit: Annotated[
        Optional[int],
        Query(
            ge=1,
            le=1000,
            description="Optional alias for page_size (takes precedence when set)",
        ),
    ] = None,
    offset: Annotated[
        Optional[int],
        Query(ge=0, description="Optional absolute offset (overrides page when set)"),
    ] = None,
) -> PaginationParams:
    """FastAPI dependency that resolves page/page_size/limit/offset."""
    size = clamp_limit(limit if limit is not None else page_size, default=50, maximum=1000)
    if offset is not None:
        off = clamp_offset(offset)
        computed_page = (off // size) + 1
        return PaginationParams(page=computed_page, page_size=size, offset=off)

    page_n = clamp_page(page)
    return PaginationParams(page=page_n, page_size=size, offset=(page_n - 1) * size)


def paginate_sequence(items: Sequence[T], params: PaginationParams) -> list[T]:
    """Slice an in-memory sequence using pagination params."""
    start = params.offset
    end = start + params.page_size
    return list(items[start:end])


class PageMeta(BaseModel):
    page: int
    page_size: int
    offset: int
    total: Optional[int] = None
    has_next: Optional[bool] = None


class Page(BaseModel, Generic[T]):
    """Reusable paginated envelope."""

    data: List[T]
    meta: PageMeta
    count: int = Field(description="Number of items in this page")

    @classmethod
    def build(
        cls,
        items: Sequence[T],
        params: PaginationParams,
        *,
        total: int | None = None,
    ) -> "Page[T]":
        page_items = list(items)
        has_next: bool | None = None
        if total is not None:
            has_next = params.offset + len(page_items) < total
        elif len(page_items) == params.page_size:
            has_next = True

        return cls(
            data=page_items,
            count=len(page_items),
            meta=PageMeta(
                page=params.page,
                page_size=params.page_size,
                offset=params.offset,
                total=total,
                has_next=has_next,
            ),
        )


def row_to_dict(row: Any) -> dict[str, Any]:
    """Convert an ORM instance or mapping row to a dict."""
    if hasattr(row, "__dict__") and hasattr(row, "__table__"):
        return {col.name: getattr(row, col.name) for col in row.__table__.columns}
    if hasattr(row, "_mapping"):
        return dict(row._mapping)
    if isinstance(row, dict):
        return row
    return dict(row)


def rows_to_dicts(rows: Iterable[Any]) -> list[dict[str, Any]]:
    return [row_to_dict(r) for r in rows]
