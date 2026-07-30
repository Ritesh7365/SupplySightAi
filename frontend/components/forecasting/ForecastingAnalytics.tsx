"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

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
import { formatCompactCurrency, formatCurrency, formatPercent } from "@/lib/format";
import { LineChart, Target } from "lucide-react";

export function ForecastingAnalytics() {
  const [periods, setPeriods] = useState(6);
  const query = useQuery({
    queryKey: ["forecasting", "revenue", periods],
    queryFn: () => api.getRevenueForecast(periods),
  });

  const chartData = useMemo(() => {
    const hist = (query.data?.history ?? []).map((p) => ({
      period: p.period,
      actual: p.yhat,
      lower: p.yhat_lower,
      upper: p.yhat_upper,
      forecast: null as number | null,
    }));
    const fut = (query.data?.forecast ?? []).map((p) => ({
      period: p.period,
      actual: null as number | null,
      lower: p.yhat_lower,
      upper: p.yhat_upper,
      forecast: p.yhat,
    }));
    return [...hist, ...fut];
  }, [query.data]);

  const tableRows = [
    ...(query.data?.history ?? []).map((p) => ({ ...p, type: "history" })),
    ...(query.data?.forecast ?? []).map((p) => ({ ...p, type: "forecast" })),
  ];

  return (
    <section className="space-y-6">
      <PageHeader pathname="/forecasting">
        <div className="flex flex-wrap gap-2">
          <select
            value={periods}
            onChange={(e) => setPeriods(Number(e.target.value))}
            className="h-10 rounded-xl border border-border bg-background px-3 text-sm"
          >
            {[3, 6, 9, 12].map((n) => (
              <option key={n} value={n}>
                Next {n} months
              </option>
            ))}
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              exportCsv(
                "revenue-forecast.csv",
                tableRows.map((r) => ({
                  period: r.period,
                  yhat: r.yhat,
                  lower: r.yhat_lower,
                  upper: r.yhat_upper,
                  type: r.type,
                })),
              )
            }
          >
            Download forecast
          </Button>
        </div>
      </PageHeader>

      {query.error ? (
        <Alert title="Unable to load forecast" description={(query.error as Error).message} />
      ) : null}

      {query.isLoading ? (
        <DashboardSkeleton />
      ) : query.data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <KpiCard
              title="Model"
              value={query.data.model}
              icon={LineChart}
              growth={null}
              hint="Prophet preferred; linear fallback"
            />
            <KpiCard
              title="Forecast accuracy"
              value={query.data.mape == null ? "—" : formatPercent(100 - query.data.mape)}
              icon={Target}
              growth={null}
              hint={query.data.mape == null ? "MAPE unavailable" : `MAPE ${query.data.mape}%`}
            />
            <KpiCard
              title="Next period"
              value={
                query.data.forecast[0]
                  ? formatCurrency(query.data.forecast[0].yhat)
                  : "—"
              }
              icon={LineChart}
              growth={null}
              hint={query.data.forecast[0]?.period ?? "n/a"}
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Revenue forecast</CardTitle>
              <CardDescription>
                Fitted history with confidence interval and forward projection
              </CardDescription>
            </CardHeader>
            <CardContent className="h-[360px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                  <YAxis tickFormatter={(v) => formatCompactCurrency(v)} width={64} tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(v) => formatCurrency(typeof v === "number" ? v : Number(v))}
                    contentStyle={{
                      borderRadius: 12,
                      border: "1px solid hsl(var(--border))",
                      background: "hsl(var(--card))",
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="upper"
                    stroke="transparent"
                    fill="#0ea5e9"
                    fillOpacity={0.12}
                    name="Upper"
                  />
                  <Area
                    type="monotone"
                    dataKey="lower"
                    stroke="transparent"
                    fill="#ffffff"
                    fillOpacity={1}
                    name="Lower"
                  />
                  <Area
                    type="monotone"
                    dataKey="actual"
                    stroke="hsl(var(--primary))"
                    fill="hsl(var(--primary))"
                    fillOpacity={0.15}
                    name="Fitted"
                    connectNulls={false}
                  />
                  <Area
                    type="monotone"
                    dataKey="forecast"
                    stroke="#f59e0b"
                    fill="#f59e0b"
                    fillOpacity={0.12}
                    name="Forecast"
                    connectNulls={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Forecast table</CardTitle>
              <CardDescription>Point forecast with confidence bounds</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Period</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Forecast</TableHead>
                    <TableHead>Lower</TableHead>
                    <TableHead>Upper</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tableRows.map((r) => (
                    <TableRow key={`${r.type}-${r.period}`}>
                      <TableCell>{r.period}</TableCell>
                      <TableCell>{r.type}</TableCell>
                      <TableCell className="tabular-nums">{formatCurrency(r.yhat)}</TableCell>
                      <TableCell className="tabular-nums">{formatCurrency(r.yhat_lower)}</TableCell>
                      <TableCell className="tabular-nums">{formatCurrency(r.yhat_upper)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      ) : null}
    </section>
  );
}
