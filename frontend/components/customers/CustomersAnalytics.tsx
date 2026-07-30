"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Repeat, UserPlus, Users, Wallet } from "lucide-react";

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
import { exportCsv } from "@/lib/export";
import { formatCurrency, formatNumber, formatPercent, toNumber, truncateLabel } from "@/lib/format";

export function CustomersAnalytics() {
  const [segment, setSegment] = useState("");

  const query = useQuery({
    queryKey: ["customers", segment],
    queryFn: () => api.getCustomers({ segment: segment || undefined, limit: 100 }),
  });

  const monthlyQ = useQuery({
    queryKey: ["charts", "monthly-sales", "customers"],
    queryFn: () => api.getMonthlySales(),
  });

  const customers = query.data?.customers ?? [];
  const segments = query.data?.segments ?? [];

  const kpis = useMemo(() => {
    const total = customers.length;
    const revenue = customers.reduce((a, c) => a + toNumber(c.revenue), 0);
    const orders = customers.reduce((a, c) => a + c.order_count, 0);
    const returning = customers.filter((c) => c.order_count > 1).length;
    const ltv = total ? revenue / total : 0;
    const retention = total ? (returning / total) * 100 : 0;
    return { total, revenue, orders, returning, ltv, retention };
  }, [customers]);

  const growth = [...(monthlyQ.data?.data ?? [])]
    .sort((a, b) => a.year_month.localeCompare(b.year_month))
    .map((m) => ({
      label: `${m.month_name.slice(0, 3)} ${String(m.year_number).slice(2)}`,
      customers: m.customer_count,
    }));

  const segmentOptions = [
    { label: "All segments", value: "" },
    ...segments.map((s) => ({ label: s.customer_segment, value: s.customer_segment })),
  ];

  return (
    <section className="space-y-6">
      <PageHeader pathname="/customers">
        <div className="flex flex-wrap gap-2">
          <select
            value={segment}
            onChange={(e) => setSegment(e.target.value)}
            className="h-10 rounded-xl border border-border bg-background px-3 text-sm"
          >
            {segmentOptions.map((o) => (
              <option key={o.value || "all"} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              exportCsv(
                "customers.csv",
                customers.map((c) => ({
                  customer_id: c.customer_id,
                  name: c.customer_name,
                  segment: c.customer_segment,
                  revenue: toNumber(c.revenue),
                  orders: c.order_count,
                  aov: toNumber(c.average_order_value),
                })),
              )
            }
          >
            Export CSV
          </Button>
        </div>
      </PageHeader>

      {query.error ? (
        <Alert title="Unable to load customers" description={(query.error as Error).message} />
      ) : null}

      {query.isLoading ? (
        <DashboardSkeleton />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard title="Customers" value={formatNumber(kpis.total)} icon={Users} growth={null} hint="in current view" />
            <KpiCard title="Returning" value={formatNumber(kpis.returning)} icon={Repeat} growth={null} hint={`retention ${formatPercent(kpis.retention)}`} />
            <KpiCard title="Lifetime value" value={formatCurrency(kpis.ltv)} icon={Wallet} growth={null} hint="avg revenue / customer" />
            <KpiCard title="New proxy" value={formatNumber(Math.max(kpis.total - kpis.returning, 0))} icon={UserPlus} growth={null} hint="single-order accounts" />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Customer Growth"
              data={growth}
              xKey="label"
              series={[{ key: "customers", name: "Customers", color: "#8b5cf6" }]}
              currency={false}
              variant="area"
            />
            <DonutChartCard
              title="Customer Segmentation"
              data={segments.map((s) => ({
                name: s.customer_segment,
                value: toNumber(s.revenue),
              }))}
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Revenue by Customer"
              data={customers.slice(0, 10).map((c) => ({
                name: truncateLabel(c.customer_name, 14),
                revenue: toNumber(c.revenue),
              }))}
              xKey="name"
              series={[{ key: "revenue", name: "Revenue" }]}
              variant="bar"
            />
            <SeriesChart
              title="Repeat Purchase Rate"
              description="Orders per top customer"
              data={customers.slice(0, 10).map((c) => ({
                name: truncateLabel(c.customer_name, 14),
                orders: c.order_count,
              }))}
              xKey="name"
              series={[{ key: "orders", name: "Orders", color: "#0ea5e9" }]}
              variant="bar"
              currency={false}
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Top customers</CardTitle>
              <CardDescription>Ranked by revenue</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Rank</TableHead>
                    <TableHead>Customer</TableHead>
                    <TableHead>Segment</TableHead>
                    <TableHead>Revenue</TableHead>
                    <TableHead>Orders</TableHead>
                    <TableHead>AOV</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {customers.map((c) => (
                    <TableRow key={c.customer_id}>
                      <TableCell>{c.revenue_rank}</TableCell>
                      <TableCell className="font-medium">{c.customer_name}</TableCell>
                      <TableCell>{c.customer_segment}</TableCell>
                      <TableCell className="tabular-nums">{formatCurrency(c.revenue)}</TableCell>
                      <TableCell className="tabular-nums">{formatNumber(c.order_count)}</TableCell>
                      <TableCell className="tabular-nums">
                        {formatCurrency(c.average_order_value)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}
    </section>
  );
}
