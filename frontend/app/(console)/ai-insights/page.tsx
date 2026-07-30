import type { Metadata } from "next";

import { EmptyCanvas } from "@/components/layout/EmptyCanvas";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "AI Insights" };

export default function AiInsightsPage() {
  return (
    <section>
      <PageHeader pathname="/ai-insights" />
      <EmptyCanvas
        title="AI Insights workspace"
        description="Recommendation and model insight panels will appear here later."
      />
    </section>
  );
}
