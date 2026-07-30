"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";

import { getNavItemByPath } from "@/lib/navigation";
import { cn } from "@/lib/utils";

type BreadcrumbsProps = {
  className?: string;
};

export function Breadcrumbs({ className }: BreadcrumbsProps) {
  const pathname = usePathname();
  const current = getNavItemByPath(pathname);

  return (
    <nav aria-label="Breadcrumb" className={cn("min-w-0", className)}>
      <ol className="flex items-center gap-1.5 text-sm text-muted-foreground">
        <li className="flex items-center gap-1.5">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 transition-colors hover:bg-muted hover:text-foreground"
          >
            <Home className="size-3.5" aria-hidden />
            <span className="sr-only sm:not-sr-only">Workspace</span>
          </Link>
        </li>
        {current ? (
          <>
            <li aria-hidden>
              <ChevronRight className="size-3.5 opacity-60" />
            </li>
            <li className="truncate font-medium text-foreground" aria-current="page">
              {current.title}
            </li>
          </>
        ) : null}
      </ol>
    </nav>
  );
}
