"""
SupplySight AI — ETL utilities.

Logging setup and small helpers shared across extract / transform / load.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

from config import LOG_DATE_FORMAT, LOG_DIR, LOG_FORMAT


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Configure root logging for the ETL run (console + rotating file).

    Parameters
    ----------
    level:
        Logging level for the pipeline logger.

    Returns
    -------
    logging.Logger
        Named logger for ``supplysight.etl``.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "etl_pipeline.log"

    logger = logging.getLogger("supplysight.etl")
    logger.setLevel(level)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Prefer UTF-8 on Windows consoles to avoid UnicodeEncodeError on arrows/dashes
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info("Logging initialized -> %s", log_file)
    return logger


def ensure_directory(path: Path) -> None:
    """Create a directory (and parents) if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def zipcode_to_str(value: object) -> Optional[str]:
    """
    Convert zip-like values to string without changing business meaning.

    Integers/floats that represent whole numbers become digit strings
    (avoids ``12345.0`` artifacts). Nulls stay null.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if pd.isna(value):
        return None
    try:
        as_float = float(value)
        if as_float.is_integer():
            return str(int(as_float))
    except (TypeError, ValueError):
        pass
    return str(value)


def frame_summary(name: str, df: pd.DataFrame) -> str:
    """Return a one-line summary for logging."""
    return f"{name}: rows={len(df):,} cols={df.shape[1]}"
