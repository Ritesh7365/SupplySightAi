"""
SupplySight AI — Execute numbered DDL files from database/schema/.

Applies CREATE TABLE / INDEX scripts into the ``public`` schema.
The ``warehouse`` schema remains empty for a later fact/dimension phase.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from connection import (  # noqa: E402
    CORE_TABLES,
    DDL_TARGET_SCHEMA,
    SCHEMA_DIR,
    get_connection,
    list_sql_files,
    run_sql_file,
    set_search_path,
    setup_module_logging,
    table_exists,
)

logger = logging.getLogger("supplysight.postgres.execute_schema")


def execute_schema_files(schema_dir: Path = SCHEMA_DIR) -> list[str]:
    """
    Execute every ``.sql`` file in ``schema_dir`` in sorted order.

    Tables are created in the ``public`` schema.

    Returns
    -------
    list[str]
        Names of SQL files executed.
    """
    files = list_sql_files(schema_dir)
    if not files:
        raise FileNotFoundError(f"No SQL files found in {schema_dir}")

    executed: list[str] = []
    with get_connection(autocommit=False) as conn:
        # Explicit public target; warehouse intentionally unused for DDL
        set_search_path([DDL_TARGET_SCHEMA], conn=conn)
        for path in files:
            logger.info("Applying %s into schema '%s' ...", path.name, DDL_TARGET_SCHEMA)
            run_sql_file(path, conn=conn)
            executed.append(path.name)
        conn.commit()

    logger.info("Executed %s SQL file(s) into %s", len(executed), DDL_TARGET_SCHEMA)
    return executed


def verify_core_tables_exist() -> dict[str, bool]:
    """Check that expected public tables exist after DDL."""
    presence: dict[str, bool] = {}
    with get_connection(autocommit=True) as conn:
        for table in CORE_TABLES:
            presence[table] = table_exists(DDL_TARGET_SCHEMA, table, conn=conn)
            logger.info(
                "Table %s.%s: %s",
                DDL_TARGET_SCHEMA,
                table,
                "OK" if presence[table] else "MISSING",
            )
    return presence


def main() -> int:
    """CLI entrypoint."""
    setup_module_logging()
    logger.info(
        "Executing schema files from %s into schema '%s'",
        SCHEMA_DIR,
        DDL_TARGET_SCHEMA,
    )
    try:
        executed = execute_schema_files()
        presence = verify_core_tables_exist()
        missing = [t for t, ok in presence.items() if not ok]
        if missing:
            logger.error("Missing tables after DDL: %s", ", ".join(missing))
            return 1
        logger.info("Schema execution complete (%s files)", len(executed))
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Schema execution failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
