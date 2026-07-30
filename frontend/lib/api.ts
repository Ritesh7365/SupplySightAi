import type {
  AiInsightResponse,
  CustomersDashboard,
  ExecutiveDashboard,
  ForecastResponse,
  GeographicPoint,
  InventoryAlertsResponse,
  InventoryBalance,
  InventorySummary,
  ListResponse,
  MonthlySalesPoint,
  NamedMetric,
  RecentOrder,
  RecentShipment,
  SalesPerformancePoint,
  ShippingModePoint,
  TopCustomerPoint,
  TopProductPoint,
  VendorsResponse,
  WarehouseRow,
  WarehousesResponse,
} from "@/types/api";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "http://127.0.0.1:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

const FETCH_TIMEOUT_MS = 20_000;

function buildQuery(params?: Record<string, string | number | boolean | undefined | null>): string {
  if (!params) return "";
  const qs = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    qs.set(key, String(value));
  }
  const s = qs.toString();
  return s ? `?${s}` : "";
}

async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      ...init,
      signal: init?.signal ?? controller.signal,
      headers: {
        Accept: "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });

    if (!response.ok) {
      let message = `Request failed (${response.status})`;
      try {
        const body = (await response.json()) as { error?: { message?: string } };
        if (body?.error?.message) message = body.error.message;
      } catch {
        /* ignore parse errors */
      }
      throw new ApiError(message, response.status);
    }

    return (await response.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError(
        `Analytics API timed out after ${FETCH_TIMEOUT_MS / 1000}s. Is the backend running on ${API_BASE}?`,
        408,
      );
    }
    const message =
      err instanceof TypeError
        ? `Cannot reach analytics API at ${API_BASE}. Start the backend with: cd backend && python -m uvicorn app.main:app --reload`
        : err instanceof Error
          ? err.message
          : "Unknown API error";
    throw new ApiError(message, 0);
  } finally {
    clearTimeout(timeoutId);
  }
}

async function apiPost<T>(path: string, body: unknown, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    const response = await fetch(url, {
      ...init,
      method: "POST",
      signal: init?.signal ?? controller.signal,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      body: JSON.stringify(body),
      cache: "no-store",
    });

    if (!response.ok) {
      let message = `Request failed (${response.status})`;
      try {
        const parsed = (await response.json()) as { error?: { message?: string } };
        if (parsed?.error?.message) message = parsed.error.message;
      } catch {
        /* ignore */
      }
      throw new ApiError(message, response.status);
    }

    return (await response.json()) as T;
  } catch (err) {
    if (err instanceof ApiError) throw err;
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError(`Analytics API timed out after ${FETCH_TIMEOUT_MS / 1000}s`, 408);
    }
    throw new ApiError(err instanceof Error ? err.message : "Unknown API error", 0);
  } finally {
    clearTimeout(timeoutId);
  }
}

export const api = {
  getExecutive: () => apiGet<ExecutiveDashboard>("/dashboard/executive"),
  getMonthlySales: (year?: number) =>
    apiGet<ListResponse<MonthlySalesPoint>>(
      `/charts/monthly-sales${buildQuery({ year })}`,
    ),
  getTopProducts: (limit = 10) =>
    apiGet<ListResponse<TopProductPoint>>(`/charts/top-products${buildQuery({ limit })}`),
  getTopCustomers: (limit = 10) =>
    apiGet<ListResponse<TopCustomerPoint>>(`/charts/top-customers${buildQuery({ limit })}`),
  getGeography: (limit = 500) =>
    apiGet<ListResponse<GeographicPoint>>(`/dashboard/geography${buildQuery({ limit })}`),
  getRecentOrders: (limit = 10) =>
    apiGet<ListResponse<RecentOrder>>(`/dashboard/recent-orders${buildQuery({ limit })}`),
  getRecentShipments: (limit = 10) =>
    apiGet<ListResponse<RecentShipment>>(`/dashboard/recent-shipments${buildQuery({ limit })}`),
  getInventoryAlerts: (limit = 20) =>
    apiGet<InventoryAlertsResponse>(`/dashboard/inventory-alerts${buildQuery({ limit })}`),
  getShipping: () => apiGet<ListResponse<ShippingModePoint>>("/dashboard/shipping"),
  getRevenueByCategory: (limit = 12) =>
    apiGet<ListResponse<NamedMetric>>(`/dashboard/revenue-by-category${buildQuery({ limit })}`),
  getRevenueByDepartment: (limit = 12) =>
    apiGet<ListResponse<NamedMetric>>(`/dashboard/revenue-by-department${buildQuery({ limit })}`),
  getSales: (params?: { year?: number; market?: string; region?: string; limit?: number }) =>
    apiGet<ListResponse<SalesPerformancePoint>>(`/dashboard/sales${buildQuery(params)}`),
  getCustomers: (params?: { segment?: string; limit?: number }) =>
    apiGet<CustomersDashboard>(`/dashboard/customers${buildQuery(params)}`),
  getProducts: (params?: { limit?: number; lowest?: boolean }) =>
    apiGet<ListResponse<TopProductPoint>>(`/dashboard/products${buildQuery(params)}`),
  getInventorySummary: () => apiGet<InventorySummary>("/operations/inventory/summary"),
  getInventoryBalances: (limit = 100) =>
    apiGet<ListResponse<InventoryBalance>>(`/operations/inventory/balances${buildQuery({ limit })}`),
  getWarehouses: () => apiGet<WarehousesResponse>("/operations/warehouses"),
  getVendors: () => apiGet<VendorsResponse>("/operations/vendors"),
  getRevenueForecast: (periods = 6) =>
    apiGet<ForecastResponse>(`/forecasting/revenue${buildQuery({ periods })}`),
  askAi: (question: string) => apiPost<AiInsightResponse>("/ai/ask", { question }),
};

export { API_BASE };
