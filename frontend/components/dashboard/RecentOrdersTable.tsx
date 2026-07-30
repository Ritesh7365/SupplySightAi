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
import { formatCurrency, formatDate } from "@/lib/format";
import type { RecentOrder } from "@/types/api";

type Props = {
  data: RecentOrder[];
};

function statusVariant(status: string): "success" | "warning" | "danger" | "secondary" {
  const s = status.toLowerCase();
  if (s.includes("complete") || s.includes("delivered")) return "success";
  if (s.includes("pending") || s.includes("processing")) return "warning";
  if (s.includes("cancel") || s.includes("suspend")) return "danger";
  return "secondary";
}

export function RecentOrdersTable({ data }: Props) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Recent Orders</CardTitle>
        <CardDescription>Latest orders with revenue and fulfillment status</CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="flex min-h-[12rem] items-center justify-center rounded-xl border border-dashed border-border bg-muted/30 px-4 text-center text-sm text-muted-foreground">
            No recent orders found.
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Order ID</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Revenue</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((order) => (
                <TableRow key={order.order_id}>
                  <TableCell className="font-medium tabular-nums">#{order.order_id}</TableCell>
                  <TableCell className="max-w-[10rem] truncate sm:max-w-none">
                    {order.customer_name || "—"}
                  </TableCell>
                  <TableCell className="tabular-nums">{formatCurrency(order.revenue)}</TableCell>
                  <TableCell>
                    <Badge variant={statusVariant(order.status)}>{order.status}</Badge>
                  </TableCell>
                  <TableCell className="whitespace-nowrap text-muted-foreground">
                    {formatDate(order.order_date)}
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
