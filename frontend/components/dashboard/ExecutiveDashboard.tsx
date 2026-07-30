"use client";

import { DonutChartCard, SeriesChart } from "@/components/charts";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { InventoryAlertsPanel } from "@/components/dashboard/InventoryAlertsPanel";
import { KpiGrid } from "@/components/dashboard/KpiGrid";
import { RecentOrdersTable } from "@/components/dashboard/RecentOrdersTable";
import { RecentShipmentsTable } from "@/components/dashboard/RecentShipmentsTable";
import { PageHeader } from "@/components/layout/PageHeader";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { useExecutiveDashboardData } from "@/hooks/use-executive-dashboard";
import { formatDate, toNumber, truncateLabel } from "@/lib/format";

export function ExecutiveDashboard() {
  const {
    isLoading,
    error,
    refetchAll,
    executive,
    monthlySales,
    topProducts,
    topCustomers,
    regions,
    shipping,
    categories,
    departments,
    recentOrders,
    recentShipments,
    inventory,
    growth,
    sparklines,
  } = useExecutiveDashboardData();

  const monthlyChart = [...monthlySales]
    .sort((a, b) => a.year_month.localeCompare(b.year_month))
    .map((row) => ({
      label: `${row.month_name.slice(0, 3)} ${String(row.year_number).slice(2)}`,
      sales: toNumber(row.sales),
      profit: toNumber(row.profit),
      orders: row.order_count,
      customers: row.customer_count,
    }));

  const lateModes = shipping.map((s) => ({
    name: truncateLabel(s.shipping_mode, 18),
    late: s.late_delivery_count,
    shipments: s.shipment_count,
    risk: toNumber(s.late_delivery_risk_pct),
  }));

  return (
    <section className="space-y-6">
      <PageHeader pathname="/dashboard">
        {executive?.refreshed_at ? (
          <p className="text-sm text-muted-foreground">
            Data refreshed {formatDate(executive.refreshed_at)}
          </p>
        ) : null}
      </PageHeader>

      {error ? (
        <Alert
          title="Unable to load executive dashboard"
          description={error.message || "The analytics API did not respond successfully."}
          action={
            <Button variant="outline" size="sm" onClick={() => void refetchAll()}>
              Retry
            </Button>
          }
        />
      ) : null}

      {isLoading && !executive ? (
        <DashboardSkeleton />
      ) : executive ? (
        <>
          <KpiGrid data={executive} growth={growth} sparklines={sparklines} />

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Revenue Trend"
              description="Monthly revenue from analytics.mv_monthly_sales"
              data={monthlyChart}
              xKey="label"
              series={[{ key: "sales", name: "Revenue" }]}
              variant="area"
            />
            <SeriesChart
              title="Profit Trend"
              description="Gross profit across the same monthly series"
              data={monthlyChart}
              xKey="label"
              series={[{ key: "profit", name: "Profit", color: "#10b981" }]}
              variant="area"
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Orders Trend"
              description="Order volume by month"
              data={monthlyChart}
              xKey="label"
              series={[{ key: "orders", name: "Orders", color: "#0ea5e9" }]}
              currency={false}
            />
            <SeriesChart
              title="Customer Growth"
              description="Active customers contributing revenue each month"
              data={monthlyChart}
              xKey="label"
              series={[{ key: "customers", name: "Customers", color: "#8b5cf6" }]}
              currency={false}
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-3">
            <DonutChartCard
              title="Revenue by Region"
              description="Top regions by sales"
              data={regions.map((r) => ({ name: r.region, value: r.sales }))}
            />
            <SeriesChart
              title="Revenue by Category"
              description="Category contribution"
              data={categories.map((c) => ({
                name: truncateLabel(c.name, 14),
                sales: toNumber(c.sales),
              }))}
              xKey="name"
              series={[{ key: "sales", name: "Revenue" }]}
              variant="bar"
              height={320}
            />
            <SeriesChart
              title="Revenue by Department"
              description="Department contribution"
              data={departments.map((d) => ({
                name: truncateLabel(d.name, 14),
                sales: toNumber(d.sales),
              }))}
              xKey="name"
              series={[{ key: "sales", name: "Revenue", color: "#f59e0b" }]}
              variant="bar"
              height={320}
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Late Deliveries by Mode"
              description="Late shipment counts across shipping modes"
              data={lateModes}
              xKey="name"
              series={[{ key: "late", name: "Late shipments", color: "#ef4444" }]}
              variant="bar"
              currency={false}
            />
            <DonutChartCard
              title="Shipping Modes"
              description="Shipment volume mix"
              data={shipping.map((s) => ({
                name: s.shipping_mode,
                value: s.shipment_count,
              }))}
              currency={false}
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Top Products"
              description="Best sellers by revenue"
              data={topProducts.map((p) => ({
                name: truncateLabel(p.product_name, 16),
                sales: toNumber(p.sales),
              }))}
              xKey="name"
              series={[{ key: "sales", name: "Revenue" }]}
              variant="bar"
            />
            <SeriesChart
              title="Top Customers"
              description="Highest revenue accounts"
              data={topCustomers.map((c) => ({
                name: truncateLabel(c.customer_name, 16),
                revenue: toNumber(c.revenue),
              }))}
              xKey="name"
              series={[{ key: "revenue", name: "Revenue", color: "#0ea5e9" }]}
              variant="bar"
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <InventoryAlertsPanel data={inventory} />
            <DonutChartCard
              title="Inventory Alert Mix"
              description="Operational stock risk distribution"
              data={[
                { name: "Out of stock", value: inventory?.out_of_stock_count ?? 0 },
                { name: "Low stock", value: inventory?.low_stock_count ?? 0 },
                { name: "Reorder soon", value: inventory?.reorder_soon_count ?? 0 },
              ].filter((d) => d.value > 0)}
              currency={false}
              emptyMessage="Inventory alerts will appear once stock balances are loaded."
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <RecentOrdersTable data={recentOrders} />
            <RecentShipmentsTable data={recentShipments} />
          </div>
        </>
      ) : !error ? (
        <div className="flex min-h-[16rem] items-center justify-center rounded-2xl border border-dashed border-border bg-muted/40 px-6 text-center">
          <div>
            <p className="text-base font-medium text-foreground">No executive metrics yet</p>
            <p className="mt-2 max-w-md text-sm text-muted-foreground">
              Confirm the warehouse and analytics layer are loaded, then refresh.
            </p>
          </div>
        </div>
      ) : null}
    </section>
  );
}
