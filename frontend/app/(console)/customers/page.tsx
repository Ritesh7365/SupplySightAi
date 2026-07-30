import type { Metadata } from "next";

import { EmptyCanvas } from "@/components/layout/EmptyCanvas";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "Customers" };

export default function CustomersPage() {
  return (
    <section>
      <PageHeader pathname="/customers" />
      <EmptyCanvas
        title="Customers workspace"
        description="Customer performance panels will appear here without changing the shell layout."
      />
    </section>
  );
}
