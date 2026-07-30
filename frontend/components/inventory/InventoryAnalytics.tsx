"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle, Boxes, PackageX, Warehouse } from "lucide-react";

import { SeriesChart } from "@/components/charts";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { InventoryAlertsPanel } from "@/components/dashboard/InventoryAlertsPanel";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { Alert } from "@/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";
import { formatCurrency, formatNumber, formatPercent, toNumber } from "@/lib/format";

export function InventoryAnalytics() {
  const summaryQ = useQuery({
    queryKey: ["operations", "inventory-summary"],
    queryFn: () => api.getInventorySummary(),
  });
  const balancesQ = useQuery({
    queryKey: ["operations", "inventory-balances"],
    queryFn: () => api.getInventoryBalances(100),
  });
  const alertsQ = useQuery({
    queryKey: ["dashboard", "inventory-alerts", "page"],
    queryFn: () => api.getInventoryAlerts(20),
  });

  const summary = summaryQ.data;
  const balances = balancesQ.data?.data ?? [];
  const empty = (summary?.sku_count ?? 0) === 0;

  return (
    <section className="space-y-6">
      <PageHeader pathname="/inventory" />

      {summaryQ.error ? (
        <Alert title="Unable to load inventory" description={(summaryQ.error as Error).message} />
      ) : null}

      {summaryQ.isLoading ? (
        <DashboardSkeleton />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard title="Stock units" value={formatNumber(summary?.total_units)} icon={Boxes} growth={null} hint="available units" />
            <KpiCard title="Inventory value" value={formatCurrency(summary?.inventory_value_proxy)} icon={Warehouse} growth={null} hint="qty × product price" />
            <KpiCard title="Low / out of stock" value={`${formatNumber(summary?.low_stock_count)} / ${formatNumber(summary?.out_of_stock_count)}`} icon={AlertTriangle} growth={null} hint={`below safety ${formatNumber(summary?.below_safety_count ?? 0)}`} accent="bg-amber-500/10 text-amber-700 dark:text-amber-300" />
            <KpiCard title="Turnover" value={summary?.inventory_turnover == null ? "—" : formatNumber(summary.inventory_turnover)} icon={PackageX} growth={null} hint={`util ${summary?.avg_warehouse_utilization_pct == null ? "—" : formatPercent(summary.avg_warehouse_utilization_pct)}`} />
          </div>

          {empty ? (
            <Alert
              title="Inventory master is not populated"
              description="public.inventory is a placeholder table. Connect a WMS feed or load balances to unlock turnover, safety stock, and restock recommendations."
            />
          ) : (
            <>
              <div className="grid gap-4 xl:grid-cols-2">
                <SeriesChart
                  title="Inventory Levels"
                  data={balances.slice(0, 12).map((b) => ({
                    name: b.product_name.slice(0, 14),
                    units: toNumber(b.quantity_available),
                  }))}
                  xKey="name"
                  series={[{ key: "units", name: "Available", color: "#0ea5e9" }]}
                  variant="bar"
                  currency={false}
                />
                <InventoryAlertsPanel data={alertsQ.data} />
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Inventory balances</CardTitle>
                  <CardDescription>Lowest available quantities first</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Product</TableHead>
                        <TableHead>Warehouse</TableHead>
                        <TableHead>On hand</TableHead>
                        <TableHead>Available</TableHead>
                        <TableHead>Safety</TableHead>
                        <TableHead>Reorder</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {balances.map((b) => (
                        <TableRow key={b.inventory_id}>
                          <TableCell className="font-medium">{b.product_name}</TableCell>
                          <TableCell>{b.warehouse_name || `#${b.warehouse_id}`}</TableCell>
                          <TableCell className="tabular-nums">
                            {formatNumber(b.quantity_on_hand)}
                          </TableCell>
                          <TableCell className="tabular-nums">
                            {formatNumber(b.quantity_available)}
                          </TableCell>
                          <TableCell className="tabular-nums">
                            {b.safety_stock == null ? "—" : formatNumber(b.safety_stock)}
                          </TableCell>
                          <TableCell className="tabular-nums">
                            {b.reorder_point == null ? "—" : formatNumber(b.reorder_point)}
                          </TableCell>
                          <TableCell>{b.stock_status || "—"}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </>
          )}
        </>
      )}
    </section>
  );
}
