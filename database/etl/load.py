"""
SupplySight AI — ETL Load stage.

Writes normalized DataFrames to CSV under database/normalized_data/.
Does not connect to PostgreSQL.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from config import NORMALIZED_DATA_DIR, PLACEHOLDER_TABLES, POPULATED_TABLES
from transform import TransformResult
from utils import ensure_directory, frame_summary

logger = logging.getLogger("supplysight.etl.load")


class LoadError(Exception):
    """Raised when CSV export fails."""


def _write_dataframe(df: pd.DataFrame, path: Path) -> None:
    """Export a dataframe to UTF-8 CSV."""
    try:
        df.to_csv(path, index=False)
    except OSError as exc:
        raise LoadError(f"Failed to write {path}: {exc}") from exc
    logger.info("Wrote %s (%s)", path.name, frame_summary(path.stem, df))


def export_populated_tables(
    result: TransformResult,
    output_dir: Path = NORMALIZED_DATA_DIR,
) -> list[Path]:
    """
    Export commerce tables populated from DataCo.

    Returns
    -------
    list[Path]
        Paths of written CSV files.
    """
    ensure_directory(output_dir)
    mapping = {
        "departments": result.departments,
        "categories": result.categories,
        "products": result.products,
        "customers": result.customers,
        "orders": result.orders,
        "order_items": result.order_items,
        "shipments": result.shipments,
    }

    written: list[Path] = []
    for table in POPULATED_TABLES:
        path = output_dir / f"{table}.csv"
        _write_dataframe(mapping[table], path)
        written.append(path)
    return written


def export_placeholder_tables(output_dir: Path = NORMALIZED_DATA_DIR) -> list[Path]:
    """
    Create empty CSVs with schema headers for warehouses, inventory, vendors.

    These tables are not present in DataCo and will be populated in a later phase.
    No fabricated business rows are written.
    """
    ensure_directory(output_dir)
    written: list[Path] = []

    for table, columns in PLACEHOLDER_TABLES.items():
        path = output_dir / f"{table}.csv"
        empty = pd.DataFrame(columns=list(columns))
        _write_dataframe(empty, path)
        logger.info(
            "Placeholder CSV created for %s (headers only; populate in later phase)",
            table,
        )
        written.append(path)

    # Side-car note for operators
    note_path = output_dir / "PLACEHOLDER_TABLES.md"
    note_path.write_text(
        (
            "# Placeholder normalized tables\n\n"
            "`warehouses.csv`, `inventory.csv`, and `vendors.csv` contain "
            "**headers only** matching `database/schema/` DDL.\n\n"
            "The DataCo extract has no warehouse, inventory-quantity, or vendor "
            "identifiers. Populate these files in a later phase using synthetic "
            "or external WMS / ERP / SRM datasets.\n"
        ),
        encoding="utf-8",
    )
    logger.info("Wrote operator note: %s", note_path.name)
    return written


def load(result: TransformResult, output_dir: Path = NORMALIZED_DATA_DIR) -> list[Path]:
    """
    Run the full load stage: populated tables + placeholder headers.

    Parameters
    ----------
    result:
        Transform output.
    output_dir:
        Destination directory for CSV artifacts.

    Returns
    -------
    list[Path]
        All CSV paths written.
    """
    logger.info("Starting load -> %s", output_dir)
    paths = export_populated_tables(result, output_dir)
    paths.extend(export_placeholder_tables(output_dir))
    logger.info("Load complete (%s files)", len(paths))
    return paths
