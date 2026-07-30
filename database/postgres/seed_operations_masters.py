"""
CLI: seed synthetic warehouses / inventory / vendors into public schema.

Usage:
  python database/postgres/seed_operations_masters.py
  python database/postgres/seed_operations_masters.py --vendors 55
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from connection import (  # noqa: E402
    SCHEMA_DIR,
    get_connection,
    run_sql_file,
    setup_module_logging,
)
from loading.seed_operations_masters import (  # noqa: E402
    counts,
    seed_operations_masters,
)

logger = logging.getLogger("supplysight.postgres.seed_ops.cli")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed synthetic operations master data")
    parser.add_argument("--vendors", type=int, default=50, help="Vendor count (40–60 recommended)")
    parser.add_argument("--seed", type=int, default=20260730, help="RNG seed for reproducibility")
    args = parser.parse_args()

    setup_module_logging()
    ext_sql = SCHEMA_DIR / "12_ops_master_extensions.sql"
    try:
        with get_connection(autocommit=False) as conn:
            if ext_sql.exists():
                logger.info("Applying %s", ext_sql.name)
                run_sql_file(ext_sql, conn=conn)
            result = seed_operations_masters(
                conn,
                vendor_count=max(40, min(args.vendors, 60)),
                rng_seed=args.seed,
            )
            c = counts(conn)
        logger.info("Done: %s", result)
        logger.info("Counts: %s", c)
        if any(v <= 0 for v in c.values()):
            logger.error("One or more operations tables are still empty")
            return 1
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Operations seed failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
