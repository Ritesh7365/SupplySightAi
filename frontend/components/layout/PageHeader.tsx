import type { ReactNode } from "react";

import { getNavItemByPath } from "@/lib/navigation";

type PageHeaderProps = {
  pathname: string;
  children?: ReactNode;
};

/**
 * Lightweight page header for shell routes — title + description only.
 * No KPI cards or charts.
 */
export function PageHeader({ pathname, children }: PageHeaderProps) {
  const item = getNavItemByPath(pathname);

  return (
    <div className="mb-6 flex flex-col gap-3 border-b border-border pb-5 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        <p className="text-sm font-semibold uppercase tracking-[0.16em] text-muted-foreground">
          SupplySight AI
        </p>
        <h1 className="mt-1.5 font-display text-4xl tracking-tight text-foreground sm:text-5xl">
          {item?.title ?? "Workspace"}
        </h1>
        <p className="mt-3 max-w-2xl text-base text-muted-foreground sm:text-lg">
          {item?.description ?? "Enterprise supply chain analytics workspace."}
        </p>
      </div>
      {children}
    </div>
  );
}
