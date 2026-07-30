import type { Metadata } from "next";

import { EmptyCanvas } from "@/components/layout/EmptyCanvas";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "Inventory" };

export default function InventoryPage() {
  return (
    <section>
      <PageHeader pathname="/inventory" />
      <EmptyCanvas
        title="Inventory workspace"
        description="Warehouse and stock views will plug into this layout canvas."
      />
    </section>
  );
}
