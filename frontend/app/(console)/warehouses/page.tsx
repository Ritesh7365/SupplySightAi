import type { Metadata } from "next";

import { WarehousesAnalytics } from "@/components/warehouses/WarehousesAnalytics";

export const metadata: Metadata = { title: "Warehouses" };

export default function WarehousesPage() {
  return <WarehousesAnalytics />;
}
