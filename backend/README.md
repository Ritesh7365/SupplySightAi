# Backend ? SupplySight AI

FastAPI analytics API over the PostgreSQL ``analytics`` schema.

## Quick start

```bash
# From the backend/ directory
pip install -r requirements/base.txt

python -m uvicorn app.main:app --reload
# or: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI: http://localhost:8000/docs  
- ReDoc: http://localhost:8000/redoc  
- Health: http://localhost:8000/health  
- Readiness: http://localhost:8000/health/readiness  

Requires warehouse + analytics views already loaded in PostgreSQL (see `database/`).

## Production infrastructure

- GZip (min 1000 bytes), configurable CORS, request ID + timing logs, response headers
- Pooled SQLAlchemy (size / overflow / recycle / pre-ping)
- Global handlers for 404 / 422 / 500 / DB errors
- Docs: [`docs/backend_architecture.md`](docs/backend_architecture.md), [`docs/api_overview.md`](docs/api_overview.md), [`docs/middleware.md`](docs/middleware.md)

## Layout

```
backend/app/
+-- main.py              # FastAPI factory + lifespan
+-- api/                 # Router aggregation
+-- routers/             # /dashboard/*, /charts/*, /health
+-- models/              # SQLAlchemy mappings ? analytics views
+-- services/            # Query logic (analytics only)
+-- schemas/             # Pydantic response models
+-- database/            # Engine, pooling, sessions
+-- core/                # Config, logging, errors, auth stubs
+-- utils/               # Helpers
```

## Endpoints

| Method | Path | Source |
|--------|------|--------|
| GET | `/api/v1/dashboard/executive` | `vw_executive_dashboard` |
| GET | `/api/v1/dashboard/sales` | `vw_sales_performance` |
| GET | `/api/v1/dashboard/customers` | `vw_customer_performance` |
| GET | `/api/v1/dashboard/products` | `vw_product_performance` |
| GET | `/api/v1/dashboard/shipping` | `vw_shipping_performance` |
| GET | `/api/v1/dashboard/geography` | `vw_geographic_performance` |
| GET | `/api/v1/charts/monthly-sales` | `mv_monthly_sales` |
| GET | `/api/v1/charts/top-products` | `vw_product_performance` |
| GET | `/api/v1/charts/top-customers` | `vw_customer_performance` |

Services **do not** query `warehouse` or `public` fact tables directly.

## Configuration

Loaded from project-root `.env` (see `.env.example`):

- `POSTGRES_*` / `DATABASE_URL`
- `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, `DB_POOL_RECYCLE`
- `API_PREFIX` (default `/api/v1`)
- `AUTH_ENABLED=false` ? JWT hooks exist in `core/security.py` but are not enforced

## Auth (future)

`HTTPBearer` + `get_current_user_optional` are wired on dashboard/chart routes.
Set `AUTH_ENABLED=true` and implement JWT validation when ready.
