import type { LucideIcon } from "lucide-react";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { formatGrowth } from "@/lib/format";
import { cn } from "@/lib/utils";

type KpiCardProps = {
  title: string;
  value: string;
  icon: LucideIcon;
  growth: number | null;
  accent?: string;
};

export function KpiCard({ title, value, icon: Icon, growth, accent }: KpiCardProps) {
  const positive = growth != null && growth > 0;
  const negative = growth != null && growth < 0;
  const TrendIcon = positive ? TrendingUp : negative ? TrendingDown : Minus;

  return (
    <Card className="overflow-hidden transition-shadow hover:shadow-md">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="mt-2 truncate text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
              {value}
            </p>
          </div>
          <span
            className={cn(
              "flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary",
              accent,
            )}
          >
            <Icon className="size-5" aria-hidden />
          </span>
        </div>
        <div className="mt-4 flex items-center gap-2 text-sm">
          <span
            className={cn(
              "inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-semibold",
              positive && "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
              negative && "bg-red-500/15 text-red-700 dark:text-red-300",
              !positive && !negative && "bg-muted text-muted-foreground",
            )}
          >
            <TrendIcon className="size-3.5" aria-hidden />
            {formatGrowth(growth)}
          </span>
          <span className="text-xs text-muted-foreground">vs prior month</span>
        </div>
      </CardContent>
    </Card>
  );
}
