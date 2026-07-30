"use client";

import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { Clock3, Percent, Ship, Truck } from "lucide-react";

import { DonutChartCard, SeriesChart } from "@/components/charts";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { RecentShipmentsTable } from "@/components/dashboard/RecentShipmentsTable";
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
import { formatNumber, formatPercent, toNumber } from "@/lib/format";

export function ShippingAnalytics() {
  const shippingQ = useQuery({
    queryKey: ["dashboard", "shipping", "page"],
    queryFn: () => api.getShipping(),
  });
  const execQ = useQuery({
    queryKey: ["dashboard", "executive", "shipping"],
    queryFn: () => api.getExecutive(),
  });
  const recentQ = useQuery({
    queryKey: ["dashboard", "recent-shipments", "page"],
    queryFn: () => api.getRecentShipments(15),
  });

  const modes = shippingQ.data?.data ?? [];

  const kpis = useMemo(() => {
    const shipments = modes.reduce((a, m) => a + m.shipment_count, 0);
    const late = modes.reduce((a, m) => a + m.late_delivery_count, 0);
    const weighted = modes.reduce(
      (a, m) => a + toNumber(m.avg_shipping_time_days) * m.shipment_count,
      0,
    );
    return {
      shipments,
      latePct: shipments ? (late / shipments) * 100 : toNumber(execQ.data?.late_delivery_pct),
      avgDays: shipments ? weighted / shipments : toNumber(execQ.data?.avg_lead_time_days),
      modes: modes.length,
    };
  }, [modes, execQ.data]);

  return (
    <section className="space-y-6">
      <PageHeader pathname="/shipping" />

      {shippingQ.error ? (
        <Alert title="Unable to load shipping" description={(shippingQ.error as Error).message} />
      ) : null}

      {shippingQ.isLoading ? (
        <DashboardSkeleton />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard title="Shipments" value={formatNumber(kpis.shipments)} icon={Ship} growth={null} hint="all modes" />
            <KpiCard title="Late %" value={formatPercent(kpis.latePct)} icon={Percent} growth={null} hint="late delivery risk" accent="bg-amber-500/10 text-amber-700 dark:text-amber-300" />
            <KpiCard title="Avg delivery" value={`${kpis.avgDays.toFixed(1)} days`} icon={Clock3} growth={null} hint="weighted transit" />
            <KpiCard title="Shipping modes" value={formatNumber(kpis.modes)} icon={Truck} growth={null} hint="active modes" />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Late Deliveries"
              data={modes.map((m) => ({
                name: m.shipping_mode,
                late: m.late_delivery_count,
              }))}
              xKey="name"
              series={[{ key: "late", name: "Late", color: "#ef4444" }]}
              variant="bar"
              currency={false}
            />
            <SeriesChart
              title="Delivery Time by Mode"
              data={modes.map((m) => ({
                name: m.shipping_mode,
                days: toNumber(m.avg_shipping_time_days),
              }))}
              xKey="name"
              series={[{ key: "days", name: "Avg days", color: "#0ea5e9" }]}
              variant="bar"
              currency={false}
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <DonutChartCard
              title="Carrier / Mode Mix"
              data={modes.map((m) => ({ name: m.shipping_mode, value: m.shipment_count }))}
              currency={false}
            />
            <SeriesChart
              title="Carrier Comparison"
              description="Late delivery risk %"
              data={modes.map((m) => ({
                name: m.shipping_mode,
                risk: toNumber(m.late_delivery_risk_pct),
              }))}
              xKey="name"
              series={[{ key: "risk", name: "Late risk %", color: "#f59e0b" }]}
              variant="bar"
              currency={false}
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Shipping mode performance</CardTitle>
              <CardDescription>From analytics.vw_shipping_performance</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Mode</TableHead>
                    <TableHead>Shipments</TableHead>
                    <TableHead>Late</TableHead>
                    <TableHead>Late %</TableHead>
                    <TableHead>Avg days</TableHead>
                    <TableHead>Delay rate</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {modes.map((m) => (
                    <TableRow key={m.shipping_key}>
                      <TableCell className="font-medium">{m.shipping_mode}</TableCell>
                      <TableCell className="tabular-nums">{formatNumber(m.shipment_count)}</TableCell>
                      <TableCell className="tabular-nums">{formatNumber(m.late_delivery_count)}</TableCell>
                      <TableCell className="tabular-nums">
                        {formatPercent(m.late_delivery_risk_pct)}
                      </TableCell>
                      <TableCell className="tabular-nums">
                        {toNumber(m.avg_shipping_time_days).toFixed(1)}
                      </TableCell>
                      <TableCell className="tabular-nums">
                        {formatPercent(m.delay_rate_pct)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <RecentShipmentsTable data={recentQ.data?.data ?? []} />
        </>
      )}
    </section>
  );
}
