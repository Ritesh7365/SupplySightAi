"""
SQLAlchemy engine and session factory with connection pooling.

Read-only analytics traffic reuses a QueuePool sized via settings.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Optional

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.core.logging import get_logger

logger = get_logger("database")

_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker[Session]] = None


def create_db_engine(settings: Optional[Settings] = None) -> Engine:
    """Create a pooled SQLAlchemy engine for PostgreSQL."""
    cfg = settings or get_settings()
    engine = create_engine(
        cfg.sqlalchemy_database_uri,
        pool_size=cfg.db_pool_size,
        max_overflow=cfg.db_max_overflow,
        pool_timeout=cfg.db_pool_timeout,
        pool_recycle=cfg.db_pool_recycle,
        pool_pre_ping=True,
        pool_use_lifo=True,
        echo=cfg.db_echo,
        future=True,
        connect_args={
            "application_name": "supplysight_api",
            "connect_timeout": 10,
        },
    )

    @event.listens_for(engine, "checkout")
    def _on_checkout(dbapi_connection, connection_record, connection_proxy):  # noqa: ANN001
        logger.debug("DB pool checkout")

    logger.info(
        "SQLAlchemy engine created (pool_size=%s, max_overflow=%s, pool_recycle=%s, pre_ping=True)",
        cfg.db_pool_size,
        cfg.db_max_overflow,
        cfg.db_pool_recycle,
    )
    return engine


def init_db(settings: Optional[Settings] = None) -> Engine:
    """Initialize global engine + session factory (idempotent)."""
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_db_engine(settings)
        _SessionLocal = sessionmaker(
            bind=_engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=Session,
        )
    return _engine


def get_engine() -> Engine:
    """Return the process-wide engine, initializing if needed."""
    if _engine is None:
        return init_db()
    return _engine


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a DB session.

    Commits are not performed automatically (read-heavy API). On exception the
    session is rolled back; the connection is always closed / returned to pool.
    """
    if _SessionLocal is None:
        init_db()
    assert _SessionLocal is not None

    db = _SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_db_connection() -> bool:
    """Run a lightweight connectivity check against PostgreSQL."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True


def get_pool_status() -> dict[str, int | str | None]:
    """Return best-effort pool statistics for health endpoints."""
    engine = get_engine()
    pool = engine.pool
    status: dict[str, int | str | None] = {
        "pool_class": pool.__class__.__name__,
    }
    for attr in ("size", "checkedin", "checkedout", "overflow"):
        method = getattr(pool, attr, None)
        if callable(method):
            try:
                status[attr] = int(method())
            except Exception:  # noqa: BLE001
                status[attr] = None
    return status


def dispose_engine() -> None:
    """Dispose the global engine (used on shutdown)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
        logger.info("SQLAlchemy engine disposed")
    _engine = None
    _SessionLocal = None
