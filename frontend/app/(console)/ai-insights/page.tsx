import type { Metadata } from "next";

import { AiInsightsPanel } from "@/components/ai/AiInsightsPanel";

export const metadata: Metadata = { title: "AI Insights" };

export default function AiInsightsPage() {
  return <AiInsightsPanel />;
}
