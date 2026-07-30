"""
SupplySight AI — ETL pipeline orchestrator.

Executes Extract → Transform → Load with logging and structured error handling.
Does not connect to PostgreSQL.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Optional

# Allow `python database/etl/pipeline.py` from project root
_ETL_DIR = Path(__file__).resolve().parent
if str(_ETL_DIR) not in sys.path:
    sys.path.insert(0, str(_ETL_DIR))

from config import NORMALIZED_DATA_DIR, RAW_DATA_PATH
from extract import ExtractError, extract_raw_dataset
from load import LoadError, load
from transform import TransformError, transform
from utils import setup_logging


def run_pipeline() -> int:
    """
    Run the end-to-end normalization pipeline.

    Returns
    -------
    int
        Process exit code (0 success, 1 failure).
    """
    logger = setup_logging()
    logger.info("=" * 72)
    logger.info("SupplySight AI ETL - start")
    logger.info("Raw source : %s", RAW_DATA_PATH)
    logger.info("Output dir : %s", NORMALIZED_DATA_DIR)
    logger.info("=" * 72)

    try:
        # ----- Extract -----
        logger.info("STAGE 1/3 - EXTRACT")
        extract_result = extract_raw_dataset()
        logger.info(
            "Extract summary: rows=%s cols=%s encoding=%s",
            f"{extract_result.row_count:,}",
            extract_result.column_count,
            extract_result.encoding,
        )

        # ----- Transform -----
        logger.info("STAGE 2/3 - TRANSFORM")
        transform_result = transform(extract_result.dataframe)

        # ----- Load -----
        logger.info("STAGE 3/3 - LOAD")
        written = load(transform_result, NORMALIZED_DATA_DIR)

        logger.info("=" * 72)
        logger.info("ETL SUCCEEDED")
        for path in written:
            logger.info("  - %s", path)
        logger.info("=" * 72)
        return 0

    except (ExtractError, TransformError, LoadError) as exc:
        logger.error("ETL FAILED: %s", exc)
        logger.debug(traceback.format_exc())
        return 1
    except Exception as exc:  # noqa: BLE001
        logger.exception("ETL FAILED with unexpected error: %s", exc)
        return 1


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint."""
    _ = argv  # reserved for future flags
    return run_pipeline()


if __name__ == "__main__":
    sys.exit(main())
