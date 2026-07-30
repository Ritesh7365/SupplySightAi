import {
  Boxes,
  Building2,
  Clock3,
  DollarSign,
  PackageCheck,
  Percent,
  ShoppingBag,
  TrendingUp,
  Truck,
  Users,
  Warehouse,
  Wallet,
} from "lucide-react";

import { KpiCard } from "@/components/dashboard/KpiCard";
import type { KpiGrowth } from "@/hooks/use-executive-dashboard";
import { formatCurrency, formatNumber, formatPercent, toNumber } from "@/lib/format";
import type { ExecutiveDashboard } from "@/types/api";

type Props = {
  data: ExecutiveDashboard;
  growth: KpiGrowth;
  sparklines: {
    revenue: number[];
    profit: number[];
    orders: number[];
    customers: number[];
    aov: number[];
    margin: number[];
  };
};

export function KpiGrid({ data, growth, sparklines }: Props) {
  const revenueGrowth = growth.revenue;

  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
      <KpiCard
        title="Total Revenue"
        value={formatCurrency(data.total_sales)}
        icon={DollarSign}
        growth={growth.revenue}
        sparkline={sparklines.revenue}
      />
      <KpiCard
        title="Gross Profit"
        value={formatCurrency(data.total_profit)}
        icon={Wallet}
        growth={growth.profit}
        sparkline={sparklines.profit}
        accent="bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
      />
      <KpiCard
        title="Orders"
        value={formatNumber(data.total_orders)}
        icon={ShoppingBag}
        growth={growth.orders}
        sparkline={sparklines.orders}
      />
      <KpiCard
        title="Customers"
        value={formatNumber(data.total_customers)}
        icon={Users}
        growth={growth.customers}
        sparkline={sparklines.customers}
      />
      <KpiCard
        title="Average Order Value"
        value={formatCurrency(data.average_order_value)}
        icon={PackageCheck}
        growth={growth.aov}
        sparkline={sparklines.aov}
      />
      <KpiCard
        title="Late Delivery %"
        value={formatPercent(data.late_delivery_pct)}
        icon={Truck}
        growth={growth.lateDelivery}
        accent="bg-amber-500/10 text-amber-700 dark:text-amber-300"
      />
      <KpiCard
        title="Profit Margin %"
        value={formatPercent(data.overall_profit_margin_pct)}
        icon={Percent}
        growth={growth.margin}
        sparkline={sparklines.margin}
        accent="bg-sky-500/10 text-sky-700 dark:text-sky-300"
      />
      <KpiCard
        title="Revenue Growth %"
        value={revenueGrowth == null ? "—" : formatPercent(revenueGrowth)}
        icon={TrendingUp}
        growth={revenueGrowth}
        hint="month over month"
        accent="bg-violet-500/10 text-violet-700 dark:text-violet-300"
      />
      <KpiCard
        title="Avg Lead Time"
        value={
          data.avg_lead_time_days == null
            ? "—"
            : `${toNumber(data.avg_lead_time_days).toFixed(1)} days`
        }
        icon={Clock3}
        growth={null}
        hint="weighted shipping transit"
      />
      <KpiCard
        title="Vendor Count"
        value={formatNumber(data.vendor_count ?? 0)}
        icon={Building2}
        growth={null}
        hint={data.vendor_count ? "active vendors" : "seed vendors to populate"}
        muted={!data.vendor_count}
      />
      <KpiCard
        title="Inventory SKUs"
        value={formatNumber(data.inventory_sku_count ?? 0)}
        icon={Boxes}
        growth={null}
        hint={
          data.inventory_units != null
            ? `${formatNumber(data.inventory_units)} units on hand`
            : "inventory layer pending"
        }
        muted={!data.inventory_sku_count}
      />
      <KpiCard
        title="Warehouse Utilization"
        value={
          data.warehouse_utilization_pct == null
            ? data.warehouse_count
              ? formatNumber(data.warehouse_count)
              : "—"
            : formatPercent(data.warehouse_utilization_pct)
        }
        icon={Warehouse}
        growth={null}
        hint={
          data.warehouse_utilization_pct == null
            ? data.warehouse_count
              ? "warehouses registered"
              : "capacity metrics pending"
            : "of capacity used"
        }
        muted={data.warehouse_utilization_pct == null}
      />
    </div>
  );
}
