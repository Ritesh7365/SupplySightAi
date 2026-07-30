"""
SupplySight AI — Orchestrate database initialization (no CSV load).

Runs: schemas → DDL → views → materialized views → verification report.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from connection import setup_module_logging  # noqa: E402
from create_materialized_views import create_materialized_views  # noqa: E402
from create_schemas import create_platform_schemas  # noqa: E402
from create_views import create_analytics_views  # noqa: E402
from execute_schema_files import execute_schema_files, verify_core_tables_exist  # noqa: E402
from verify_database import write_verification_report  # noqa: E402

logger = logging.getLogger("supplysight.postgres.init")


def initialize_database() -> None:
    """Run full DB initialization without loading CSVs."""
    logger.info("=== SupplySight AI DB init: schemas ===")
    create_platform_schemas()

    logger.info("=== SupplySight AI DB init: DDL ===")
    execute_schema_files()
    presence = verify_core_tables_exist()
    missing = [name for name, ok in presence.items() if not ok]
    if missing:
        raise RuntimeError(f"Missing public tables: {missing}")

    logger.info("=== SupplySight AI DB init: views ===")
    create_analytics_views()

    logger.info("=== SupplySight AI DB init: materialized views ===")
    create_materialized_views()

    logger.info("=== SupplySight AI DB init: verification ===")
    report = write_verification_report()
    logger.info("Initialization complete. Report: %s", report)
    logger.info("CSV load skipped (use load_normalized_csv.py --execute later).")


def main() -> int:
    setup_module_logging()
    try:
        initialize_database()
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Database initialization failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
