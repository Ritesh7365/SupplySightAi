"""
SupplySight AI — PostgreSQL connection and migration helpers.

Loads credentials from environment variables and exposes reusable utilities
for schema initialization, SQL execution, and future migrations.
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Iterable, Optional, Sequence

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection as PgConnection
from psycopg2.extensions import cursor as PgCursor

logger = logging.getLogger("supplysight.postgres")

# Project paths
POSTGRES_DIR: Path = Path(__file__).resolve().parent
DATABASE_DIR: Path = POSTGRES_DIR.parent
PROJECT_ROOT: Path = DATABASE_DIR.parent
SCHEMA_DIR: Path = DATABASE_DIR / "schema"
NORMALIZED_DATA_DIR: Path = DATABASE_DIR / "normalized_data"
REPORTS_DIR: Path = POSTGRES_DIR / "reports"

# Logical schemas for the platform
PLATFORM_SCHEMAS: tuple[str, ...] = (
    "staging",
    "warehouse",
    "analytics",
    "ml",
)

# Schema that receives DDL from database/schema/ (warehouse reserved for later)
DDL_TARGET_SCHEMA: str = "public"

# Core commerce tables expected in public after DDL apply
CORE_TABLES: tuple[str, ...] = (
    "departments",
    "categories",
    "products",
    "customers",
    "orders",
    "order_items",
    "shipments",
    "warehouses",
    "inventory",
    "vendors",
    "vendor_products",
)

# Backwards-compatible alias
WAREHOUSE_TABLES = CORE_TABLES


def load_dotenv_if_available() -> None:
    """Load `.env` from the project root when python-dotenv is installed."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        logger.warning("python-dotenv not installed; relying on process environment")
        return

    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        logger.info("Loaded environment from %s", env_path)
    else:
        # Do not load .env.example secrets; only document expected keys there.
        logger.warning(
            "No .env file at %s — using process environment variables only",
            env_path,
        )


def get_database_config() -> dict[str, Any]:
    """
    Build a psycopg2 connection keyword dict from environment variables.

    Supported variables:
      POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
      or DATABASE_URL (postgresql:// / postgresql+psycopg2://)
    """
    load_dotenv_if_available()

    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        # Normalize SQLAlchemy-style URL for psycopg2
        url = database_url.replace("postgresql+psycopg2://", "postgresql://")
        return {"dsn": url}

    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB", "supplysight_ai"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
    }


def connect(autocommit: bool = False) -> PgConnection:
    """
    Open a new PostgreSQL connection.

    Parameters
    ----------
    autocommit:
        When True, each statement commits immediately (useful for DDL).
    """
    cfg = get_database_config()
    safe_cfg = {k: v for k, v in cfg.items() if k != "password"}
    logger.info("Connecting to PostgreSQL with config=%s", safe_cfg)
    conn = psycopg2.connect(**cfg)
    conn.autocommit = autocommit
    return conn


@contextmanager
def get_connection(autocommit: bool = False) -> Generator[PgConnection, None, None]:
    """Context-managed PostgreSQL connection (closes on exit)."""
    conn = connect(autocommit=autocommit)
    try:
        yield conn
        if not autocommit:
            conn.commit()
    except Exception:
        if not autocommit:
            conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor(
    conn: Optional[PgConnection] = None,
    *,
    autocommit: bool = False,
) -> Generator[PgCursor, None, None]:
    """
    Yield a cursor. If ``conn`` is omitted, open a short-lived connection.
    """
    owns_connection = conn is None
    active = conn or connect(autocommit=autocommit)
    cur = active.cursor()
    try:
        yield cur
        if owns_connection and not active.autocommit:
            active.commit()
    except Exception:
        if owns_connection and not active.autocommit:
            active.rollback()
        raise
    finally:
        cur.close()
        if owns_connection:
            active.close()


def execute_sql(
    statement: str,
    params: Optional[Sequence[Any]] = None,
    *,
    conn: Optional[PgConnection] = None,
) -> None:
    """Execute a single SQL statement (reusable for migrations)."""
    with get_cursor(conn, autocommit=conn is None) as cur:
        cur.execute(statement, params)


def execute_sql_script(script: str, *, conn: Optional[PgConnection] = None) -> None:
    """
    Execute a multi-statement SQL script.

    Uses psycopg2's ability to run multiple statements in one execute call.
    """
    cleaned = script.strip()
    if not cleaned:
        return
    with get_cursor(conn, autocommit=False if conn else True) as cur:
        cur.execute(cleaned)


def run_sql_file(path: Path, *, conn: Optional[PgConnection] = None) -> None:
    """
    Read and execute a ``.sql`` file (reusable migration helper).

    Parameters
    ----------
    path:
        Absolute path to a SQL file.
    conn:
        Optional existing connection; otherwise a new one is opened.
    """
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    logger.info("Executing SQL file: %s", path.name)
    script = path.read_text(encoding="utf-8")
    execute_sql_script(script, conn=conn)


def table_exists(schema: str, table: str, *, conn: Optional[PgConnection] = None) -> bool:
    """Return True if ``schema.table`` exists."""
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = %s
              AND table_name = %s
        );
    """
    with get_cursor(conn) as cur:
        cur.execute(query, (schema, table))
        row = cur.fetchone()
        return bool(row and row[0])


def schema_exists(schema: str, *, conn: Optional[PgConnection] = None) -> bool:
    """Return True if a PostgreSQL schema exists."""
    query = """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.schemata
            WHERE schema_name = %s
        );
    """
    with get_cursor(conn) as cur:
        cur.execute(query, (schema,))
        row = cur.fetchone()
        return bool(row and row[0])


def ensure_schema(schema: str, *, conn: Optional[PgConnection] = None) -> None:
    """Create a schema if it does not already exist (idempotent)."""
    # Identifier cannot be parameterized; validate then quote.
    if not schema.replace("_", "").isalnum():
        raise ValueError(f"Invalid schema name: {schema}")
    statement = sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
        sql.Identifier(schema)
    )
    with get_cursor(conn, autocommit=True if conn is None else conn.autocommit) as cur:
        cur.execute(statement)
    logger.info("Schema ready: %s", schema)


def set_search_path(schemas: Iterable[str], *, conn: PgConnection) -> None:
    """Set session ``search_path`` for subsequent DDL/DML."""
    idents = [sql.Identifier(s) for s in schemas]
    statement = sql.SQL("SET search_path TO {}").format(
        sql.SQL(", ").join(idents)
    )
    with conn.cursor() as cur:
        cur.execute(statement)


def list_sql_files(directory: Path = SCHEMA_DIR) -> list[Path]:
    """
    Return ``*.sql`` files in numeric / lexical order.

    Skips README or non-numbered helpers that do not end in ``.sql``.
    """
    files = sorted(directory.glob("*.sql"))
    return [f for f in files if f.is_file()]


def setup_module_logging(level: int = logging.INFO) -> None:
    """Configure console logging for postgres package scripts."""
    root = logging.getLogger("supplysight.postgres")
    if root.handlers:
        return
    root.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    )
    root.addHandler(handler)
    root.propagate = False
