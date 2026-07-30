"use client";

import { Sidebar } from "@/components/layout/Sidebar";
import { useSidebar } from "@/components/layout/SidebarProvider";
import { cn } from "@/lib/utils";

/**
 * Desktop rail + mobile drawer for the application sidebar.
 * Full viewport height (top → bottom) with continuous background.
 */
export function ResponsiveSidebar() {
  const { collapsed, mobileOpen, closeMobile } = useSidebar();

  return (
    <>
      {/* Desktop / tablet rail — full viewport height */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-40 hidden h-svh max-h-svh border-r border-sidebar-border bg-sidebar transition-[width] duration-300 ease-shell lg:flex lg:flex-col",
          collapsed ? "w-sidebar-collapsed" : "w-sidebar",
        )}
      >
        <Sidebar className="h-full min-h-0" />
      </div>

      {/* Mobile drawer — full viewport height */}
      <div
        className={cn(
          "fixed inset-0 z-50 lg:hidden",
          mobileOpen ? "pointer-events-auto" : "pointer-events-none",
        )}
      >
        <button
          type="button"
          aria-label="Close sidebar overlay"
          className={cn(
            "absolute inset-0 bg-slate-950/40 backdrop-blur-[2px] transition-opacity duration-300",
            mobileOpen ? "opacity-100" : "opacity-0",
          )}
          onClick={closeMobile}
        />
        <div
          className={cn(
            "absolute inset-y-0 left-0 flex h-svh max-h-svh w-[min(100%,18rem)] flex-col border-r border-sidebar-border bg-sidebar shadow-shell transition-transform duration-300 ease-shell",
            mobileOpen ? "translate-x-0" : "-translate-x-full",
          )}
        >
          <Sidebar forceExpanded className="h-full min-h-0 animate-slide-in-left" />
        </div>
      </div>
    </>
  );
}
