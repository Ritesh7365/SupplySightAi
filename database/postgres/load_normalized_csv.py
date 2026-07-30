"""
SupplySight AI — Load normalized CSVs into PostgreSQL ``public`` schema.

Enterprise entrypoint. Delegates to ``loading.pipeline``.

Usage:
  python database/postgres/load_normalized_csv.py
  python database/postgres/load_normalized_csv.py --execute   # same (enabled)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from connection import setup_module_logging  # noqa: E402
from loading.pipeline import run_load_pipeline  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """CLI — loads normalized CSVs (raw DataCo is never loaded)."""
    setup_module_logging()
    parser = argparse.ArgumentParser(
        description=(
            "Load database/normalized_data/*.csv into PostgreSQL public schema "
            "using COPY (INSERT fallback), with validation and load_report.md."
        )
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        default=True,
        help="Execute the load (default: enabled).",
    )
    parser.add_argument(
        "--no-truncate",
        action="store_true",
        help="Skip TRUNCATE before load (not recommended for idempotent runs).",
    )
    args = parser.parse_args(argv)

    if not args.execute:
        print("Load disabled.")
        return 0

    return run_load_pipeline(truncate=not args.no_truncate)


if __name__ == "__main__":
    raise SystemExit(main())
