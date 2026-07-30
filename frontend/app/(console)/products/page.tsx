import type { Metadata } from "next";

import { EmptyCanvas } from "@/components/layout/EmptyCanvas";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "Products" };

export default function ProductsPage() {
  return (
    <section>
      <PageHeader pathname="/products" />
      <EmptyCanvas
        title="Products workspace"
        description="Product and category analytics will mount in this content region."
      />
    </section>
  );
}
