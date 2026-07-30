import { AlertTriangle, PackageMinus, PackageX, RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { formatNumber } from "@/lib/format";
import type { InventoryAlertsResponse } from "@/types/api";
import { cn } from "@/lib/utils";

type Props = {
  data: InventoryAlertsResponse | undefined;
};

const TYPE_META = {
  out_of_stock: {
    label: "Out of Stock",
    icon: PackageX,
    badge: "danger" as const,
  },
  low_stock: {
    label: "Low Stock",
    icon: PackageMinus,
    badge: "warning" as const,
  },
  reorder_soon: {
    label: "Reorder Soon",
    icon: RefreshCw,
    badge: "secondary" as const,
  },
};

export function InventoryAlertsPanel({ data }: Props) {
  const alerts = data?.data ?? [];
  const counts = {
    out_of_stock: data?.out_of_stock_count ?? 0,
    low_stock: data?.low_stock_count ?? 0,
    reorder_soon: data?.reorder_soon_count ?? 0,
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Inventory Alerts</CardTitle>
        <CardDescription>Low stock, out of stock, and reorder signals</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-2">
          {(Object.keys(TYPE_META) as Array<keyof typeof TYPE_META>).map((key) => {
            const meta = TYPE_META[key];
            const Icon = meta.icon;
            return (
              <div
                key={key}
                className="rounded-xl border border-border bg-muted/40 px-3 py-2 text-center"
              >
                <Icon className="mx-auto size-4 text-muted-foreground" aria-hidden />
                <p className="mt-1 text-lg font-semibold tabular-nums">{counts[key]}</p>
                <p className="text-[11px] text-muted-foreground">{meta.label}</p>
              </div>
            );
          })}
        </div>

        {alerts.length === 0 ? (
          <div className="flex min-h-[10rem] flex-col items-center justify-center gap-2 rounded-xl border border-dashed border-border bg-muted/30 px-4 text-center">
            <AlertTriangle className="size-5 text-muted-foreground" aria-hidden />
            <p className="text-sm font-medium text-foreground">No inventory alerts</p>
            <p className="max-w-xs text-sm text-muted-foreground">
              Inventory balances are empty in the database. Alerts will appear when stock data is loaded.
            </p>
          </div>
        ) : (
          <ul className="max-h-64 space-y-2 overflow-y-auto">
            {alerts.map((alert) => {
              const key = alert.alert_type as keyof typeof TYPE_META;
              const meta = TYPE_META[key] ?? TYPE_META.low_stock;
              return (
                <li
                  key={alert.inventory_id}
                  className={cn(
                    "flex items-start justify-between gap-3 rounded-xl border border-border px-3 py-2.5",
                  )}
                >
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{alert.product_name}</p>
                    <p className="text-xs text-muted-foreground">
                      WH #{alert.warehouse_id} · Available {formatNumber(alert.quantity_available)}
                      {alert.reorder_point != null
                        ? ` · Reorder @ ${formatNumber(alert.reorder_point)}`
                        : ""}
                    </p>
                  </div>
                  <Badge variant={meta.badge}>{meta.label}</Badge>
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
