"use client";

import { Menu, X } from "lucide-react";

import { Breadcrumbs } from "@/components/layout/Breadcrumbs";
import { NotificationBell } from "@/components/layout/NotificationBell";
import { SearchBar } from "@/components/layout/SearchBar";
import { ThemeToggle } from "@/components/layout/ThemeToggle";
import { UserMenu } from "@/components/layout/UserMenu";
import { useSidebar } from "@/components/layout/SidebarProvider";
import { cn } from "@/lib/utils";

type NavbarProps = {
  className?: string;
};

export function Navbar({ className }: NavbarProps) {
  const { openMobile, mobileOpen, closeMobile } = useSidebar();

  return (
    <header
      className={cn(
        "sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-navbar/90 px-3 backdrop-blur-md sm:px-4 lg:px-6",
        className,
      )}
    >
      <button
        type="button"
        className="inline-flex size-10 items-center justify-center rounded-xl border border-border bg-card text-foreground shadow-sm transition-colors hover:bg-muted lg:hidden"
        aria-label={mobileOpen ? "Close navigation" : "Open navigation"}
        onClick={() => (mobileOpen ? closeMobile() : openMobile())}
      >
        {mobileOpen ? <X className="size-4" /> : <Menu className="size-4" />}
      </button>

      <div className="hidden min-w-0 md:block md:max-w-[14rem] lg:max-w-[18rem]">
        <Breadcrumbs />
      </div>

      <div className="min-w-0 flex-1 md:mx-auto md:max-w-xl">
        <SearchBar />
      </div>

      <div className="flex items-center gap-2">
        <NotificationBell />
        <ThemeToggle />
        <UserMenu />
      </div>
    </header>
  );
}
