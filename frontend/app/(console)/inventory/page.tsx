import type { Metadata } from "next";

import { InventoryAnalytics } from "@/components/inventory/InventoryAnalytics";

export const metadata: Metadata = { title: "Inventory" };

export default function InventoryPage() {
  return <InventoryAnalytics />;
}
