import type { Metadata } from "next";

import { EmptyCanvas } from "@/components/layout/EmptyCanvas";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "Sales" };

export default function SalesPage() {
  return (
    <section>
      <PageHeader pathname="/sales" />
      <EmptyCanvas
        title="Sales workspace"
        description="Sales analytics views will render here once dashboard widgets are connected."
      />
    </section>
  );
}
