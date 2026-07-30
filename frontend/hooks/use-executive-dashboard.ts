"use client";

import { useQueries } from "@tanstack/react-query";

import { api } from "@/lib/api";
import { momGrowth, toNumber } from "@/lib/format";
import type {
  ExecutiveDashboard,
  GeographicPoint,
  InventoryAlertsResponse,
  MonthlySalesPoint,
  NamedMetric,
  RecentOrder,
  RecentShipment,
  ShippingModePoint,
  TopCustomerPoint,
  TopProductPoint,
} from "@/types/api";

export type RegionSlice = { region: string; sales: number };

export type KpiGrowth = {
  revenue: number | null;
  profit: number | null;
  orders: number | null;
  customers: number | null;
  aov: number | null;
  lateDelivery: number | null;
  margin: number | null;
};

function aggregateRegions(rows: GeographicPoint[]): RegionSlice[] {
  const map = new Map<string, number>();
  for (const row of rows) {
    const key = row.region?.trim() || row.market?.trim() || row.country?.trim() || "Unspecified";
    map.set(key, (map.get(key) ?? 0) + toNumber(row.sales));
  }
  return [...map.entries()]
    .map(([region, sales]) => ({ region, sales }))
    .sort((a, b) => b.sales - a.sales)
    .slice(0, 8);
}

function growthFromMonthly(points: MonthlySalesPoint[]): KpiGrowth {
  if (points.length < 2) {
    return {
      revenue: null,
      profit: null,
      orders: null,
      customers: null,
      aov: null,
      lateDelivery: null,
      margin: null,
    };
  }
  const sorted = [...points].sort((a, b) => a.year_month.localeCompare(b.year_month));
  const prev = sorted[sorted.length - 2];
  const curr = sorted[sorted.length - 1];
  return {
    revenue: momGrowth(toNumber(curr.sales), toNumber(prev.sales)),
    profit: momGrowth(toNumber(curr.profit), toNumber(prev.profit)),
    orders: momGrowth(curr.order_count, prev.order_count),
    customers: momGrowth(curr.customer_count, prev.customer_count),
    aov: momGrowth(toNumber(curr.average_order_value), toNumber(prev.average_order_value)),
    lateDelivery: null,
    margin: momGrowth(toNumber(curr.profit_margin_pct), toNumber(prev.profit_margin_pct)),
  };
}

function series(points: MonthlySalesPoint[], key: keyof MonthlySalesPoint): number[] {
  return [...points]
    .sort((a, b) => a.year_month.localeCompare(b.year_month))
    .slice(-12)
    .map((p) => toNumber(p[key] as string | number));
}

export function useExecutiveDashboardData() {
  const results = useQueries({
    queries: [
      { queryKey: ["dashboard", "executive"], queryFn: () => api.getExecutive() },
      { queryKey: ["charts", "monthly-sales"], queryFn: () => api.getMonthlySales() },
      { queryKey: ["charts", "top-products"], queryFn: () => api.getTopProducts(8) },
      { queryKey: ["charts", "top-customers"], queryFn: () => api.getTopCustomers(8) },
      { queryKey: ["dashboard", "geography"], queryFn: () => api.getGeography(500) },
      { queryKey: ["dashboard", "shipping"], queryFn: () => api.getShipping() },
      { queryKey: ["dashboard", "category"], queryFn: () => api.getRevenueByCategory(10) },
      { queryKey: ["dashboard", "department"], queryFn: () => api.getRevenueByDepartment(10) },
      { queryKey: ["dashboard", "recent-orders"], queryFn: () => api.getRecentOrders(10) },
      { queryKey: ["dashboard", "recent-shipments"], queryFn: () => api.getRecentShipments(10) },
      { queryKey: ["dashboard", "inventory-alerts"], queryFn: () => api.getInventoryAlerts(20) },
    ],
  });

  const [
    executiveQ,
    monthlyQ,
    productsQ,
    customersQ,
    geographyQ,
    shippingQ,
    categoryQ,
    departmentQ,
    ordersQ,
    shipmentsQ,
    inventoryQ,
  ] = results;

  const isLoading = executiveQ.isLoading || executiveQ.isPending;
  const isFetching = results.some((r) => r.isFetching);
  const error =
    (executiveQ.error as Error | undefined) ??
    (results.find((r) => r.error)?.error as Error | undefined);

  const monthly = (monthlyQ.data?.data ?? []) as MonthlySalesPoint[];
  const geography = (geographyQ.data?.data ?? []) as GeographicPoint[];

  return {
    isLoading,
    isFetching,
    error,
    refetchAll: () => Promise.all(results.map((r) => r.refetch())),
    executive: executiveQ.data as ExecutiveDashboard | undefined,
    monthlySales: monthly,
    topProducts: (productsQ.data?.data ?? []) as TopProductPoint[],
    topCustomers: (customersQ.data?.data ?? []) as TopCustomerPoint[],
    regions: aggregateRegions(geography),
    shipping: (shippingQ.data?.data ?? []) as ShippingModePoint[],
    categories: (categoryQ.data?.data ?? []) as NamedMetric[],
    departments: (departmentQ.data?.data ?? []) as NamedMetric[],
    recentOrders: (ordersQ.data?.data ?? []) as RecentOrder[],
    recentShipments: (shipmentsQ.data?.data ?? []) as RecentShipment[],
    inventory: inventoryQ.data as InventoryAlertsResponse | undefined,
    growth: growthFromMonthly(monthly),
    sparklines: {
      revenue: series(monthly, "sales"),
      profit: series(monthly, "profit"),
      orders: series(monthly, "order_count"),
      customers: series(monthly, "customer_count"),
      aov: series(monthly, "average_order_value"),
      margin: series(monthly, "profit_margin_pct"),
    },
  };
}
