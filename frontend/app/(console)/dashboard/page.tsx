import type { Metadata } from "next";

import { EmptyCanvas } from "@/components/layout/EmptyCanvas";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = {
  title: "Dashboard",
};

export default function DashboardPage() {
  return (
    <section>
      <PageHeader pathname="/dashboard" />
      <EmptyCanvas
        title="Dashboard canvas"
        description="Layout shell is ready. KPI cards and charts will be added in a later milestone."
      />
    </section>
  );
}
