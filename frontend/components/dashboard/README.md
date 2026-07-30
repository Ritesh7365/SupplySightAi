# Dashboard components

Executive dashboard widgets wired to FastAPI analytics endpoints via React Query.

| Component | Source |
|-----------|--------|
| `KpiGrid` | `GET /dashboard/executive` (+ MoM from monthly sales) |
| `RevenueTrendChart` | `GET /charts/monthly-sales` |
| `RegionDonutChart` | `GET /dashboard/geography` |
| `TopProductsChart` | `GET /charts/top-products` |
| `RecentOrdersTable` | `GET /dashboard/recent-orders` |
| `InventoryAlertsPanel` | `GET /dashboard/inventory-alerts` |
