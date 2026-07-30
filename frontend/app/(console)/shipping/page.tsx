import type { Metadata } from "next";

import { ShippingAnalytics } from "@/components/shipping/ShippingAnalytics";

export const metadata: Metadata = { title: "Shipping" };

export default function ShippingPage() {
  return <ShippingAnalytics />;
}
