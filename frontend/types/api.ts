/** API response types aligned with FastAPI schemas. */

export type ExecutiveDashboard = {
  total_sales: string | number;
  total_profit: string | number;
  total_orders: number;
  total_customers: number;
  average_order_value: string | number | null;
  late_delivery_pct: string | number | null;
  total_shipments: number;
  late_shipments: number;
  overall_profit_margin_pct: string | number | null;
  refreshed_at: string;
};

export type MonthlySalesPoint = {
  year_number: number;
  month_number: number;
  year_month: string;
  month_name: string;
  quarter_number: number;
  quarter_name: string;
  sales: string | number;
  profit: string | number;
  discount: string | number;
  units_sold: number;
  order_count: number;
  customer_count: number;
  average_order_value: string | number | null;
  profit_margin_pct: string | number | null;
};

export type TopProductPoint = {
  product_id: number;
  product_name: string;
  category_name: string;
  department_name: string;
  sales: string | number;
  profit: string | number;
  units_sold: number;
  best_selling_rank: number;
  profit_margin_pct: string | number | null;
};

export type GeographicPoint = {
  market: string | null;
  region: string | null;
  country: string | null;
  state: string | null;
  city: string | null;
  sales: string | number;
  profit: string | number;
  order_count: number;
};

export type RecentOrder = {
  order_id: number;
  customer_name: string;
  revenue: string | number;
  status: string;
  order_date: string;
};

export type InventoryAlert = {
  inventory_id: number;
  product_id: number;
  product_name: string;
  warehouse_id: number;
  quantity_available: string | number;
  reorder_point: string | number | null;
  alert_type: "out_of_stock" | "low_stock" | "reorder_soon" | string;
};

export type ListResponse<T> = {
  data: T[];
  count: number;
  limit?: number | null;
};

export type InventoryAlertsResponse = ListResponse<InventoryAlert> & {
  out_of_stock_count: number;
  low_stock_count: number;
  reorder_soon_count: number;
};
