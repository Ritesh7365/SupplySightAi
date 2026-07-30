"use client";

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
import { formatDate } from "@/lib/format";
import type { RecentShipment } from "@/types/api";

type Props = { data: RecentShipment[] };

export function RecentShipmentsTable({ data }: Props) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Recent Shipments</CardTitle>
        <CardDescription>Latest delivery performance across shipping modes</CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="flex min-h-[12rem] items-center justify-center rounded-xl border border-dashed border-border bg-muted/30 px-4 text-center text-sm text-muted-foreground">
            No recent shipments found.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Mode</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Days</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((row) => (
                <TableRow key={`${row.order_id}-${row.order_date}`}>
                  <TableCell className="font-medium tabular-nums">#{row.order_id}</TableCell>
                  <TableCell className="max-w-[9rem] truncate">{row.customer_name || "—"}</TableCell>
                  <TableCell>{row.shipping_mode}</TableCell>
                  <TableCell>
                    <Badge variant={row.late_delivery ? "danger" : "success"}>
                      {row.late_delivery ? "Late" : row.delivery_status}
                    </Badge>
                  </TableCell>
                  <TableCell className="tabular-nums">
                    {row.actual_days ?? "—"}
                    {row.scheduled_days != null ? ` / ${row.scheduled_days}` : ""}
                  </TableCell>
                  <TableCell className="whitespace-nowrap text-muted-foreground">
                    {row.order_date ? formatDate(row.order_date) : "—"}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
