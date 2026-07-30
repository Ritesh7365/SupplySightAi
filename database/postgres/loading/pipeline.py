"""
SupplySight AI — Enterprise normalized CSV load pipeline.

Flow:
  1. Ensure placeholder CSVs exist
  2. Open transaction
  3. Truncate public tables (FK-safe)
  4. Load each CSV (COPY → INSERT fallback) with progress
  5. Validate PKs / FKs
  6. Commit or rollback
  7. Write database/postgres/reports/load_report.md
"""

from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

from tqdm import tqdm

# Make database/postgres importable
_POSTGRES_DIR = Path(__file__).resolve().parents[1]
if str(_POSTGRES_DIR) not in sys.path:
    sys.path.insert(0, str(_POSTGRES_DIR))

from connection import get_connection, setup_module_logging  # noqa: E402
from loading.config import LOAD_ORDER, LOG_DIR, TRUNCATE_ORDER  # noqa: E402
from loading.copy_load import (  # noqa: E402
    TableLoadResult,
    ensure_vendor_products_csv,
    load_table_with_fallback,
    prepare_schema_for_source_data,
    truncate_tables,
)
from loading.report import write_load_report  # noqa: E402
from loading.validate import ValidationReport, run_validations  # noqa: E402

logger = logging.getLogger("supplysight.postgres.loading.pipeline")


def _configure_file_logging() -> None:
    """Add a file handler under database/postgres/logs/."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / "data_load.log"
    root = logging.getLogger("supplysight.postgres")
    # Avoid duplicate file handlers on re-entry
    for handler in root.handlers:
        if isinstance(handler, logging.FileHandler) and getattr(handler, "baseFilename", "").endswith(
            "data_load.log"
        ):
            return
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    root.addHandler(fh)
    logger.info("File logging -> %s", log_path)


def run_load_pipeline(*, truncate: bool = True) -> int:
    """
    Execute the full load pipeline.

    Returns
    -------
    int
        Process exit code (0 success, 1 failure).
    """
    setup_module_logging()
    _configure_file_logging()

    started = time.perf_counter()
    load_results: list[TableLoadResult] = []
    validation = ValidationReport()
    success = False

    logger.info("=" * 72)
    logger.info("SupplySight AI — normalized CSV load into public schema")
    logger.info("Tables: %s", ", ".join(LOAD_ORDER))
    logger.info("=" * 72)

    ensure_vendor_products_csv()

    try:
        with get_connection(autocommit=False) as conn:
            prepare_schema_for_source_data(conn)
            if truncate:
                logger.info("Truncating target tables (CASCADE, reverse FK order)")
                truncate_tables(conn, TRUNCATE_ORDER)

            for table in tqdm(LOAD_ORDER, desc="Loading tables", unit="table"):
                result = load_table_with_fallback(conn, table)
                load_results.append(result)

            logger.info("Running post-load validations")
            validation = run_validations(conn, LOAD_ORDER)

            if validation.error_count > 0:
                logger.error(
                    "Validation failed with %s error(s) — rolling back",
                    validation.error_count,
                )
                conn.rollback()
                success = False
            else:
                conn.commit()
                success = True
                logger.info("Transaction committed")

    except Exception as exc:  # noqa: BLE001
        logger.exception("Load pipeline failed: %s", exc)
        success = False
        # Connection context manager already rolled back
        if not load_results:
            load_results.append(
                TableLoadResult(
                    table="(pipeline)",
                    csv_path=Path("."),
                    method="FAILED",
                    error=str(exc),
                )
            )

    elapsed = time.perf_counter() - started
    report_path = write_load_report(
        load_results,
        validation,
        total_elapsed=elapsed,
        success=success,
    )
    logger.info("Load report: %s", report_path)
    logger.info("Pipeline finished status=%s elapsed=%.2fs", success, elapsed)
    return 0 if success else 1


def main() -> int:
    """CLI entrypoint."""
    return run_load_pipeline(truncate=True)


if __name__ == "__main__":
    raise SystemExit(main())
