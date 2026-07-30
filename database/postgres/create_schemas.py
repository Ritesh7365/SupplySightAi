"""
SupplySight AI — Create logical PostgreSQL schemas.

Ensures staging, warehouse, analytics, and ml schemas exist.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Allow running as a script from any CWD
_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from connection import (  # noqa: E402
    PLATFORM_SCHEMAS,
    ensure_schema,
    get_connection,
    schema_exists,
    setup_module_logging,
)

logger = logging.getLogger("supplysight.postgres.schemas")


def create_platform_schemas() -> dict[str, bool]:
    """
    Create all platform schemas if missing.

    Returns
    -------
    dict[str, bool]
        Mapping of schema name → whether it existed before this run.
    """
    results: dict[str, bool] = {}
    with get_connection(autocommit=True) as conn:
        for name in PLATFORM_SCHEMAS:
            existed = schema_exists(name, conn=conn)
            ensure_schema(name, conn=conn)
            results[name] = existed
            status = "already existed" if existed else "created"
            logger.info("Schema '%s' %s", name, status)
    return results


def main() -> int:
    """CLI entrypoint."""
    setup_module_logging()
    logger.info("Creating platform schemas: %s", ", ".join(PLATFORM_SCHEMAS))
    try:
        create_platform_schemas()
        logger.info("Schema creation complete")
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to create schemas: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
