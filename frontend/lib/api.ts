import type {
  ExecutiveDashboard,
  GeographicPoint,
  InventoryAlertsResponse,
  ListResponse,
  MonthlySalesPoint,
  RecentOrder,
  TopProductPoint,
} from "@/types/api";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
  "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path.startsWith("/") ? path : `/${path}`}`;
  const response = await fetch(url, {
    ...init,
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
}

export const api = {
  getExecutive: () => apiGet<ExecutiveDashboard>("/dashboard/executive"),
  getMonthlySales: (year?: number) =>
    apiGet<ListResponse<MonthlySalesPoint>>(
      year != null ? `/charts/monthly-sales?year=${year}` : "/charts/monthly-sales",
    ),
  getTopProducts: (limit = 10) =>
    apiGet<ListResponse<TopProductPoint>>(`/charts/top-products?limit=${limit}`),
  getGeography: (limit = 500) =>
    apiGet<ListResponse<GeographicPoint>>(`/dashboard/geography?limit=${limit}`),
  getRecentOrders: (limit = 10) =>
    apiGet<ListResponse<RecentOrder>>(`/dashboard/recent-orders?limit=${limit}`),
  getInventoryAlerts: (limit = 20) =>
    apiGet<InventoryAlertsResponse>(`/dashboard/inventory-alerts?limit=${limit}`),
};

export { API_BASE };
