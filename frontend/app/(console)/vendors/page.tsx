import type { Metadata } from "next";

import { VendorsAnalytics } from "@/components/vendors/VendorsAnalytics";

export const metadata: Metadata = { title: "Vendors" };

export default function VendorsPage() {
  return <VendorsAnalytics />;
}
