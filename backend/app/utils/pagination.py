"""Helpers for converting SQLAlchemy rows to plain dicts."""

from __future__ import annotations

from typing import Any, Iterable, Sequence


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


def clamp_limit(limit: int | None, *, default: int = 100, maximum: int = 1000) -> int:
    """Normalize pagination/limit query params."""
    if limit is None:
        return default
    return max(1, min(int(limit), maximum))
