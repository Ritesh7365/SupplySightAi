"use client";

import type { ReactNode } from "react";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { Navbar } from "@/components/layout/Navbar";
import { ResponsiveSidebar } from "@/components/layout/ResponsiveSidebar";
import { SidebarProvider, useSidebar } from "@/components/layout/SidebarProvider";
import { cn } from "@/lib/utils";

type AppShellProps = {
  children: ReactNode;
};

export function AppShell({ children }: AppShellProps) {
  return (
    <SidebarProvider>
      <AppShellFrame>{children}</AppShellFrame>
    </SidebarProvider>
  );
}

function AppShellFrame({ children }: { children: ReactNode }) {
  const { collapsed } = useSidebar();

  return (
    <div className="min-h-screen bg-background">
      <ResponsiveSidebar />
      <div
        className={cn(
          "flex min-h-screen flex-col transition-[padding] duration-300 ease-shell",
          collapsed ? "lg:pl-sidebar-collapsed" : "lg:pl-sidebar",
        )}
      >
        <Navbar />
        <main className="flex-1 p-3 sm:p-4 lg:p-6">
          <div className="mb-3 md:hidden">
            <Breadcrumbs />
          </div>
          <div className="mx-auto min-h-[calc(100vh-7rem)] rounded-2xl border border-border bg-card p-4 shadow-shell sm:p-6 animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
