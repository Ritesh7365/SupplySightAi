"use client";

import { Sidebar } from "@/components/layout/Sidebar";
import { useSidebar } from "@/components/layout/SidebarProvider";
import { cn } from "@/lib/utils";

/**
 * Desktop rail + mobile drawer for the application sidebar.
 * Collapse state is shared via SidebarProvider.
 */
export function ResponsiveSidebar() {
  const { collapsed, mobileOpen, closeMobile } = useSidebar();

  return (
    <>
      {/* Desktop / tablet rail */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-40 hidden border-sidebar-border transition-[width] duration-300 ease-shell lg:block",
          collapsed ? "w-sidebar-collapsed" : "w-sidebar",
        )}
      >
        <Sidebar />
      </div>

      {/* Mobile drawer */}
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
            "absolute inset-y-0 left-0 w-[min(100%,18rem)] shadow-shell transition-transform duration-300 ease-shell",
            mobileOpen ? "translate-x-0" : "-translate-x-full",
          )}
        >
          <Sidebar forceExpanded className="animate-slide-in-left" />
        </div>
      </div>
    </>
  );
}
