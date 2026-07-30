# Backend Architecture — SupplySight AI

## Overview

The FastAPI backend is a **read-only analytics API** over PostgreSQL. Business
endpoints query the ``analytics`` schema only (views / materialized views).
Infrastructure concerns (middleware, pooling, errors, health) are layered
around those services without changing query logic.

```
Client
  │
  ▼
GZip → CORS → ResponseHeaders → RequestTiming → RequestId
  │
  ▼
FastAPI routers (health @ /, API @ /api/v1)
  │
  ▼
Services → SQLAlchemy Session (pooled) → analytics.*
```

## Package layout

| Package | Responsibility |
|---------|----------------|
| `app.main` | App factory, lifespan, middleware stack |
| `app.api` | Versioned router aggregation |
| `app.routers` | HTTP endpoints |
| `app.services` | Analytics query orchestration |
| `app.models` | SQLAlchemy mappings to analytics views |
| `app.schemas` | Pydantic request/response models |
| `app.database` | Engine, pool, session dependency |
| `app.middleware` | Request ID, timing/logging, headers |
| `app.core` | Config, logging, exceptions, OpenAPI meta, auth stubs |
| `app.utils` | Pagination and row helpers |

## Runtime entrypoint

From the **`backend/`** directory:

```bash
python -m uvicorn app.main:app --reload
```

## Configuration

Settings load from project-root `.env` via `pydantic-settings`
(`app.core.config.Settings`):

- API: `API_PREFIX`, `CORS_ORIGINS`, `LOG_LEVEL`
- DB: `POSTGRES_*`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`
- Auth (future): `AUTH_ENABLED`, `JWT_*`

## Database access

- SQLAlchemy 2.x `QueuePool` with **pool_pre_ping**, **pool_recycle**, **pool_size**, **max_overflow**
- Sessions: `autoflush=False`, `expire_on_commit=False`, rollback on exception, always closed
- Services must not query `warehouse` / `public` facts directly

## Cross-cutting concerns

See [middleware.md](middleware.md) and [api_overview.md](api_overview.md).

## Non-goals (this layer)

- JWT enforcement (stubs only)
- Dashboard UI
- DDL / SQL view changes
- Write APIs
