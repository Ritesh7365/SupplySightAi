"use client";

import { useEffect, useRef, useState } from "react";
import { Bell } from "lucide-react";

import { cn } from "@/lib/utils";

const NOTIFICATIONS = [
  {
    id: "1",
    title: "Late delivery risk elevated",
    body: "Standard Class shipments crossed the 55% late-risk threshold.",
    time: "12 min ago",
  },
  {
    id: "2",
    title: "Monthly sales view refreshed",
    body: "analytics.mv_monthly_sales was refreshed successfully.",
    time: "1 hr ago",
  },
  {
    id: "3",
    title: "Inventory placeholder ready",
    body: "Warehouse inventory screens are available for configuration.",
    time: "Yesterday",
  },
] as const;

type NotificationBellProps = {
  className?: string;
};

export function NotificationBell({ className }: NotificationBellProps) {
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
        aria-label="Notifications"
        aria-expanded={open}
        aria-haspopup="menu"
        onClick={() => setOpen((value) => !value)}
        className="relative inline-flex size-10 items-center justify-center rounded-xl border border-border bg-card text-foreground shadow-sm transition-all hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <Bell className="size-4" aria-hidden />
        <span className="absolute right-2 top-2 size-2 rounded-full bg-accent ring-2 ring-card" />
      </button>

      <div
        role="menu"
        aria-hidden={!open}
        className={cn(
          "absolute right-0 top-[calc(100%+0.5rem)] z-50 w-[22rem] origin-top-right rounded-2xl border border-border bg-card p-2 shadow-shell transition-all duration-200 ease-shell",
          open
            ? "pointer-events-auto translate-y-0 scale-100 opacity-100"
            : "pointer-events-none -translate-y-1 scale-95 opacity-0",
        )}
      >
        <div className="flex items-center justify-between px-3 py-2">
          <p className="text-sm font-semibold text-foreground">Notifications</p>
          <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
            {NOTIFICATIONS.length} new
          </span>
        </div>
        <ul className="max-h-80 space-y-1 overflow-y-auto">
          {NOTIFICATIONS.map((item) => (
            <li key={item.id}>
              <button
                type="button"
                role="menuitem"
                className="w-full rounded-xl px-3 py-2.5 text-left transition-colors hover:bg-muted"
              >
                <p className="text-sm font-medium text-foreground">{item.title}</p>
                <p className="mt-0.5 text-xs leading-relaxed text-muted-foreground">{item.body}</p>
                <p className="mt-1.5 text-[11px] text-muted-foreground/80">{item.time}</p>
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
