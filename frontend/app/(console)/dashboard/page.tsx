import type { Metadata } from "next";

import { ExecutiveDashboard } from "@/components/dashboard/ExecutiveDashboard";

export const metadata: Metadata = {
  title: "Dashboard",
};

export default function DashboardPage() {
  return <ExecutiveDashboard />;
}
