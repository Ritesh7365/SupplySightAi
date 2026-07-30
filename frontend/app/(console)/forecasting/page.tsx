import type { Metadata } from "next";

import { ForecastingAnalytics } from "@/components/forecasting/ForecastingAnalytics";

export const metadata: Metadata = { title: "Forecasting" };

export default function ForecastingPage() {
  return <ForecastingAnalytics />;
}
