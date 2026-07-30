"use client";

import type { ReactElement } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatCompactCurrency, formatCurrency, formatNumber } from "@/lib/format";
import { cn } from "@/lib/utils";

export type ChartDatum = Record<string, string | number | null | undefined>;

const CHART_COLORS = [
  "hsl(var(--primary))",
  "hsl(var(--accent))",
  "#0ea5e9",
  "#10b981",
  "#f59e0b",
  "#8b5cf6",
  "#ef4444",
  "#64748b",
];

type ChartShellProps = {
  title: string;
  description?: string;
  className?: string;
  height?: number;
  children: ReactElement;
  empty?: boolean;
  emptyMessage?: string;
};

export function ChartShell({
  title,
  description,
  className,
  height = 300,
  children,
  empty,
  emptyMessage = "No data available for this chart.",
}: ChartShellProps) {
  return (
    <Card className={cn("h-full transition-shadow hover:shadow-md", className)}>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">{title}</CardTitle>
        {description ? <CardDescription>{description}</CardDescription> : null}
      </CardHeader>
      <CardContent className="pt-2" style={{ height }}>
        {empty ? (
          <div className="flex h-full items-center justify-center rounded-xl border border-dashed border-border bg-muted/30 px-4 text-center text-sm text-muted-foreground">
            {emptyMessage}
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            {children}
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

const tooltipStyle = {
  borderRadius: 12,
  border: "1px solid hsl(var(--border))",
  background: "hsl(var(--card))",
};

type SeriesChartProps = {
  title: string;
  description?: string;
  data: ChartDatum[];
  xKey: string;
  series: { key: string; name: string; color?: string }[];
  className?: string;
  height?: number;
  currency?: boolean;
  variant?: "line" | "area" | "bar";
};

export function SeriesChart({
  title,
  description,
  data,
  xKey,
  series,
  className,
  height = 300,
  currency = true,
  variant = "line",
}: SeriesChartProps) {
  const empty = data.length === 0;
  const tick = (v: number) => (currency ? formatCompactCurrency(v) : formatNumber(v));
  const tip = (v: unknown) => {
    const n = typeof v === "number" ? v : Number(v);
    return currency ? formatCurrency(n) : formatNumber(n);
  };

  let chart: ReactElement;
  if (variant === "area") {
    chart = (
      <AreaChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11 }} tickMargin={8} />
        <YAxis tickFormatter={tick} width={56} tick={{ fontSize: 11 }} />
        <Tooltip formatter={tip} contentStyle={tooltipStyle} />
        {series.map((s, i) => (
          <Area
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.name}
            stroke={s.color ?? CHART_COLORS[i % CHART_COLORS.length]}
            fill={s.color ?? CHART_COLORS[i % CHART_COLORS.length]}
            fillOpacity={0.15}
            strokeWidth={2}
          />
        ))}
      </AreaChart>
    );
  } else if (variant === "bar") {
    chart = (
      <BarChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 24 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis
          dataKey={xKey}
          tick={{ fontSize: 11 }}
          tickMargin={8}
          interval={0}
          angle={-20}
          textAnchor="end"
          height={60}
        />
        <YAxis tickFormatter={tick} width={56} tick={{ fontSize: 11 }} />
        <Tooltip formatter={tip} contentStyle={tooltipStyle} />
        {series.map((s, i) => (
          <Bar
            key={s.key}
            dataKey={s.key}
            name={s.name}
            fill={s.color ?? CHART_COLORS[i % CHART_COLORS.length]}
            radius={[6, 6, 0, 0]}
          />
        ))}
      </BarChart>
    );
  } else {
    chart = (
      <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11 }} tickMargin={8} />
        <YAxis tickFormatter={tick} width={56} tick={{ fontSize: 11 }} />
        <Tooltip formatter={tip} contentStyle={tooltipStyle} />
        {series.map((s, i) => (
          <Line
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.name}
            stroke={s.color ?? CHART_COLORS[i % CHART_COLORS.length]}
            strokeWidth={2.25}
            dot={false}
            activeDot={{ r: 4 }}
          />
        ))}
      </LineChart>
    );
  }

  return (
    <ChartShell title={title} description={description} className={className} height={height} empty={empty}>
      {chart}
    </ChartShell>
  );
}

type DonutProps = {
  title: string;
  description?: string;
  data: { name: string; value: number }[];
  className?: string;
  height?: number;
  currency?: boolean;
  emptyMessage?: string;
};

export function DonutChartCard({
  title,
  description,
  data,
  className,
  height = 300,
  currency = true,
  emptyMessage,
}: DonutProps) {
  return (
    <ChartShell
      title={title}
      description={description}
      className={className}
      height={height}
      empty={data.length === 0}
      emptyMessage={emptyMessage}
    >
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius="58%"
          outerRadius="82%"
          paddingAngle={2}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          formatter={(v) =>
            currency
              ? formatCurrency(typeof v === "number" ? v : Number(v))
              : formatNumber(typeof v === "number" ? v : Number(v))
          }
          contentStyle={tooltipStyle}
        />
      </PieChart>
    </ChartShell>
  );
}

type SparklineProps = {
  data: number[];
  className?: string;
  color?: string;
};

export function Sparkline({ data, className, color = "hsl(var(--primary))" }: SparklineProps) {
  if (data.length < 2) return null;
  const points = data.map((value, i) => ({ i, value }));
  return (
    <div className={cn("h-10 w-full", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={points} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
          <Area
            type="monotone"
            dataKey="value"
            stroke={color}
            fill={color}
            fillOpacity={0.18}
            strokeWidth={1.75}
            dot={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export { CHART_COLORS };
