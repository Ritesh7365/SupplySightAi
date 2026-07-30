"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCompactCurrency, formatCurrency, toNumber, truncateLabel } from "@/lib/format";
import type { TopProductPoint } from "@/types/api";

type Props = {
  data: TopProductPoint[];
};

export function TopProductsChart({ data }: Props) {
  const chartData = [...data]
    .sort((a, b) => toNumber(b.sales) - toNumber(a.sales))
    .map((row) => ({
      name: truncateLabel(row.product_name, 24),
      fullName: row.product_name,
      sales: toNumber(row.sales),
      category: row.category_name,
    }));

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Top Products</CardTitle>
        <CardDescription>Best sellers by revenue</CardDescription>
      </CardHeader>
      <CardContent className="h-[340px]">
        {chartData.length === 0 ? (
          <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-border bg-muted/30 px-4 text-center text-sm text-muted-foreground">
            No product sales data available.
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={chartData}
              margin={{ top: 4, right: 16, left: 8, bottom: 4 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} className="stroke-border" />
              <XAxis type="number" tickFormatter={(v) => formatCompactCurrency(v)} tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 12 }} />
              <Tooltip
                formatter={(value) => formatCurrency(typeof value === "number" ? value : Number(value))}
                labelFormatter={(_, payload) => {
                  const item = payload?.[0]?.payload as { fullName?: string } | undefined;
                  return item?.fullName ?? "";
                }}
                contentStyle={{
                  borderRadius: 12,
                  border: "1px solid hsl(var(--border))",
                  background: "hsl(var(--card))",
                }}
              />
              <Bar dataKey="sales" name="Revenue" fill="hsl(var(--primary))" radius={[0, 8, 8, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
