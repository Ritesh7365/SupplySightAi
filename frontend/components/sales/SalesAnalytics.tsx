"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { AnalyticsFilterBar } from "@/components/analytics/AnalyticsFilterBar";
import { DonutChartCard, SeriesChart } from "@/components/charts";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
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
import { exportCsv, exportExcel, exportPdf } from "@/lib/export";
import { formatCurrency, formatNumber, formatPercent, toNumber, truncateLabel } from "@/lib/format";
import { DollarSign, ShoppingBag, Users, Wallet } from "lucide-react";

export function SalesAnalytics() {
  const [year, setYear] = useState("");
  const [region, setRegion] = useState("");
  const [market, setMarket] = useState("");

  const salesQ = useQuery({
    queryKey: ["sales", year, region, market],
    queryFn: () =>
      api.getSales({
        year: year ? Number(year) : undefined,
        region: region || undefined,
        market: market || undefined,
        limit: 2000,
      }),
  });

  const monthlyQ = useQuery({
    queryKey: ["charts", "monthly-sales", year || "all"],
    queryFn: () => api.getMonthlySales(year ? Number(year) : undefined),
  });

  const productsQ = useQuery({
    queryKey: ["charts", "top-products", "sales"],
    queryFn: () => api.getTopProducts(10),
  });

  const customersQ = useQuery({
    queryKey: ["charts", "top-customers", "sales"],
    queryFn: () => api.getTopCustomers(10),
  });

  const categoryQ = useQuery({
    queryKey: ["dashboard", "category", "sales"],
    queryFn: () => api.getRevenueByCategory(12),
  });

  const rows = salesQ.data?.data ?? [];
  const monthly = monthlyQ.data?.data ?? [];

  const years = useMemo(() => {
    const set = new Set(rows.map((r) => String(r.year_number)));
    monthly.forEach((m) => set.add(String(m.year_number)));
    return [
      { label: "All years", value: "" },
      ...[...set].sort().map((y) => ({ label: y, value: y })),
    ];
  }, [rows, monthly]);

  const regions = useMemo(() => {
    const set = new Set(rows.map((r) => r.region).filter(Boolean) as string[]);
    return [
      { label: "All regions", value: "" },
      ...[...set].sort().map((r) => ({ label: r, value: r })),
    ];
  }, [rows]);

  const markets = useMemo(() => {
    const set = new Set(rows.map((r) => r.market).filter(Boolean) as string[]);
    return [
      { label: "All markets", value: "" },
      ...[...set].sort().map((m) => ({ label: m, value: m })),
    ];
  }, [rows]);

  const totals = useMemo(() => {
    const sales = rows.reduce((a, r) => a + toNumber(r.sales), 0);
    const profit = rows.reduce((a, r) => a + toNumber(r.profit), 0);
    const orders = rows.reduce((a, r) => a + r.order_count, 0);
    const customers = rows.reduce((a, r) => a + r.customer_count, 0);
    return { sales, profit, orders, customers, margin: sales ? (profit / sales) * 100 : 0 };
  }, [rows]);

  const monthlyChart = [...monthly]
    .sort((a, b) => a.year_month.localeCompare(b.year_month))
    .map((m) => ({
      label: `${m.month_name.slice(0, 3)} ${String(m.year_number).slice(2)}`,
      sales: toNumber(m.sales),
      profit: toNumber(m.profit),
      orders: m.order_count,
    }));

  const regionRollup = useMemo(() => {
    const map = new Map<string, number>();
    for (const r of rows) {
      const key = r.region || r.market || "Unspecified";
      map.set(key, (map.get(key) ?? 0) + toNumber(r.sales));
    }
    return [...map.entries()]
      .map(([name, value]) => ({ name, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8);
  }, [rows]);

  const exportRows = rows.map((r) => ({
    year: r.year_number,
    month: r.month_name,
    market: r.market,
    region: r.region,
    sales: toNumber(r.sales),
    profit: toNumber(r.profit),
    orders: r.order_count,
    customers: r.customer_count,
    aov: toNumber(r.average_order_value),
    margin_pct: toNumber(r.profit_margin_pct),
  }));

  const isLoading = salesQ.isLoading || monthlyQ.isLoading;
  const error = (salesQ.error || monthlyQ.error) as Error | undefined;

  return (
    <section className="space-y-6">
      <PageHeader pathname="/sales" />

      <AnalyticsFilterBar
        year={year}
        region={region}
        market={market}
        years={years}
        regions={regions}
        markets={markets}
        onYearChange={setYear}
        onRegionChange={setRegion}
        onMarketChange={setMarket}
        onExportCsv={() => exportCsv("sales-performance.csv", exportRows)}
        onExportExcel={() => exportExcel("sales-performance.xls", exportRows)}
        onExportPdf={() => exportPdf("Sales Performance", exportRows)}
      />

      {error ? (
        <Alert
          title="Unable to load sales analytics"
          description={error.message}
          action={
            <Button variant="outline" size="sm" onClick={() => void salesQ.refetch()}>
              Retry
            </Button>
          }
        />
      ) : null}

      {isLoading ? (
        <DashboardSkeleton />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard title="Revenue" value={formatCurrency(totals.sales)} icon={DollarSign} growth={null} hint="filtered total" />
            <KpiCard title="Profit" value={formatCurrency(totals.profit)} icon={Wallet} growth={null} hint={`margin ${formatPercent(totals.margin)}`} accent="bg-emerald-500/10 text-emerald-700 dark:text-emerald-300" />
            <KpiCard title="Orders" value={formatNumber(totals.orders)} icon={ShoppingBag} growth={null} hint="order lines rollup" />
            <KpiCard title="Customers" value={formatNumber(totals.customers)} icon={Users} growth={null} hint="active in filter" />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Monthly Sales"
              description="Revenue and profit by month"
              data={monthlyChart}
              xKey="label"
              series={[
                { key: "sales", name: "Revenue" },
                { key: "profit", name: "Profit", color: "#10b981" },
              ]}
              variant="area"
            />
            <SeriesChart
              title="Weekly / Daily proxy"
              description="Order volume by month (daily grain not in analytics views)"
              data={monthlyChart}
              xKey="label"
              series={[{ key: "orders", name: "Orders", color: "#0ea5e9" }]}
              currency={false}
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-3">
            <DonutChartCard title="Revenue by Region" data={regionRollup} />
            <SeriesChart
              title="Revenue by Category"
              data={(categoryQ.data?.data ?? []).map((c) => ({
                name: truncateLabel(c.name, 12),
                sales: toNumber(c.sales),
              }))}
              xKey="name"
              series={[{ key: "sales", name: "Revenue" }]}
              variant="bar"
            />
            <SeriesChart
              title="Top Products"
              data={(productsQ.data?.data ?? []).map((p) => ({
                name: truncateLabel(p.product_name, 12),
                sales: toNumber(p.sales),
              }))}
              xKey="name"
              series={[{ key: "sales", name: "Revenue", color: "#f59e0b" }]}
              variant="bar"
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Top Customers"
              data={(customersQ.data?.data ?? []).map((c) => ({
                name: truncateLabel(c.customer_name, 14),
                revenue: toNumber(c.revenue),
              }))}
              xKey="name"
              series={[{ key: "revenue", name: "Revenue", color: "#8b5cf6" }]}
              variant="bar"
            />
            <SeriesChart
              title="Top Categories"
              data={(categoryQ.data?.data ?? []).slice(0, 8).map((c) => ({
                name: truncateLabel(c.name, 14),
                profit: toNumber(c.profit),
              }))}
              xKey="name"
              series={[{ key: "profit", name: "Profit", color: "#10b981" }]}
              variant="bar"
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Sales table</CardTitle>
              <CardDescription>Filtered sales performance rows</CardDescription>
            </CardHeader>
            <CardContent>
              {rows.length === 0 ? (
                <div className="flex min-h-[10rem] items-center justify-center rounded-xl border border-dashed border-border text-sm text-muted-foreground">
                  No rows for the selected filters.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Period</TableHead>
                      <TableHead>Market</TableHead>
                      <TableHead>Region</TableHead>
                      <TableHead>Sales</TableHead>
                      <TableHead>Profit</TableHead>
                      <TableHead>Orders</TableHead>
                      <TableHead>Margin</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {rows.slice(0, 100).map((r, idx) => (
                      <TableRow key={`${r.year_month}-${r.market}-${r.region}-${idx}`}>
                        <TableCell>
                          {r.month_name} {r.year_number}
                        </TableCell>
                        <TableCell>{r.market || "—"}</TableCell>
                        <TableCell>{r.region || "—"}</TableCell>
                        <TableCell className="tabular-nums">{formatCurrency(r.sales)}</TableCell>
                        <TableCell className="tabular-nums">{formatCurrency(r.profit)}</TableCell>
                        <TableCell className="tabular-nums">{formatNumber(r.order_count)}</TableCell>
                        <TableCell className="tabular-nums">
                          {formatPercent(r.profit_margin_pct)}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </section>
  );
}
