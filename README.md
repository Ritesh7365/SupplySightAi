# SupplySight AI

**Intelligent Supply Chain Analytics & Inventory Optimization Platform**

SupplySight AI is an enterprise-grade supply chain analytics platform designed to help organizations monitor operations, optimize inventory, evaluate vendors, predict delivery delays, forecast demand, and generate AI-powered business insights.

> **Status:** Project initialization phase — architecture and scaffolding only. Application logic, APIs, and ML models will be implemented in subsequent development phases.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Business Problem](#2-business-problem)
3. [Proposed Solution](#3-proposed-solution)
4. [Key Features (Planned)](#4-key-features-planned)
5. [Tech Stack](#5-tech-stack)
6. [System Architecture](#6-system-architecture)
7. [Folder Structure](#7-folder-structure)
8. [Installation Guide](#8-installation-guide)
9. [Development Workflow](#9-development-workflow)
10. [Roadmap](#10-roadmap)
11. [Future Enhancements](#11-future-enhancements)
12. [License](#12-license)
13. [Contributors](#13-contributors)

---

## 1. Project Overview

SupplySight AI unifies operational supply chain data into a single analytics and decision-support platform. It combines interactive dashboards, predictive machine learning, and generative AI insights so supply chain teams can move from reactive firefighting to proactive optimization.

The platform targets warehouse managers, inventory planners, procurement teams, logistics coordinators, and executive stakeholders who need timely, trustworthy signals across the end-to-end supply chain.

---

## 2. Business Problem

Modern supply chains generate large volumes of fragmented data across orders, warehouses, vendors, transportation, and inventory systems. Organizations typically struggle with:

- Limited real-time visibility into warehouse and inventory performance
- Reactive inventory policies that cause stockouts or overstock
- Inconsistent vendor reliability scoring
- Late discovery of delivery delays and transit bottlenecks
- Demand forecasts that are manual, siloed, or poorly calibrated
- Insight generation that depends on scarce analyst time

These gaps increase carrying costs, erode service levels, and slow executive decision-making.

---

## 3. Proposed Solution

SupplySight AI provides a centralized analytics layer with:

- A Next.js interactive dashboard for operational KPIs and drill-downs
- A FastAPI backend for secure data access, orchestration, and AI services
- PostgreSQL as the system of record for transactional and analytical data
- Dedicated ML pipelines for delay prediction, demand forecasting, inventory optimization, and vendor risk
- AI-assisted business insight generation for planners and leadership
- Docker-based local and deployment environments with CI/CD via GitHub Actions

---

## 4. Key Features (Planned)

| Domain | Planned Capabilities |
|--------|----------------------|
| **Analytics Dashboard** | KPI cards, trend charts, warehouse heatmaps, exception alerts |
| **Orders** | Order lifecycle tracking, SLA monitoring, fulfillment analytics |
| **Inventory** | Stock levels, reorder signals, ABC analysis, aging |
| **Warehouses** | Throughput, utilization, pick/pack performance |
| **Vendors** | On-time delivery, quality scores, risk tiers |
| **Transportation** | Route performance, carrier scorecards, delay hotspots |
| **Forecast** | Product/SKU demand forecasts with confidence bands |
| **Predictions** | Delivery delay probability and ETA risk flags |
| **AI Insights** | Narrative summaries, recommended actions, anomaly explanations |
| **Auth & RBAC** | Secure login with role-based access control |
| **Ops** | Docker Compose, CI/CD, migrations, observability hooks |

---

## 5. Tech Stack

### Frontend
- Next.js, React, TypeScript
- Tailwind CSS, Recharts
- React Query, Axios

### Backend
- FastAPI, Python
- SQLAlchemy, Alembic, Pydantic

### Database
- PostgreSQL

### Machine Learning
- Pandas, NumPy
- Scikit-Learn, XGBoost, LightGBM
- Prophet, SHAP

### Deployment & DevOps
- Docker, Docker Compose
- GitHub Actions

---

## 6. System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Next.js UI     │────▶│  FastAPI API    │────▶│  PostgreSQL     │
│  (frontend/)    │     │  (backend/)     │     │  (database/)    │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │  ML Services    │
                        │  (ml/)          │
                        └─────────────────┘
```

High-level layers:

1. **Presentation** — Next.js app with domain-specific UI modules
2. **API / Application** — FastAPI routes, services, auth, middleware
3. **Data** — PostgreSQL schemas, migrations, seeds
4. **Intelligence** — Feature engineering, training, evaluation, artifacts
5. **Platform** — Docker, CI/CD, scripts, documentation

Detailed diagrams will live under `docs/architecture/` and `docs/diagrams/`.

---

## 7. Folder Structure

```
SupplySight-AI/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── database/          # Schema, migrations, seeds, backups
├── data/              # Raw, processed, external, sample datasets
├── ml/                # ML modules, training, artifacts
├── notebooks/         # Exploratory and modeling notebooks
├── docs/              # Architecture, API, design docs
├── docker/            # Service-specific Docker assets
├── scripts/           # Setup, database, deployment scripts
├── tests/             # Cross-cutting and integration tests
├── .github/           # Workflows and contribution templates
├── docker-compose.yml
├── Makefile
└── README.md
```

See each subdirectory `README.md` for purpose and future implementation notes.

---

## 8. Installation Guide

> Prerequisites will be finalized during environment setup. Expected baseline:

- Node.js (LTS) and npm/yarn/pnpm
- Python 3.11+
- Docker Desktop / Docker Compose
- PostgreSQL client tools (optional for local non-Docker use)
- Git

### Clone

```bash
git clone <repository-url>
cd SupplySight-AI
```

### Environment

```bash
cp .env.example .env
# Edit .env with local credentials (never commit secrets)
```

### Start infrastructure (planned)

```bash
docker compose up -d
# or: make up
```

### Frontend / Backend (planned)

```bash
# Frontend
cd frontend && npm install && npm run dev

# Backend
cd backend && python -m venv .venv
# Activate venv, then install from backend/requirements/
```

Exact install commands will be added when application scaffolding is implemented.

---

## 9. Development Workflow

1. Create a feature branch from `main` (or `develop` once branching strategy is adopted).
2. Implement changes only in the relevant module (`frontend/`, `backend/`, `ml/`, etc.).
3. Add or update tests under `tests/` or package-local `tests/`.
4. Run lint/format/test targets via `Makefile` (targets to be expanded).
5. Open a pull request using `.github/PULL_REQUEST_TEMPLATE.md`.
6. Pass CI checks in GitHub Actions before merge.
7. Update `CHANGELOG.md` for user-visible changes.

Contribution norms are documented in `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.

---

## 10. Roadmap

| Phase | Focus | Outcome |
|-------|--------|---------|
| **Phase 0** | Project initialization | Repository structure, docs, DevOps placeholders |
| **Phase 1** | Data & database foundation | Schema design, migrations, seed data |
| **Phase 2** | Backend core | Auth, RBAC, domain APIs, service layer |
| **Phase 3** | Frontend core | Layout, dashboard shells, data fetching |
| **Phase 4** | ML pipelines | Features, training, evaluation, model registry |
| **Phase 5** | AI insights | Insight generation services and UI |
| **Phase 6** | Hardening | Observability, performance, security review, release |

---

## 11. Future Enhancements

- Multi-tenant organization support
- Real-time event streaming (e.g., Kafka / CDC)
- Advanced what-if simulation for inventory policies
- Mobile-responsive operations views
- SSO / enterprise identity providers
- Feature store and automated model retraining
- Cost-to-serve and carbon footprint analytics

---

## 12. License

This project is licensed under the terms described in the [LICENSE](LICENSE) file.

---

## 13. Contributors

SupplySight AI is maintained by the SupplySight engineering team.

| Role | Responsibility |
|------|----------------|
| Software Architect | System design and standards |
| Data Engineer | Pipelines, warehouse data, quality |
| Full Stack Engineer | Frontend and backend delivery |
| Machine Learning Engineer | Models, evaluation, MLOps |
| DevOps Engineer | Containers, CI/CD, environments |

Contributions are welcome via pull requests. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes.

---

*SupplySight AI — from reactive logistics to intelligent supply chain decisions.*
