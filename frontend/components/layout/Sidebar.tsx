"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

import { Logo } from "@/components/layout/Logo";
import { useSidebar } from "@/components/layout/SidebarProvider";
import { mainNav, utilityNav } from "@/lib/navigation";
import { cn } from "@/lib/utils";

type SidebarProps = {
  className?: string;
  /** Force expanded labels (mobile drawer). */
  forceExpanded?: boolean;
};

export function Sidebar({ className, forceExpanded = false }: SidebarProps) {
  const pathname = usePathname();
  const { collapsed, toggleCollapsed, closeMobile } = useSidebar();
  const isCollapsed = forceExpanded ? false : collapsed;

  return (
    <aside
      className={cn(
        "flex h-full flex-col border-r border-sidebar-border bg-sidebar text-sidebar-foreground",
        className,
      )}
    >
      <div
        className={cn(
          "flex h-16 items-center border-b border-sidebar-border px-3",
          isCollapsed ? "justify-center" : "justify-between gap-2",
        )}
      >
        <Logo collapsed={isCollapsed} />
        {!forceExpanded ? (
          <button
            type="button"
            onClick={toggleCollapsed}
            aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            className={cn(
              "inline-flex size-9 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              isCollapsed && "hidden lg:inline-flex",
            )}
          >
            {isCollapsed ? (
              <PanelLeftOpen className="size-4" aria-hidden />
            ) : (
              <PanelLeftClose className="size-4" aria-hidden />
            )}
          </button>
        ) : null}
      </div>

      <nav className="flex flex-1 flex-col gap-6 overflow-y-auto px-3 py-4" aria-label="Primary">
        <NavSection
          label="Analytics"
          items={mainNav}
          pathname={pathname}
          collapsed={isCollapsed}
          onNavigate={closeMobile}
        />
        <NavSection
          label="Workspace"
          items={utilityNav}
          pathname={pathname}
          collapsed={isCollapsed}
          onNavigate={closeMobile}
        />
      </nav>

      <div className="border-t border-sidebar-border p-3">
        <div
          className={cn(
            "rounded-2xl border border-sidebar-border bg-card/70 p-3 shadow-sm transition-all",
            isCollapsed && "px-2",
          )}
        >
          {isCollapsed ? (
            <p className="text-center text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              AI
            </p>
          ) : (
            <>
              <p className="text-xs font-semibold text-foreground">Enterprise workspace</p>
              <p className="mt-1 text-[11px] leading-relaxed text-muted-foreground">
                Analytics shell ready for dashboards and insights.
              </p>
            </>
          )}
        </div>
      </div>
    </aside>
  );
}

function NavSection({
  label,
  items,
  pathname,
  collapsed,
  onNavigate,
}: {
  label: string;
  items: typeof mainNav;
  pathname: string;
  collapsed: boolean;
  onNavigate: () => void;
}) {
  return (
    <div>
      <p
        className={cn(
          "mb-2 px-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground transition-all",
          collapsed && "text-center tracking-normal",
        )}
      >
        {collapsed ? "•" : label}
      </p>
      <ul className="space-y-1">
        {items.map((item) => {
          const active =
            pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                title={collapsed ? item.title : undefined}
                onClick={onNavigate}
                className={cn(
                  "group relative flex items-center gap-3 rounded-xl px-2.5 py-2 text-sm font-medium transition-all duration-200 ease-shell",
                  active
                    ? "bg-sidebar-accent text-sidebar-accent-foreground shadow-sm"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                  collapsed && "justify-center px-0",
                )}
              >
                <span
                  className={cn(
                    "absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-primary transition-opacity",
                    active ? "opacity-100" : "opacity-0",
                    collapsed && "hidden",
                  )}
                />
                <Icon
                  className={cn(
                    "size-4 shrink-0 transition-transform duration-200 group-hover:scale-105",
                    active && "text-primary",
                  )}
                  aria-hidden
                />
                <span
                  className={cn(
                    "truncate transition-all duration-300 ease-shell",
                    collapsed ? "w-0 overflow-hidden opacity-0" : "w-auto opacity-100",
                  )}
                >
                  {item.title}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
