"""Logging configuration for the FastAPI backend."""

from __future__ import annotations

import logging
import sys
from typing import Optional

from app.core.config import Settings, get_settings


def setup_logging(settings: Optional[Settings] = None) -> None:
    """Configure root + app loggers once at startup."""
    cfg = settings or get_settings()
    level = getattr(logging, cfg.log_level.upper(), logging.INFO)

    root = logging.getLogger()
    if root.handlers:
        root.setLevel(level)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
    root.setLevel(level)

    # Keep noisy libraries quieter in production
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if cfg.db_echo else logging.WARNING
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger under the supplysight namespace."""
    if not name.startswith("supplysight"):
        name = f"supplysight.{name}"
    return logging.getLogger(name)
