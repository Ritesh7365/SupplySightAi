import type { Metadata } from "next";

import { EmptyCanvas } from "@/components/layout/EmptyCanvas";
import { PageHeader } from "@/components/layout/PageHeader";

export const metadata: Metadata = { title: "Settings" };

export default function SettingsPage() {
  return (
    <section>
      <PageHeader pathname="/settings" />
      <EmptyCanvas
        title="Settings workspace"
        description="Workspace preferences and account controls will live in this shell."
      />
    </section>
  );
}
