# Tests — SupplySight AI

## Purpose

Cross-cutting test suites that span packages, plus pointers to package-local tests (`frontend/`, `backend/tests/`).

## Contents

| Path | Role |
|------|------|
| `frontend/` | Frontend E2E / component suites (future) |
| `backend/` | Backend API / service suites (future) |
| `integration/` | End-to-end API + DB (+ optional UI) flows |

## Future Implementation

- Pytest and Playwright/Jest runners wired in CI
- Shared fixtures and test data under `data/sample/`
