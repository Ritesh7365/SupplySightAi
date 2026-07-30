import {
  DollarSign,
  PackageCheck,
  Percent,
  ShoppingBag,
  Truck,
  Users,
  Wallet,
} from "lucide-react";

import { KpiCard } from "@/components/dashboard/KpiCard";
import type { KpiGrowth } from "@/hooks/use-executive-dashboard";
import { formatCurrency, formatNumber, formatPercent, toNumber } from "@/lib/format";
import type { ExecutiveDashboard } from "@/types/api";

type Props = {
  data: ExecutiveDashboard;
  growth: KpiGrowth;
};

export function KpiGrid({ data, growth }: Props) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
      <KpiCard
        title="Total Revenue"
        value={formatCurrency(data.total_sales)}
        icon={DollarSign}
        growth={growth.revenue}
      />
      <KpiCard
        title="Gross Profit"
        value={formatCurrency(data.total_profit)}
        icon={Wallet}
        growth={growth.profit}
        accent="bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
      />
      <KpiCard
        title="Total Orders"
        value={formatNumber(data.total_orders)}
        icon={ShoppingBag}
        growth={growth.orders}
      />
      <KpiCard
        title="Total Customers"
        value={formatNumber(data.total_customers)}
        icon={Users}
        growth={growth.customers}
      />
      <KpiCard
        title="Average Order Value"
        value={formatCurrency(data.average_order_value)}
        icon={PackageCheck}
        growth={growth.aov}
      />
      <KpiCard
        title="Late Delivery %"
        value={formatPercent(data.late_delivery_pct)}
        icon={toNumber(data.late_delivery_pct) >= 50 ? Truck : Percent}
        growth={growth.lateDelivery}
        accent="bg-amber-500/10 text-amber-700 dark:text-amber-300"
      />
    </div>
  );
}
