"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown, LogOut, Settings, UserRound } from "lucide-react";

import { cn } from "@/lib/utils";

type UserMenuProps = {
  className?: string;
};

export function UserMenu({ className }: UserMenuProps) {
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onPointerDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, []);

  return (
    <div ref={rootRef} className={cn("relative", className)}>
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
        className="inline-flex h-10 items-center gap-2 rounded-xl border border-border bg-card pl-1.5 pr-2.5 shadow-sm transition-all hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <span className="flex size-7 items-center justify-center rounded-lg bg-primary/10 text-xs font-semibold text-primary">
          SA
        </span>
        <span className="hidden min-w-0 text-left md:block">
          <span className="block truncate text-sm font-medium leading-tight text-foreground">
            Supply Admin
          </span>
          <span className="block truncate text-[11px] leading-tight text-muted-foreground">
            Operations
          </span>
        </span>
        <ChevronDown
          className={cn(
            "size-3.5 text-muted-foreground transition-transform duration-200",
            open && "rotate-180",
          )}
          aria-hidden
        />
      </button>

      <div
        role="menu"
        aria-hidden={!open}
        className={cn(
          "absolute right-0 top-[calc(100%+0.5rem)] z-50 w-56 origin-top-right rounded-2xl border border-border bg-card p-1.5 shadow-shell transition-all duration-200 ease-shell",
          open
            ? "pointer-events-auto translate-y-0 scale-100 opacity-100"
            : "pointer-events-none -translate-y-1 scale-95 opacity-0",
        )}
      >
        <div className="px-3 py-2">
          <p className="text-sm font-medium text-foreground">Supply Admin</p>
          <p className="text-xs text-muted-foreground">admin@supplysight.ai</p>
        </div>
        <div className="my-1 h-px bg-border" />
        <MenuItem icon={UserRound} label="Profile" />
        <MenuItem icon={Settings} label="Preferences" />
        <div className="my-1 h-px bg-border" />
        <MenuItem icon={LogOut} label="Sign out" tone="danger" />
      </div>
    </div>
  );
}

function MenuItem({
  icon: Icon,
  label,
  tone = "default",
}: {
  icon: typeof UserRound;
  label: string;
  tone?: "default" | "danger";
}) {
  return (
    <button
      type="button"
      role="menuitem"
      className={cn(
        "flex w-full items-center gap-2 rounded-xl px-3 py-2 text-sm transition-colors",
        tone === "danger"
          ? "text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/40"
          : "text-foreground hover:bg-muted",
      )}
    >
      <Icon className="size-4 opacity-80" aria-hidden />
      {label}
    </button>
  );
}
