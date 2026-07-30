"""
CSV → PostgreSQL loaders (COPY preferred, batch INSERT fallback).
"""

from __future__ import annotations

import csv
import io
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from psycopg2.extras import execute_batch
from tqdm import tqdm

from loading.config import ALLOW_EMPTY, CSV_DIR, TARGET_SCHEMA

logger = logging.getLogger("supplysight.postgres.loading.copy")


@dataclass
class TableLoadResult:
    """Outcome of loading a single table."""

    table: str
    csv_path: Path
    method: str  # COPY | INSERT | SKIPPED_EMPTY | SKIPPED_MISSING
    rows_in_csv: int = 0
    rows_inserted: int = 0
    rows_skipped: int = 0
    elapsed_seconds: float = 0.0
    error: Optional[str] = None
    notes: list[str] = field(default_factory=list)


def csv_path_for(table: str) -> Path:
    """Return expected CSV path for a table."""
    return CSV_DIR / f"{table}.csv"


def count_csv_data_rows(path: Path) -> int:
    """Count data rows (excluding header) without loading full file into memory."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)  # header
        return sum(1 for _ in reader)


def read_csv_header(path: Path) -> list[str]:
    """Return CSV column headers."""
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
    return list(header)


def truncate_tables(conn, tables: tuple[str, ...]) -> None:
    """
    Truncate target tables in FK-safe reverse order.

    Uses CASCADE so dependent rows are cleared atomically within the transaction.
    """
    with conn.cursor() as cur:
        for table in tables:
            sql = f'TRUNCATE TABLE "{TARGET_SCHEMA}"."{table}" RESTART IDENTITY CASCADE;'
            logger.info("TRUNCATE %s.%s", TARGET_SCHEMA, table)
            cur.execute(sql)


def prepare_schema_for_source_data(conn) -> None:
    """
    Align constraints with known DataCo realities (no business-value changes).

    DataCo contains two Category Id values sharing the name ``Electronics``.
    Drop UNIQUE(category_name) if present so the load can proceed.
    """
    with conn.cursor() as cur:
        cur.execute(
            f'ALTER TABLE "{TARGET_SCHEMA}"."categories" '
            f"DROP CONSTRAINT IF EXISTS uq_categories_name;"
        )
    logger.info("Ensured categories allows duplicate category_name (DataCo-compatible)")


def _copy_csv(conn, table: str, path: Path, columns: list[str]) -> int:
    """
    Load via PostgreSQL COPY FROM STDIN (client-side file stream).

    Returns rows reported by the cursor after COPY.
    """
    col_sql = ", ".join(f'"{c}"' for c in columns)
    copy_sql = (
        f'COPY "{TARGET_SCHEMA}"."{table}" ({col_sql}) '
        f"FROM STDIN WITH (FORMAT csv, HEADER true, NULL '')"
    )
    with path.open("r", encoding="utf-8", newline="") as handle:
        with conn.cursor() as cur:
            cur.copy_expert(copy_sql, handle)
            # rowcount is set for COPY in psycopg2
            return max(cur.rowcount or 0, 0)


def _insert_csv(conn, table: str, path: Path, columns: list[str]) -> int:
    """
    Fallback batch INSERT using csv module (no pandas transform of values).
    """
    col_sql = ", ".join(f'"{c}"' for c in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    insert_sql = (
        f'INSERT INTO "{TARGET_SCHEMA}"."{table}" ({col_sql}) VALUES ({placeholders})'
    )

    rows: list[tuple] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for record in reader:
            values = []
            for col in columns:
                raw = record.get(col, "")
                if raw is None or raw == "":
                    values.append(None)
                else:
                    values.append(raw)
            rows.append(tuple(values))

    if not rows:
        return 0

    with conn.cursor() as cur:
        # Progress in chunks for large facts
        page = 1000
        for start in tqdm(
            range(0, len(rows), page),
            desc=f"INSERT {table}",
            unit="batch",
            leave=False,
        ):
            chunk = rows[start : start + page]
            execute_batch(cur, insert_sql, chunk, page_size=page)
    return len(rows)


def load_table(conn, table: str) -> TableLoadResult:
    """
    Load one normalized CSV into ``public.<table>``.

    Prefers COPY; falls back to batch INSERT on COPY failure (same transaction
    continues only if caller handles rollback — this function re-raises after
    recording context when both methods fail).
    """
    path = csv_path_for(table)
    result = TableLoadResult(table=table, csv_path=path, method="PENDING")

    if not path.exists():
        result.method = "SKIPPED_MISSING"
        result.error = f"CSV not found: {path}"
        result.notes.append("File missing — create header CSV or regenerate ETL output")
        logger.error(result.error)
        raise FileNotFoundError(result.error)

    started = time.perf_counter()
    row_count = count_csv_data_rows(path)
    result.rows_in_csv = row_count

    if row_count == 0:
        result.method = "SKIPPED_EMPTY"
        result.elapsed_seconds = time.perf_counter() - started
        if table in ALLOW_EMPTY:
            result.notes.append("Empty placeholder CSV — 0 rows loaded (expected)")
            logger.info("Table %s: empty CSV, skipping insert", table)
            return result
        result.notes.append("Empty CSV for non-placeholder table")
        logger.warning("Table %s: empty CSV", table)
        return result

    columns = read_csv_header(path)
    if not columns:
        result.method = "SKIPPED_MISSING"
        result.error = "CSV has no header"
        raise ValueError(result.error)

    # Prefer COPY
    try:
        logger.info("COPY %s.%s from %s (%s rows)", TARGET_SCHEMA, table, path.name, f"{row_count:,}")
        inserted = _copy_csv(conn, table, path, columns)
        result.method = "COPY"
        result.rows_inserted = inserted if inserted else row_count
        result.elapsed_seconds = time.perf_counter() - started
        logger.info(
            "COPY OK %s: inserted=%s elapsed=%.2fs",
            table,
            f"{result.rows_inserted:,}",
            result.elapsed_seconds,
        )
        return result
    except Exception as copy_exc:  # noqa: BLE001
        logger.warning("COPY failed for %s (%s); falling back to INSERT", table, copy_exc)
        result.notes.append(f"COPY failed: {copy_exc}")
        # Important: COPY failure aborts the current transaction in PostgreSQL.
        # Caller must rollback and retry table with INSERT in a fresh subtransaction,
        # or we use a savepoint here.
        raise  # handled by pipeline with savepoints


def load_table_with_fallback(conn, table: str) -> TableLoadResult:
    """
    Load a table using a SAVEPOINT so COPY failure can fall back to INSERT
    without aborting the outer transaction.
    """
    path = csv_path_for(table)
    result = TableLoadResult(table=table, csv_path=path, method="PENDING")

    if not path.exists():
        result.method = "SKIPPED_MISSING"
        result.error = f"CSV not found: {path}"
        logger.error(result.error)
        raise FileNotFoundError(result.error)

    started = time.perf_counter()
    row_count = count_csv_data_rows(path)
    result.rows_in_csv = row_count
    columns = read_csv_header(path)

    if row_count == 0:
        result.method = "SKIPPED_EMPTY"
        result.elapsed_seconds = time.perf_counter() - started
        note = (
            "Empty placeholder CSV — 0 rows loaded (expected)"
            if table in ALLOW_EMPTY
            else "Empty CSV"
        )
        result.notes.append(note)
        logger.info("Table %s: %s", table, note)
        return result

    savepoint = f"sp_load_{table}"
    with conn.cursor() as cur:
        cur.execute(f"SAVEPOINT {savepoint}")

    try:
        logger.info(
            "Loading %s.%s via COPY (%s rows)",
            TARGET_SCHEMA,
            table,
            f"{row_count:,}",
        )
        inserted = _copy_csv(conn, table, path, columns)
        result.method = "COPY"
        result.rows_inserted = inserted if inserted else row_count
        with conn.cursor() as cur:
            cur.execute(f"RELEASE SAVEPOINT {savepoint}")
    except Exception as copy_exc:  # noqa: BLE001
        logger.warning("COPY failed for %s: %s", table, copy_exc)
        result.notes.append(f"COPY failed: {copy_exc}")
        with conn.cursor() as cur:
            cur.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")

        try:
            logger.info("Retrying %s via batch INSERT", table)
            inserted = _insert_csv(conn, table, path, columns)
            result.method = "INSERT"
            result.rows_inserted = inserted
            with conn.cursor() as cur:
                cur.execute(f"RELEASE SAVEPOINT {savepoint}")
        except Exception as insert_exc:  # noqa: BLE001
            with conn.cursor() as cur:
                cur.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
            result.method = "FAILED"
            result.error = str(insert_exc)
            result.elapsed_seconds = time.perf_counter() - started
            logger.error("INSERT failed for %s: %s", table, insert_exc)
            raise

    result.elapsed_seconds = time.perf_counter() - started
    # Skipped = CSV rows not reflected in insert count (should be 0 on success)
    if result.rows_inserted < result.rows_in_csv:
        result.rows_skipped = result.rows_in_csv - result.rows_inserted
    logger.info(
        "Loaded %s method=%s inserted=%s skipped=%s elapsed=%.2fs",
        table,
        result.method,
        f"{result.rows_inserted:,}",
        result.rows_skipped,
        result.elapsed_seconds,
    )
    return result


def ensure_vendor_products_csv() -> Path:
    """Ensure vendor_products.csv exists with schema headers (empty placeholder)."""
    from loading.config import VENDOR_PRODUCTS_HEADERS

    path = csv_path_for("vendor_products")
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(list(VENDOR_PRODUCTS_HEADERS))
    logger.info("Created empty placeholder CSV: %s", path)
    return path
