"use client";

import { useQuery } from "@tanstack/react-query";
import { Building2, Clock3, Shield } from "lucide-react";

import { SeriesChart } from "@/components/charts";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { Alert } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";
import { formatCurrency, formatNumber, formatPercent, toNumber } from "@/lib/format";

export function VendorsAnalytics() {
  const query = useQuery({
    queryKey: ["operations", "vendors"],
    queryFn: () => api.getVendors(),
  });

  const rows = query.data?.data ?? [];
  const avgLead = query.data?.avg_lead_time_days;

  return (
    <section className="space-y-6">
      <PageHeader pathname="/vendors" />

      {query.error ? (
        <Alert title="Unable to load vendors" description={(query.error as Error).message} />
      ) : null}

      {query.isLoading ? (
        <DashboardSkeleton />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard title="Vendors" value={formatNumber(query.data?.vendor_count ?? 0)} icon={Building2} growth={null} hint="supplier master" />
            <KpiCard
              title="Avg lead time"
              value={avgLead == null ? "—" : `${toNumber(avgLead).toFixed(1)} days`}
              icon={Clock3}
              growth={null}
              hint="from vendor products"
            />
            <KpiCard
              title="On-time %"
              value={
                query.data?.on_time_pct == null ? "—" : formatPercent(query.data.on_time_pct)
              }
              icon={Shield}
              growth={null}
              hint={
                query.data?.avg_rating == null
                  ? "network average"
                  : `avg rating ${toNumber(query.data.avg_rating).toFixed(2)}`
              }
            />
            <KpiCard
              title="Purchase volume"
              value={formatCurrency(query.data?.total_purchase_volume)}
              icon={Building2}
              growth={null}
              hint="unit cost × MOQ proxy"
            />
          </div>

          {rows.length === 0 ? (
            <Alert
              title="No vendors loaded"
              description="public.vendors is a placeholder. Seed supplier masters to unlock lead-time, purchase volume, and late-delivery vendor analytics."
            />
          ) : (
            <>
              <SeriesChart
                title="Lead Time by Vendor"
                data={rows
                  .filter((v) => v.avg_lead_time_days != null)
                  .map((v) => ({
                    name: v.vendor_code,
                    days: toNumber(v.avg_lead_time_days),
                  }))}
                xKey="name"
                series={[{ key: "days", name: "Lead days", color: "#f59e0b" }]}
                variant="bar"
                currency={false}
              />

              <Card>
                <CardHeader>
                  <CardTitle>Vendor directory</CardTitle>
                  <CardDescription>Supplier master with optional risk tiers</CardDescription>
                </CardHeader>
                <CardContent>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Code</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Location</TableHead>
                        <TableHead>Risk</TableHead>
                        <TableHead>Rating</TableHead>
                        <TableHead>On-time</TableHead>
                        <TableHead>Products</TableHead>
                        <TableHead>Lead time</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {rows.map((v) => (
                        <TableRow key={v.vendor_id}>
                          <TableCell className="font-medium">{v.vendor_code}</TableCell>
                          <TableCell>{v.vendor_name}</TableCell>
                          <TableCell>
                            {[v.city, v.country].filter(Boolean).join(", ") || "—"}
                          </TableCell>
                          <TableCell>
                            {v.risk_tier ? <Badge variant="secondary">{v.risk_tier}</Badge> : "—"}
                          </TableCell>
                          <TableCell className="tabular-nums">
                            {v.rating == null ? "—" : toNumber(v.rating).toFixed(2)}
                          </TableCell>
                          <TableCell className="tabular-nums">
                            {v.on_time_delivery_pct == null
                              ? "—"
                              : formatPercent(v.on_time_delivery_pct)}
                          </TableCell>
                          <TableCell className="tabular-nums">
                            {formatNumber(v.product_count)}
                          </TableCell>
                          <TableCell className="tabular-nums">
                            {v.avg_lead_time_days == null
                              ? "—"
                              : `${toNumber(v.avg_lead_time_days).toFixed(1)}d`}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </>
          )}
        </>
      )}
    </section>
  );
}
