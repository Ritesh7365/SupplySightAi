"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { RegionSlice } from "@/hooks/use-executive-dashboard";
import { formatCompactCurrency, formatCurrency } from "@/lib/format";

const COLORS = [
  "hsl(174 62% 32%)",
  "hsl(28 85% 48%)",
  "hsl(210 55% 42%)",
  "hsl(152 45% 40%)",
  "hsl(200 60% 45%)",
  "hsl(340 55% 48%)",
  "hsl(45 80% 45%)",
  "hsl(260 35% 48%)",
];

type Props = {
  data: RegionSlice[];
};

export function RegionDonutChart({ data }: Props) {
  const total = data.reduce((sum, row) => sum + row.sales, 0);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Revenue by Region</CardTitle>
        <CardDescription>Aggregated from geographic performance</CardDescription>
      </CardHeader>
      <CardContent className="h-[320px]">
        {data.length === 0 ? (
          <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-border bg-muted/30 px-4 text-center text-sm text-muted-foreground">
            No regional sales data available.
          </div>
        ) : (
          <div className="grid h-full grid-cols-1 gap-2 sm:grid-cols-[1fr_0.9fr]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  dataKey="sales"
                  nameKey="region"
                  innerRadius="58%"
                  outerRadius="82%"
                  paddingAngle={2}
                >
                  {data.map((entry, index) => (
                    <Cell key={entry.region} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => formatCurrency(typeof value === "number" ? value : Number(value))}
                  contentStyle={{
                    borderRadius: 12,
                    border: "1px solid hsl(var(--border))",
                    background: "hsl(var(--card))",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            <ul className="flex flex-col justify-center gap-2 overflow-y-auto pr-1 text-sm">
              {data.map((row, index) => (
                <li key={row.region} className="flex items-center justify-between gap-2">
                  <span className="flex min-w-0 items-center gap-2">
                    <span
                      className="size-2.5 shrink-0 rounded-full"
                      style={{ background: COLORS[index % COLORS.length] }}
                    />
                    <span className="truncate">{row.region}</span>
                  </span>
                  <span className="shrink-0 font-medium tabular-nums text-muted-foreground">
                    {formatCompactCurrency(row.sales)}
                    <span className="ml-1 text-xs">
                      ({total ? ((row.sales / total) * 100).toFixed(0) : 0}%)
                    </span>
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
