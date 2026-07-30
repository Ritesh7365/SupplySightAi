import type { Metadata } from "next";

import { ProductsAnalytics } from "@/components/products/ProductsAnalytics";

export const metadata: Metadata = { title: "Products" };

export default function ProductsPage() {
  return <ProductsAnalytics />;
}
