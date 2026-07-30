"""
Post-load validation: null PKs, duplicate PKs, foreign key orphans, row counts.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from loading.config import PRIMARY_KEYS, TARGET_SCHEMA

logger = logging.getLogger("supplysight.postgres.loading.validate")


@dataclass
class ValidationIssue:
    """Single validation finding."""

    table: str
    check: str
    severity: str  # ERROR | WARN | INFO
    detail: str
    count: int = 0


@dataclass
class ValidationReport:
    """Aggregated validation results."""

    row_counts: dict[str, int] = field(default_factory=dict)
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "ERROR")


def fetch_row_counts(conn, tables: tuple[str, ...]) -> dict[str, int]:
    """SELECT COUNT(*) for each table."""
    counts: dict[str, int] = {}
    with conn.cursor() as cur:
        for table in tables:
            cur.execute(f'SELECT COUNT(*) FROM "{TARGET_SCHEMA}"."{table}";')
            counts[table] = int(cur.fetchone()[0])
            logger.info("COUNT %s.%s = %s", TARGET_SCHEMA, table, f"{counts[table]:,}")
    return counts


def validate_null_primary_keys(conn, tables: tuple[str, ...]) -> list[ValidationIssue]:
    """Detect NULL values in primary key columns."""
    issues: list[ValidationIssue] = []
    with conn.cursor() as cur:
        for table in tables:
            pk_cols = PRIMARY_KEYS.get(table)
            if not pk_cols:
                continue
            null_pred = " OR ".join(f'"{c}" IS NULL' for c in pk_cols)
            cur.execute(
                f'SELECT COUNT(*) FROM "{TARGET_SCHEMA}"."{table}" WHERE {null_pred};'
            )
            count = int(cur.fetchone()[0])
            if count > 0:
                issues.append(
                    ValidationIssue(
                        table=table,
                        check="null_primary_key",
                        severity="ERROR",
                        detail=f"NULL in PK columns {pk_cols}",
                        count=count,
                    )
                )
                logger.error("NULL PK in %s: %s row(s)", table, count)
            else:
                logger.info("NULL PK check OK: %s", table)
    return issues


def validate_duplicate_primary_keys(
    conn, tables: tuple[str, ...]
) -> list[ValidationIssue]:
    """Detect duplicate primary key values."""
    issues: list[ValidationIssue] = []
    with conn.cursor() as cur:
        for table in tables:
            pk_cols = PRIMARY_KEYS.get(table)
            if not pk_cols:
                continue
            cols = ", ".join(f'"{c}"' for c in pk_cols)
            cur.execute(
                f"""
                SELECT COUNT(*) FROM (
                    SELECT {cols}, COUNT(*) AS c
                    FROM "{TARGET_SCHEMA}"."{table}"
                    GROUP BY {cols}
                    HAVING COUNT(*) > 1
                ) dups;
                """
            )
            count = int(cur.fetchone()[0])
            if count > 0:
                issues.append(
                    ValidationIssue(
                        table=table,
                        check="duplicate_primary_key",
                        severity="ERROR",
                        detail=f"Duplicate groups on PK {pk_cols}",
                        count=count,
                    )
                )
                logger.error("Duplicate PK groups in %s: %s", table, count)
            else:
                logger.info("Duplicate PK check OK: %s", table)
    return issues


def validate_foreign_keys(conn) -> list[ValidationIssue]:
    """
    Validate known FK relationships for the commerce model.

    Uses explicit checks (portable) rather than disabling constraints.
    """
    issues: list[ValidationIssue] = []
    checks = [
        (
            "categories",
            "department_id",
            "departments",
            "department_id",
        ),
        (
            "products",
            "category_id",
            "categories",
            "category_id",
        ),
        (
            "orders",
            "customer_id",
            "customers",
            "customer_id",
        ),
        (
            "order_items",
            "order_id",
            "orders",
            "order_id",
        ),
        (
            "order_items",
            "product_id",
            "products",
            "product_id",
        ),
        (
            "shipments",
            "order_id",
            "orders",
            "order_id",
        ),
        (
            "inventory",
            "warehouse_id",
            "warehouses",
            "warehouse_id",
        ),
        (
            "inventory",
            "product_id",
            "products",
            "product_id",
        ),
        (
            "vendor_products",
            "vendor_id",
            "vendors",
            "vendor_id",
        ),
        (
            "vendor_products",
            "product_id",
            "products",
            "product_id",
        ),
    ]

    with conn.cursor() as cur:
        for child, child_col, parent, parent_col in checks:
            sql = f"""
                SELECT COUNT(*)
                FROM "{TARGET_SCHEMA}"."{child}" AS c
                LEFT JOIN "{TARGET_SCHEMA}"."{parent}" AS p
                  ON c."{child_col}" = p."{parent_col}"
                WHERE c."{child_col}" IS NOT NULL
                  AND p."{parent_col}" IS NULL;
            """
            cur.execute(sql)
            count = int(cur.fetchone()[0])
            label = f"{child}.{child_col} -> {parent}.{parent_col}"
            if count > 0:
                issues.append(
                    ValidationIssue(
                        table=child,
                        check="foreign_key",
                        severity="ERROR",
                        detail=f"Orphan FK values for {label}",
                        count=count,
                    )
                )
                logger.error("FK orphans %s: %s", label, count)
            else:
                logger.info("FK check OK: %s", label)
    return issues


def run_validations(conn, tables: tuple[str, ...]) -> ValidationReport:
    """Run all post-load validations and collect row counts."""
    report = ValidationReport()
    report.row_counts = fetch_row_counts(conn, tables)
    report.issues.extend(validate_null_primary_keys(conn, tables))
    report.issues.extend(validate_duplicate_primary_keys(conn, tables))
    report.issues.extend(validate_foreign_keys(conn))
    logger.info(
        "Validation complete: errors=%s issues=%s",
        report.error_count,
        len(report.issues),
    )
    return report
