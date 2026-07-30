import type { Metadata } from "next";

import { SalesAnalytics } from "@/components/sales/SalesAnalytics";

export const metadata: Metadata = { title: "Sales" };

export default function SalesPage() {
  return <SalesAnalytics />;
}
