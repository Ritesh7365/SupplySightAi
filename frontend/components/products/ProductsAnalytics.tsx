"use client";

import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Layers, Package, Percent, Wallet } from "lucide-react";

import { SeriesChart } from "@/components/charts";
import { DashboardSkeleton } from "@/components/dashboard/DashboardSkeleton";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { PageHeader } from "@/components/layout/PageHeader";
import { Alert } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
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
import { exportCsv } from "@/lib/export";
import { formatCurrency, formatNumber, formatPercent, toNumber, truncateLabel } from "@/lib/format";

export function ProductsAnalytics() {
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<"best" | "lowest" | "profit">("best");
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const bestQ = useQuery({
    queryKey: ["products", "best"],
    queryFn: () => api.getProducts({ limit: 200, lowest: false }),
  });
  const lowQ = useQuery({
    queryKey: ["products", "lowest"],
    queryFn: () => api.getProducts({ limit: 50, lowest: true }),
  });
  const categoryQ = useQuery({
    queryKey: ["dashboard", "category", "products"],
    queryFn: () => api.getRevenueByCategory(12),
  });

  const products = bestQ.data?.data ?? [];
  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    let rows = products.filter((p) =>
      !q
        ? true
        : p.product_name.toLowerCase().includes(q) ||
          p.category_name.toLowerCase().includes(q) ||
          p.department_name.toLowerCase().includes(q),
    );
    if (sort === "lowest") {
      rows = [...(lowQ.data?.data ?? [])].filter((p) =>
        !q
          ? true
          : p.product_name.toLowerCase().includes(q) ||
            p.category_name.toLowerCase().includes(q),
      );
    } else if (sort === "profit") {
      rows = [...rows].sort((a, b) => toNumber(b.profit) - toNumber(a.profit));
    }
    return rows;
  }, [products, lowQ.data, search, sort]);

  const pageRows = filtered.slice(page * pageSize, page * pageSize + pageSize);
  const pageCount = Math.max(1, Math.ceil(filtered.length / pageSize));

  const kpis = useMemo(() => {
    const revenue = products.reduce((a, p) => a + toNumber(p.sales), 0);
    const profit = products.reduce((a, p) => a + toNumber(p.profit), 0);
    const categories = new Set(products.map((p) => p.category_name)).size;
    return {
      products: products.length,
      categories,
      revenue,
      profit,
      margin: revenue ? (profit / revenue) * 100 : 0,
    };
  }, [products]);

  const abc = useMemo(() => {
    const sorted = [...products].sort((a, b) => toNumber(b.sales) - toNumber(a.sales));
    const total = sorted.reduce((a, p) => a + toNumber(p.sales), 0) || 1;
    let running = 0;
    const buckets = { A: 0, B: 0, C: 0 };
    for (const p of sorted) {
      running += toNumber(p.sales);
      const share = running / total;
      if (share <= 0.8) buckets.A += 1;
      else if (share <= 0.95) buckets.B += 1;
      else buckets.C += 1;
    }
    return [
      { name: "A (80%)", value: buckets.A },
      { name: "B (15%)", value: buckets.B },
      { name: "C (5%)", value: buckets.C },
    ];
  }, [products]);

  return (
    <section className="space-y-6">
      <PageHeader pathname="/products">
        <div className="flex flex-wrap gap-2">
          <input
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(0);
            }}
            placeholder="Search products…"
            className="h-10 min-w-[14rem] rounded-xl border border-border bg-background px-3 text-sm"
          />
          <select
            value={sort}
            onChange={(e) => {
              setSort(e.target.value as typeof sort);
              setPage(0);
            }}
            className="h-10 rounded-xl border border-border bg-background px-3 text-sm"
          >
            <option value="best">Best selling</option>
            <option value="lowest">Low selling</option>
            <option value="profit">Most profitable</option>
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() =>
              exportCsv(
                "products.csv",
                filtered.map((p) => ({
                  product_id: p.product_id,
                  name: p.product_name,
                  category: p.category_name,
                  department: p.department_name,
                  sales: toNumber(p.sales),
                  profit: toNumber(p.profit),
                  units: p.units_sold,
                })),
              )
            }
          >
            Export CSV
          </Button>
        </div>
      </PageHeader>

      {bestQ.error ? (
        <Alert title="Unable to load products" description={(bestQ.error as Error).message} />
      ) : null}

      {bestQ.isLoading ? (
        <DashboardSkeleton />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <KpiCard title="Products" value={formatNumber(kpis.products)} icon={Package} growth={null} hint="in ranked set" />
            <KpiCard title="Categories" value={formatNumber(kpis.categories)} icon={Layers} growth={null} hint="distinct" />
            <KpiCard title="Revenue" value={formatCurrency(kpis.revenue)} icon={Wallet} growth={null} hint="product rollup" />
            <KpiCard title="Profit margin" value={formatPercent(kpis.margin)} icon={Percent} growth={null} hint={`profit ${formatCurrency(kpis.profit)}`} />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Top Selling Products"
              data={products.slice(0, 10).map((p) => ({
                name: truncateLabel(p.product_name, 14),
                sales: toNumber(p.sales),
              }))}
              xKey="name"
              series={[{ key: "sales", name: "Revenue" }]}
              variant="bar"
            />
            <SeriesChart
              title="Low Selling Products"
              data={(lowQ.data?.data ?? []).slice(0, 10).map((p) => ({
                name: truncateLabel(p.product_name, 14),
                sales: toNumber(p.sales),
              }))}
              xKey="name"
              series={[{ key: "sales", name: "Revenue", color: "#ef4444" }]}
              variant="bar"
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <SeriesChart
              title="Product Profitability"
              data={[...products]
                .sort((a, b) => toNumber(b.profit) - toNumber(a.profit))
                .slice(0, 10)
                .map((p) => ({
                  name: truncateLabel(p.product_name, 14),
                  profit: toNumber(p.profit),
                }))}
              xKey="name"
              series={[{ key: "profit", name: "Profit", color: "#10b981" }]}
              variant="bar"
            />
            <SeriesChart
              title="Category Performance"
              data={(categoryQ.data?.data ?? []).map((c) => ({
                name: truncateLabel(c.name, 14),
                sales: toNumber(c.sales),
              }))}
              xKey="name"
              series={[{ key: "sales", name: "Revenue", color: "#f59e0b" }]}
              variant="bar"
            />
          </div>

          <SeriesChart
            title="ABC Analysis"
            description="SKU count by cumulative revenue contribution"
            data={abc.map((b) => ({ name: b.name, skus: b.value }))}
            xKey="name"
            series={[{ key: "skus", name: "SKUs", color: "#8b5cf6" }]}
            variant="bar"
            currency={false}
          />

          <Card>
            <CardHeader className="flex flex-row items-center justify-between gap-3">
              <div>
                <CardTitle>Product catalog</CardTitle>
                <CardDescription>
                  Showing {pageRows.length} of {filtered.length} products
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 0}
                  onClick={() => setPage((p) => Math.max(0, p - 1))}
                >
                  Prev
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= pageCount - 1}
                  onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
                >
                  Next
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Department</TableHead>
                    <TableHead>Sales</TableHead>
                    <TableHead>Profit</TableHead>
                    <TableHead>Units</TableHead>
                    <TableHead>Margin</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pageRows.map((p) => (
                    <TableRow key={p.product_id}>
                      <TableCell className="max-w-[16rem] truncate font-medium">
                        {p.product_name}
                      </TableCell>
                      <TableCell>{p.category_name}</TableCell>
                      <TableCell>{p.department_name}</TableCell>
                      <TableCell className="tabular-nums">{formatCurrency(p.sales)}</TableCell>
                      <TableCell className="tabular-nums">{formatCurrency(p.profit)}</TableCell>
                      <TableCell className="tabular-nums">{formatNumber(p.units_sold)}</TableCell>
                      <TableCell className="tabular-nums">
                        {formatPercent(p.profit_margin_pct)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}
    </section>
  );
}
