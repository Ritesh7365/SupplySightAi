"""OpenAPI / Swagger metadata (tags, description, contact)."""

from __future__ import annotations

from backend.app import __version__

API_DESCRIPTION = """
## SupplySight AI Analytics API

Production-oriented FastAPI service that exposes **dashboard** and **chart**
endpoints backed exclusively by the PostgreSQL ``analytics`` schema
(views and materialized views).

### Design principles

- **Read-only analytics** — no writes to ``warehouse`` or ``public`` fact tables
- **Pooled SQLAlchemy** sessions with pre-ping and recycling
- **Observability** — request IDs, timing headers, structured access logs
- **Compression** — GZip for responses larger than 1000 bytes
- **Auth-ready** — Bearer dependency wired; JWT enforcement disabled by default

### Health probes

| Path | Purpose |
|------|---------|
| `/health` | Aggregate service health |
| `/health/liveness` | Process is up |
| `/health/readiness` | Ready to accept traffic (includes DB) |
| `/health/database` | Database connectivity + pool snapshot |

### Error envelope

```json
{
  "error": { "code": "validation_error", "message": "...", "details": ... },
  "request_id": "uuid"
}
```
""".strip()

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "Health",
        "description": "Liveness, readiness, and database probes for orchestrators.",
    },
    {
        "name": "Dashboard",
        "description": "KPI and dimensional dashboards sourced from analytics views.",
    },
    {
        "name": "Charts",
        "description": "Time-series and ranking series for frontend visualizations.",
    },
]

OPENAPI_CONTACT = {
    "name": "SupplySight AI",
    "url": "https://github.com/Ritesh7365/SupplySightAi",
}

OPENAPI_LICENSE = {
    "name": "Proprietary",
}


def build_openapi_extra() -> dict:
    return {
        "x-api-version": __version__,
    }
