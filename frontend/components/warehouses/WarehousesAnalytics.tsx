"use client";

import { useQuery } from "@tanstack/react-query";
import { MapPin, Warehouse } from "lucide-react";

import { SeriesChart } from "@/components/charts";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { Alert } from "@/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";
import { formatCurrency, formatNumber, formatPercent, toNumber } from "@/lib/format";

export function WarehousesAnalytics() {
  const query = useQuery({
    queryKey: ["operations", "warehouses"],
    queryFn: () => api.getWarehouses(),
  });

  const rows = query.data?.data ?? [];
  const units = rows.reduce((a, r) => a + toNumber(r.units_on_hand), 0);
  const value = query.data?.total_inventory_value ?? rows.reduce((a, r) => a + toNumber(r.inventory_value), 0);

  return (
    <section className="space-y-6">
      <PageHeader pathname="/warehouses" />

      {query.error ? (
        <Alert title="Unable to load warehouses" description={(query.error as Error).message} />
      ) : null}

      {query.isLoading ? (
        <DashboardSkeleton />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard title="Warehouses" value={formatNumber(query.data?.warehouse_count ?? rows.length)} icon={Warehouse} growth={null} hint="registered sites" />
            <KpiCard title="Capacity" value={formatNumber(query.data?.total_capacity)} icon={MapPin} growth={null} hint="total storage units" />
            <KpiCard title="Avg utilization" value={query.data?.avg_utilization_pct == null ? "—" : formatPercent(query.data.avg_utilization_pct)} icon={Warehouse} growth={null} hint="occupancy across network" />
            <KpiCard title="Inventory value" value={formatCurrency(value)} icon={MapPin} growth={null} hint={`${formatNumber(units)} units on hand`} />
          </div>

          {rows.length === 0 ? (
            <Alert
              title="No warehouses loaded"
              description="public.warehouses is a placeholder. Seed warehouse masters and inventory balances to unlock utilization heatmaps and capacity analytics."
            />
          ) : (
            <>
              <SeriesChart
                title="Warehouse Comparison"
                data={rows.map((w) => ({
                  name: w.warehouse_code,
                  units: toNumber(w.units_on_hand),
                }))}
                xKey="name"
                series={[{ key: "units", name: "Units", color: "#0ea5e9" }]}
                variant="bar"
                currency={false}
              />

              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {rows.map((w) => (
                  <Card key={w.warehouse_id} className="transition-shadow hover:shadow-md">
                    <CardHeader>
                      <CardTitle className="text-lg">{w.warehouse_name}</CardTitle>
                      <CardDescription>
                        {w.warehouse_code}
                        {w.city ? ` · ${w.city}` : ""}
                        {w.country ? `, ${w.country}` : ""}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Capacity</span>
                        <span className="font-medium tabular-nums">
                          {w.capacity == null ? "—" : formatNumber(w.capacity)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Inventory value</span>
                        <span className="font-medium tabular-nums">
                          {formatCurrency(w.inventory_value)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Utilization</span>
                        <span className="font-medium">
                          {w.utilization_pct == null ? "—" : formatPercent(w.utilization_pct)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Orders (city proxy)</span>
                        <span className="font-medium tabular-nums">
                          {formatNumber(w.orders_handled ?? 0)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </section>
  );
}
