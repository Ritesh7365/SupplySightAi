# Layout components

Production application shell for SupplySight AI (sidebar, navbar, theme, responsive drawer).

| Component | Role |
|-----------|------|
| `AppShell.tsx` | Composes sidebar + navbar + content frame |
| `ResponsiveSidebar.tsx` | Desktop rail + mobile drawer |
| `Sidebar.tsx` | Navigation links and collapse control |
| `Navbar.tsx` | Search, notifications, theme, user, breadcrumbs |
| `Logo.tsx` | Brand lockup |
| `Breadcrumbs.tsx` | Route trail |
| `ThemeToggle.tsx` / `ThemeProvider.tsx` | Light / dark mode |
| `UserMenu.tsx` | Account menu |
| `SearchBar.tsx` | Workspace search field |
| `NotificationBell.tsx` | Notification panel |
| `PageHeader.tsx` / `EmptyCanvas.tsx` | Page chrome without KPI/charts |

No API calls or business logic live in these components.
