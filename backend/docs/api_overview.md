# API Overview — SupplySight AI

Base URL (local): `http://localhost:8000`  
Versioned API prefix: `/api/v1` (configurable via `API_PREFIX`)  
Interactive docs: `/docs` (Swagger) · `/redoc`

## Health (root)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Aggregate health (includes DB probe) |
| GET | `/health/database` | DB connectivity + pool stats |
| GET | `/health/readiness` | Ready for traffic (process + DB) |
| GET | `/health/liveness` | Process alive (no DB check) |
| GET | `/health/status` | Compact status string |

## Dashboard (`/api/v1/dashboard`)

| Method | Path | Analytics source |
|--------|------|------------------|
| GET | `/executive` | `vw_executive_dashboard` |
| GET | `/sales` | `vw_sales_performance` |
| GET | `/customers` | `vw_customer_performance` |
| GET | `/products` | `vw_product_performance` |
| GET | `/shipping` | `vw_shipping_performance` |
| GET | `/geography` | `vw_geographic_performance` |

Common query params (where applicable): `limit`, `year`, `market`, `region`, `segment`, `country`, `lowest`.

## Charts (`/api/v1/charts`)

| Method | Path | Analytics source |
|--------|------|------------------|
| GET | `/monthly-sales` | `mv_monthly_sales` |
| GET | `/top-products` | `vw_product_performance` |
| GET | `/top-customers` | `vw_customer_performance` |

## Response headers

| Header | Meaning |
|--------|---------|
| `X-Request-ID` | Correlation ID (echoed / generated) |
| `X-Process-Time-Ms` | Server handling time in milliseconds |
| `X-API-Version` | Application version |
| `Content-Encoding: gzip` | Present when body ≥ 1000 bytes and client accepts gzip |

## Error envelope

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed",
    "details": []
  },
  "request_id": "uuid"
}
```

| HTTP | Code |
|------|------|
| 404 | `not_found` |
| 422 | `validation_error` |
| 500 | `internal_error` |
| 503 | `database_error` |

## Pagination utility

Reusable helpers live in `backend.app.utils.pagination`:

- `pagination_params` — FastAPI dependency (`page`, `page_size`, `limit`, `offset`)
- `PaginationParams`, `Page`, `paginate_sequence`, `clamp_limit`

Existing dashboard/chart endpoints continue to use `limit` for backward compatibility;
new list APIs should prefer the shared pagination dependency.

## CORS

Default allowed origins (override with `CORS_ORIGINS`):

- `http://localhost:3000`
- `http://localhost:3001`
- `http://localhost:5173`
- `http://localhost:8000`
