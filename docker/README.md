# Docker — SupplySight AI

## Purpose

Service-specific Docker assets (Dockerfiles, entrypoints, init scripts) referenced by the root `docker-compose.yml`.

## Contents

| Path | Role |
|------|------|
| `frontend/` | Next.js image build context helpers |
| `backend/` | FastAPI image build context helpers |
| `postgres/` | DB init scripts and config overlays |

## Future Implementation

- Production-ready multi-stage Dockerfiles
- Non-root users, healthchecks, slim base images
- Compose overlays for staging/production
