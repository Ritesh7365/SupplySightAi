# Backend — SupplySight AI

## Purpose

Hosts the **FastAPI** application: HTTP API surface, domain services, ORM models, auth/RBAC middleware, configuration, and ML inference orchestration hooks.

## Contents

| Path | Role |
|------|------|
| `app/api/routes/` | Route modules (versioned endpoints) |
| `app/models/` | SQLAlchemy ORM models |
| `app/schemas/` | Pydantic request/response schemas |
| `app/services/` | Business/application services |
| `app/core/` | Security, dependencies, shared core |
| `app/database/` | Engine, session, base metadata |
| `app/middleware/` | Logging, CORS, auth middleware |
| `app/utils/` | Helpers |
| `app/config/` | Settings / environment loading |
| `app/ml/` | Inference adapters calling `ml/` artifacts |
| `tests/` | Backend unit/integration tests |
| `requirements/` | Split dependency files (base, dev, ml) |

## Tech (planned)

FastAPI, Python, SQLAlchemy, Alembic, Pydantic

## Future Implementation

- Application factory and router registration
- Auth (JWT) and role-based access control
- Domain CRUD and analytics endpoints
- Alembic migrations coordinated with `database/`
- Health checks and OpenAPI documentation

> No APIs or business logic in this initialization phase.
