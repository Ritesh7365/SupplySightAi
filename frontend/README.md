# Frontend — SupplySight AI

## Purpose

Houses the **Next.js / React / TypeScript** user interface for SupplySight AI: analytics dashboards, domain screens (orders, inventory, warehouses, vendors, transportation, forecast, predictions, AI insights), authentication UI, and settings.

## Contents

| Path | Role |
|------|------|
| `app/` | Next.js App Router entrypoints and page shells |
| `components/` | Reusable UI by domain (layout, dashboard, orders, …) |
| `api/` | Client-side API helpers / route handlers (future) |
| `hooks/` | React Query and shared React hooks |
| `lib/` | Utilities, Axios clients, formatters |
| `styles/` | Global and Tailwind-related styles |
| `types/` | Shared TypeScript types and DTOs |
| `public/` | Static assets |

## Tech (planned)

Next.js, React, TypeScript, Tailwind CSS, Recharts, React Query, Axios

## Future Implementation

- Scaffold Next.js app with Tailwind and TypeScript
- Build layout shell and authenticated routes
- Wire React Query + Axios to FastAPI
- Implement domain pages and chart components
- Add auth/login and RBAC-aware navigation

> No application pages or business logic in this initialization phase.
