# Frontend — SupplySight AI

Next.js 15 App Router foundation for the SupplySight AI UI.

## Quick start

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

| Script | Command |
|--------|---------|
| Dev (Turbopack) | `npm run dev` |
| Production build | `npm run build` |
| Start | `npm run start` |
| Lint | `npm run lint` |

## Stack

- Next.js 15 · React 19 · TypeScript
- Tailwind CSS 3 · App Router · ESLint
- Absolute imports via `@/*`
- `components.json` prepared for shadcn/ui

## Layout (preserved)

```
frontend/
├── app/           # App Router (layout, page, globals)
├── components/    # Domain UI (placeholders)
├── hooks/
├── lib/
├── styles/
├── types/
├── public/
└── api/
```

Dashboards, charts, and API business logic are intentionally not included yet.
