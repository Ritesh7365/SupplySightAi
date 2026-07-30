import type { Metadata } from "next";

import { EmptyCanvas } from "@/components/layout/EmptyCanvas";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "Shipping" };

export default function ShippingPage() {
  return (
    <section>
      <PageHeader pathname="/shipping" />
      <EmptyCanvas
        title="Shipping workspace"
        description="Delivery performance modules will use this shell section."
      />
    </section>
  );
}
