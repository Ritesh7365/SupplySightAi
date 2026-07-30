"use client";

import { InventoryAlertsPanel } from "@/components/dashboard/InventoryAlertsPanel";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { KpiGrid } from "@/components/dashboard/KpiGrid";
import { RecentOrdersTable } from "@/components/dashboard/RecentOrdersTable";
import { RegionDonutChart } from "@/components/dashboard/RegionDonutChart";
import { RevenueTrendChart } from "@/components/dashboard/RevenueTrendChart";
import { TopProductsChart } from "@/components/dashboard/TopProductsChart";
import { PageHeader } from "@/components/layout/PageHeader";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { useExecutiveDashboardData } from "@/hooks/use-executive-dashboard";
import { formatDate } from "@/lib/format";

export function ExecutiveDashboard() {
  const {
    isLoading,
    error,
    refetchAll,
    executive,
    monthlySales,
    topProducts,
    regions,
    recentOrders,
    inventory,
    growth,
  } = useExecutiveDashboardData();

  return (
    <section className="space-y-6">
      <PageHeader pathname="/dashboard">
        {executive?.refreshed_at ? (
          <p className="text-sm text-muted-foreground">
            Data refreshed {formatDate(executive.refreshed_at)}
          </p>
        ) : null}
      </PageHeader>

      {error ? (
        <Alert
          title="Unable to load executive dashboard"
          description={error.message || "The analytics API did not respond successfully."}
          action={
            <Button variant="outline" size="sm" onClick={() => void refetchAll()}>
              Retry
            </Button>
          }
        />
      ) : null}

      {isLoading && !executive ? (
        <DashboardSkeleton />
      ) : executive ? (
        <>
          <KpiGrid data={executive} growth={growth} />

          <div className="grid gap-4 xl:grid-cols-5">
            <div className="xl:col-span-3">
              <RevenueTrendChart data={monthlySales} />
            </div>
            <div className="xl:col-span-2">
              <RegionDonutChart data={regions} />
            </div>
          </div>

          <div className="grid gap-4 xl:grid-cols-5">
            <div className="xl:col-span-3">
              <TopProductsChart data={topProducts} />
            </div>
            <div className="xl:col-span-2">
              <InventoryAlertsPanel data={inventory} />
            </div>
          </div>

          <RecentOrdersTable data={recentOrders} />
        </>
      ) : !error ? (
        <div className="flex min-h-[16rem] items-center justify-center rounded-2xl border border-dashed border-border bg-muted/40 px-6 text-center">
          <div>
            <p className="text-base font-medium text-foreground">No executive metrics yet</p>
            <p className="mt-2 max-w-md text-sm text-muted-foreground">
              The analytics API returned no KPI payload. Confirm the warehouse and analytics layer are loaded.
            </p>
          </div>
        </div>
      ) : null}
    </section>
  );
}
