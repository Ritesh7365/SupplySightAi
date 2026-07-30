"""
SupplySight AI — Database verification and report generation.

Inspects schemas, tables, keys, indexes, and row counts. Writes a Markdown
verification report under database/postgres/reports/.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_PKG = Path(__file__).resolve().parent
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

from connection import (  # noqa: E402
    CORE_TABLES,
    DDL_TARGET_SCHEMA,
    PLATFORM_SCHEMAS,
    REPORTS_DIR,
    get_connection,
    setup_module_logging,
)

logger = logging.getLogger("supplysight.postgres.verify")


def _fetch_all(query: str, params: tuple[Any, ...] | None = None) -> list[tuple]:
    with get_connection(autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return list(cur.fetchall())


def list_tables(schema: str = DDL_TARGET_SCHEMA) -> list[str]:
    """Return base table names in a schema."""
    rows = _fetch_all(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE'
        ORDER BY table_name;
        """,
        (schema,),
    )
    return [r[0] for r in rows]


def list_primary_keys(schema: str = DDL_TARGET_SCHEMA) -> list[dict[str, str]]:
    """Return primary key constraints for a schema."""
    rows = _fetch_all(
        """
        SELECT
            tc.table_name,
            tc.constraint_name,
            string_agg(kcu.column_name, ', ' ORDER BY kcu.ordinal_position) AS columns
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.table_schema = %s
          AND tc.constraint_type = 'PRIMARY KEY'
        GROUP BY tc.table_name, tc.constraint_name
        ORDER BY tc.table_name;
        """,
        (schema,),
    )
    return [
        {"table": r[0], "constraint": r[1], "columns": r[2]}
        for r in rows
    ]


def list_foreign_keys(schema: str = DDL_TARGET_SCHEMA) -> list[dict[str, str]]:
    """Return foreign key relationships for a schema."""
    rows = _fetch_all(
        """
        SELECT
            tc.table_name AS child_table,
            kcu.column_name AS child_column,
            ccu.table_name AS parent_table,
            ccu.column_name AS parent_column,
            tc.constraint_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema = tc.table_schema
        WHERE tc.table_schema = %s
          AND tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name, tc.constraint_name;
        """,
        (schema,),
    )
    return [
        {
            "child_table": r[0],
            "child_column": r[1],
            "parent_table": r[2],
            "parent_column": r[3],
            "constraint": r[4],
        }
        for r in rows
    ]


def list_indexes(schema: str = DDL_TARGET_SCHEMA) -> list[dict[str, str]]:
    """Return indexes for tables in a schema."""
    rows = _fetch_all(
        """
        SELECT
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = %s
        ORDER BY tablename, indexname;
        """,
        (schema,),
    )
    return [
        {"table": r[0], "index": r[1], "definition": r[2]}
        for r in rows
    ]


def table_row_counts(schema: str = DDL_TARGET_SCHEMA) -> list[dict[str, Any]]:
    """
    Count rows per table.

    Before CSV load, counts are expected to be zero. After a future load step,
    this function reports post-load volumes.
    """
    tables = list_tables(schema)
    counts: list[dict[str, Any]] = []
    with get_connection(autocommit=True) as conn:
        with conn.cursor() as cur:
            for table in tables:
                cur.execute(
                    f'SELECT COUNT(*) FROM "{schema}"."{table}";'  # noqa: S608
                )
                count = int(cur.fetchone()[0])
                counts.append({"table": table, "row_count": count})
    return counts


def list_schemas_present() -> list[str]:
    """Return platform schemas that currently exist."""
    present = []
    rows = _fetch_all(
        """
        SELECT schema_name
        FROM information_schema.schemata
        WHERE schema_name = ANY(%s)
        ORDER BY schema_name;
        """,
        (list(PLATFORM_SCHEMAS),),
    )
    present = [r[0] for r in rows]
    return present


def build_verification_report() -> str:
    """Compose a Markdown verification report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    schemas = list_schemas_present()
    tables = list_tables(DDL_TARGET_SCHEMA)
    pks = list_primary_keys(DDL_TARGET_SCHEMA)
    fks = list_foreign_keys(DDL_TARGET_SCHEMA)
    indexes = list_indexes(DDL_TARGET_SCHEMA)
    counts = table_row_counts(DDL_TARGET_SCHEMA)

    expected_missing = [t for t in CORE_TABLES if t not in tables]

    lines: list[str] = [
        "# SupplySight AI — Database Verification Report",
        "",
        f"**Generated:** {now}",
        f"**DDL target schema:** `{DDL_TARGET_SCHEMA}`",
        "",
        "## 1. Schemas",
        "",
        "| Schema | Present | Notes |",
        "|--------|---------|-------|",
    ]
    schema_notes = {
        "staging": "Reserved for landing loads",
        "warehouse": "Reserved for future fact/dimension tables (empty for now)",
        "analytics": "Views and materialized views",
        "ml": "Reserved for ML feature/scoring tables",
    }
    for name in PLATFORM_SCHEMAS:
        note = schema_notes.get(name, "")
        lines.append(f"| `{name}` | {'Yes' if name in schemas else 'No'} | {note} |")

    lines.extend(
        [
            "",
            "## 2. Tables Created",
            "",
            f"Found **{len(tables)}** base table(s) in `{DDL_TARGET_SCHEMA}`.",
            "",
            "| Table | Status |",
            "|-------|--------|",
        ]
    )
    for table in CORE_TABLES:
        status = "CREATED" if table in tables else "MISSING"
        lines.append(f"| `{DDL_TARGET_SCHEMA}.{table}` | {status} |")
    extras = [t for t in tables if t not in CORE_TABLES]
    for table in extras:
        lines.append(f"| `{DDL_TARGET_SCHEMA}.{table}` | CREATED (extra) |")

    if expected_missing:
        lines.append("")
        lines.append(
            f"**Missing expected tables:** {', '.join(f'`{t}`' for t in expected_missing)}"
        )

    lines.extend(["", "## 3. Primary Keys", "", "| Table | Constraint | Columns |", "|-------|------------|---------|"])
    for pk in pks:
        lines.append(f"| `{pk['table']}` | `{pk['constraint']}` | `{pk['columns']}` |")
    if not pks:
        lines.append("| — | — | — |")

    lines.extend(
        [
            "",
            "## 4. Foreign Keys",
            "",
            "| Child | Column | Parent | Column | Constraint |",
            "|-------|--------|--------|--------|------------|",
        ]
    )
    for fk in fks:
        lines.append(
            f"| `{fk['child_table']}` | `{fk['child_column']}` | "
            f"`{fk['parent_table']}` | `{fk['parent_column']}` | `{fk['constraint']}` |"
        )
    if not fks:
        lines.append("| — | — | — | — | — |")

    lines.extend(
        [
            "",
            "## 5. Indexes",
            "",
            "| Table | Index |",
            "|-------|-------|",
        ]
    )
    for idx in indexes:
        lines.append(f"| `{idx['table']}` | `{idx['index']}` |")
    if not indexes:
        lines.append("| — | — |")

    lines.extend(
        [
            "",
            "## 6. Row Counts",
            "",
            "_Counts reflect current table contents. Before CSV load they should be 0._",
            "",
            "| Table | Row Count |",
            "|-------|-----------|",
        ]
    )
    for row in counts:
        lines.append(f"| `{DDL_TARGET_SCHEMA}.{row['table']}` | {row['row_count']:,} |")
    if not counts:
        lines.append("| — | — |")

    lines.extend(
        [
            "",
            "## 7. Summary",
            "",
            f"- Platform schemas present: **{len(schemas)}/{len(PLATFORM_SCHEMAS)}**",
            f"- Expected `{DDL_TARGET_SCHEMA}` tables present: "
            f"**{len(CORE_TABLES) - len(expected_missing)}/{len(CORE_TABLES)}**",
            f"- Primary keys: **{len(pks)}**",
            f"- Foreign keys: **{len(fks)}**",
            f"- Indexes: **{len(indexes)}**",
            f"- `warehouse` schema: reserved / empty (no DDL applied here)",
            "",
            "---",
            "",
            "*Generated by `database/postgres/verify_database.py`*",
            "",
        ]
    )
    return "\n".join(lines)


def write_verification_report(
    output_path: Path | None = None,
) -> Path:
    """Build and persist the verification report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = output_path or (REPORTS_DIR / "verification_report.md")
    content = build_verification_report()
    path.write_text(content, encoding="utf-8")
    logger.info("Verification report written: %s", path)
    return path


def main() -> int:
    """CLI entrypoint."""
    setup_module_logging()
    try:
        path = write_verification_report()
        tables = list_tables()
        missing = [t for t in CORE_TABLES if t not in tables]
        if missing:
            logger.error("Verification found missing tables: %s", missing)
            logger.info("Report available at %s", path)
            return 1
        logger.info("Verification succeeded — report: %s", path)
        return 0
    except Exception as exc:  # noqa: BLE001
        logger.exception("Verification failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
