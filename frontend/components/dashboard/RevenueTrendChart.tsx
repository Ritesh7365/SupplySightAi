"use client";

import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCompactCurrency, formatCurrency, toNumber } from "@/lib/format";
import type { MonthlySalesPoint } from "@/types/api";

type Props = {
  data: MonthlySalesPoint[];
};

export function RevenueTrendChart({ data }: Props) {
  const chartData = [...data]
    .sort((a, b) => a.year_month.localeCompare(b.year_month))
    .map((row) => ({
      label: `${row.month_name.slice(0, 3)} ${String(row.year_number).slice(2)}`,
      sales: toNumber(row.sales),
      profit: toNumber(row.profit),
      year_month: row.year_month,
    }));

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Revenue Trend</CardTitle>
        <CardDescription>Monthly sales from analytics.mv_monthly_sales</CardDescription>
      </CardHeader>
      <CardContent className="h-[320px] pt-2">
        {chartData.length === 0 ? (
          <EmptyChart message="No monthly sales data available." />
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
              <XAxis dataKey="label" tick={{ fontSize: 12 }} tickMargin={8} />
              <YAxis
                tickFormatter={(v) => formatCompactCurrency(v)}
                width={64}
                tick={{ fontSize: 12 }}
              />
              <Tooltip
                formatter={(value) => formatCurrency(typeof value === "number" ? value : Number(value))}
                labelFormatter={(label) => String(label)}
                contentStyle={{
                  borderRadius: 12,
                  border: "1px solid hsl(var(--border))",
                  background: "hsl(var(--card))",
                }}
              />
              <Line
                type="monotone"
                dataKey="sales"
                name="Revenue"
                stroke="hsl(var(--primary))"
                strokeWidth={2.5}
                dot={false}
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="profit"
                name="Profit"
                stroke="hsl(var(--accent))"
                strokeWidth={2}
                dot={false}
                strokeDasharray="4 4"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

function EmptyChart({ message }: { message: string }) {
  return (
    <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-border bg-muted/30 px-4 text-center text-sm text-muted-foreground">
      {message}
    </div>
  );
}
