"""
SupplySight AI — ETL Extract stage.

Reads and validates the raw DataCo CSV. Does not alter business values.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config import (
    CSV_ENCODING,
    EXPECTED_COLUMN_COUNT,
    EXPECTED_MIN_ROW_COUNT,
    RAW_DATA_PATH,
)

logger = logging.getLogger("supplysight.etl.extract")


@dataclass(frozen=True)
class ExtractResult:
    """Validated raw extract payload."""

    dataframe: pd.DataFrame
    source_path: Path
    encoding: str
    row_count: int
    column_count: int


class ExtractError(Exception):
    """Raised when extract validation fails."""


def validate_source_file(path: Path = RAW_DATA_PATH) -> None:
    """
    Confirm the raw file exists and is non-empty.

    Raises
    ------
    ExtractError
        If the path is missing or empty.
    """
    logger.info("Validating source file: %s", path)
    if not path.exists():
        raise ExtractError(f"Raw dataset not found: {path}")
    if not path.is_file():
        raise ExtractError(f"Raw dataset path is not a file: {path}")
    size = path.stat().st_size
    if size <= 0:
        raise ExtractError(f"Raw dataset is empty: {path}")
    logger.info("Source file OK (size=%s bytes)", f"{size:,}")


def extract_raw_dataset(
    path: Path = RAW_DATA_PATH,
    encoding: str = CSV_ENCODING,
) -> ExtractResult:
    """
    Load the DataCo CSV and validate row/column counts.

    Parameters
    ----------
    path:
        Absolute or relative path to the raw CSV.
    encoding:
        File encoding (DataCo requires latin-1).

    Returns
    -------
    ExtractResult
        Raw dataframe plus metadata for downstream stages.
    """
    validate_source_file(path)

    logger.info("Reading CSV with encoding=%s ...", encoding)
    try:
        df = pd.read_csv(path, encoding=encoding, low_memory=False)
    except UnicodeDecodeError as exc:
        raise ExtractError(
            f"Failed to decode CSV with encoding '{encoding}': {exc}"
        ) from exc
    except Exception as exc:  # noqa: BLE001 — surface any IO/parse failure
        raise ExtractError(f"Failed to read CSV: {exc}") from exc

    row_count, column_count = df.shape
    logger.info("Extracted row_count=%s column_count=%s", f"{row_count:,}", column_count)

    if column_count != EXPECTED_COLUMN_COUNT:
        raise ExtractError(
            f"Unexpected column count: got {column_count}, "
            f"expected {EXPECTED_COLUMN_COUNT}"
        )
    if row_count < EXPECTED_MIN_ROW_COUNT:
        raise ExtractError(
            f"Row count too low: got {row_count}, "
            f"minimum expected {EXPECTED_MIN_ROW_COUNT}"
        )

    logger.info("Extract validation passed")
    return ExtractResult(
        dataframe=df,
        source_path=path,
        encoding=encoding,
        row_count=row_count,
        column_count=column_count,
    )
