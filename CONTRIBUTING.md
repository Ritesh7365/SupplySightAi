# Contributing to SupplySight AI

Thank you for your interest in contributing to **SupplySight AI**. This document describes how to propose changes during and after project initialization.

---

## Code of Conduct

Participation is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By contributing, you agree to uphold those standards.

---

## Project Status

This repository is in the **architecture / scaffolding** phase. Prefer structure, documentation, and DevOps improvements until application modules are opened for implementation.

Do **not** introduce unfinished business logic, production APIs, or trained models unless a related issue or epic explicitly requests that work.

---

## Getting Started

1. Fork or clone the repository.
2. Copy `.env.example` to `.env` and adjust local values.
3. Review the root [README.md](README.md) and the `README.md` in the area you will change.
4. Create a feature branch: `feature/<short-description>` or `docs/<short-description>`.

---

## Branching & Commits

- Keep commits focused and reversible.
- Use clear commit messages that explain **why** the change exists.
- Prefer small PRs over large mixed-scope changes.

Suggested prefixes: `feat:`, `fix:`, `docs:`, `chore:`, `ci:`, `refactor:`.

---

## Pull Requests

1. Ensure your branch is up to date with the base branch.
2. Fill out [.github/PULL_REQUEST_TEMPLATE.md](.github/PULL_REQUEST_TEMPLATE.md).
3. Link related issues when applicable.
4. Request review from the appropriate domain owner (frontend, backend, ML, DevOps).

CI checks (once enabled) must pass before merge.

---

## Coding Standards (Planned)

| Area | Guidance |
|------|----------|
| Frontend | TypeScript, Next.js conventions, Tailwind utility patterns |
| Backend | FastAPI layering (routes → services → models), Pydantic schemas |
| ML | Reproducible notebooks → scripts → packaged training modules |
| Docs | Markdown, diagrams under `docs/diagrams/` |

Exact linters and formatters will be pinned in later setup scripts.

---

## Security

- Never commit secrets, API keys, or production dumps.
- Use `.env` locally; keep `.env.example` as the non-secret template.
- Report vulnerabilities privately to the maintainers when a security contact is published.

---

## Questions

Open a GitHub Discussion or issue using the templates under `.github/ISSUE_TEMPLATE/`.

---

*SupplySight AI engineering team*
