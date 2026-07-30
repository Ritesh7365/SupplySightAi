import type { Metadata } from "next";

import { EmptyCanvas } from "@/components/layout/EmptyCanvas";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "Forecasting" };

export default function ForecastingPage() {
  return (
    <section>
      <PageHeader pathname="/forecasting" />
      <EmptyCanvas
        title="Forecasting workspace"
        description="Demand forecast visualizations will mount in this content area."
      />
    </section>
  );
}
