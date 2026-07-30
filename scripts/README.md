# Scripts — SupplySight AI

## Purpose

Operational automation for developer setup, database maintenance, and deployment helpers. Prefer Makefile targets that call into these scripts.

## Contents

| Path | Role |
|------|------|
| `setup/` | Bootstrap local environments |
| `database/` | Migrate, seed, backup helpers |
| `deployment/` | Release / deploy assistants |

## Future Implementation

- Cross-platform scripts (PowerShell + bash where needed)
- Idempotent setup with clear prerequisites checks
