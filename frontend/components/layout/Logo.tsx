import Link from "next/link";

import { BrandIcon } from "@/lib/navigation";
import { cn } from "@/lib/utils";

type LogoProps = {
  collapsed?: boolean;
  className?: string;
};

/**
 * Brand lockup:
 * Row 1 — icon + "SupplySight AI" (same baseline)
 * Row 2 — "SUPPLY CHAIN ANALYTICS" below, left-aligned
 */
export function Logo({ collapsed = false, className }: LogoProps) {
  return (
    <Link
      href="/dashboard"
      className={cn(
        "group flex min-w-0 flex-col rounded-xl px-1 py-0.5 outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring",
        collapsed ? "items-center gap-0" : "gap-2",
        className,
      )}
      aria-label="SupplySight AI home"
    >
      <span className="flex min-w-0 items-center gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm transition-transform duration-300 ease-shell group-hover:scale-[1.03]">
          <BrandIcon className="size-5" aria-hidden />
        </span>
        <span
          className={cn(
            "min-w-0 truncate font-display text-xl leading-none tracking-tight text-foreground transition-all duration-300 ease-shell sm:text-2xl",
            collapsed ? "w-0 opacity-0" : "opacity-100",
          )}
        >
          SupplySight AI
        </span>
      </span>

      <span
        className={cn(
          "block truncate text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground transition-all duration-300 ease-shell",
          collapsed ? "h-0 overflow-hidden opacity-0" : "opacity-100",
        )}
      >
        Supply chain analytics
      </span>
    </Link>
  );
}
