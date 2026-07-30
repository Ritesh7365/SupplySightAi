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
  avg_lead_time_days?: string | number | null;
  vendor_count?: number;
  warehouse_count?: number;
  inventory_sku_count?: number;
  inventory_units?: string | number | null;
  inventory_turnover?: string | number | null;
  warehouse_utilization_pct?: string | number | null;
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

export type TopCustomerPoint = {
  customer_id: number;
  customer_name: string;
  customer_segment: string;
  revenue: string | number;
  profit: string | number;
  order_count: number;
  average_order_value: string | number | null;
  revenue_rank: number;
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

export type ShippingModePoint = {
  shipping_key: number;
  shipping_mode: string;
  shipping_mode_group: string;
  shipment_count: number;
  late_delivery_count: number;
  late_delivery_risk_pct: string | number | null;
  avg_shipping_time_days: string | number | null;
  delay_rate_pct: string | number | null;
};

export type NamedMetric = {
  name: string;
  sales: string | number;
  profit: string | number;
  order_count: number;
  units_sold: number;
};

export type RecentOrder = {
  order_id: number;
  customer_name: string;
  revenue: string | number;
  status: string;
  order_date: string;
};

export type RecentShipment = {
  order_id: number;
  shipping_mode: string;
  delivery_status: string;
  actual_days: number | null;
  scheduled_days: number | null;
  late_delivery: boolean;
  order_date: string | null;
  customer_name: string | null;
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

export type CustomersDashboard = {
  customers: TopCustomerPoint[];
  segments: {
    customer_segment: string;
    customer_count: number;
    revenue: string | number;
    average_order_value: string | number | null;
  }[];
  count: number;
  limit?: number | null;
};

export type SalesPerformancePoint = {
  year_number: number;
  month_number: number;
  year_month: string;
  month_name: string;
  market: string | null;
  region: string | null;
  sales: string | number;
  profit: string | number;
  order_count: number;
  customer_count: number;
  average_order_value: string | number | null;
  profit_margin_pct: string | number | null;
};

export type InventorySummary = {
  sku_count: number;
  total_units: string | number;
  inventory_value_proxy: string | number | null;
  low_stock_count: number;
  out_of_stock_count: number;
  below_safety_count?: number;
  warehouse_count: number;
  inventory_turnover: string | number | null;
  avg_warehouse_utilization_pct?: string | number | null;
  top_inventory_value?: string | number | null;
};

export type InventoryBalance = {
  inventory_id: number;
  warehouse_id: number;
  warehouse_name: string | null;
  product_id: number;
  product_name: string;
  quantity_on_hand: string | number;
  quantity_available: string | number;
  reorder_point: string | number | null;
  safety_stock?: string | number | null;
  maximum_stock?: string | number | null;
  inventory_value?: string | number | null;
  stock_status?: string | null;
};

export type WarehouseRow = {
  warehouse_id: number;
  warehouse_code: string;
  warehouse_name: string;
  warehouse_type?: string | null;
  city: string | null;
  state_code: string | null;
  country: string | null;
  latitude?: string | number | null;
  longitude?: string | number | null;
  is_active: boolean;
  capacity?: string | number | null;
  sku_count: number;
  products_stored?: number;
  units_on_hand: string | number;
  inventory_value?: string | number | null;
  utilization_pct: string | number | null;
  occupancy_pct?: string | number | null;
  orders_handled?: number;
};

export type VendorRow = {
  vendor_id: number;
  vendor_code: string;
  vendor_name: string;
  country: string | null;
  city: string | null;
  risk_tier: string | null;
  is_active: boolean;
  product_count: number;
  avg_lead_time_days: string | number | null;
  rating?: string | number | null;
  on_time_delivery_pct?: string | number | null;
  purchase_volume_proxy?: string | number | null;
  late_delivery_pct?: string | number | null;
};

export type VendorsResponse = ListResponse<VendorRow> & {
  vendor_count: number;
  avg_lead_time_days: string | number | null;
  avg_rating?: string | number | null;
  on_time_pct: string | number | null;
  total_purchase_volume?: string | number | null;
};

export type WarehousesResponse = ListResponse<WarehouseRow> & {
  warehouse_count: number;
  total_capacity?: string | number | null;
  avg_utilization_pct?: string | number | null;
  total_inventory_value?: string | number | null;
};

export type ForecastPoint = {
  period: string;
  yhat: number;
  yhat_lower: number;
  yhat_upper: number;
  is_forecast: boolean;
};

export type ForecastResponse = {
  metric: string;
  model: string;
  history: ForecastPoint[];
  forecast: ForecastPoint[];
  mape: number | null;
};

export type AiInsightResponse = {
  question: string;
  answer: string;
  sources: string[];
  model: string;
};
