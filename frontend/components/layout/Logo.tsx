import Link from "next/link";

import { BrandIcon } from "@/lib/navigation";
import { cn } from "@/lib/utils";

type LogoProps = {
  collapsed?: boolean;
  className?: string;
};

export function Logo({ collapsed = false, className }: LogoProps) {
  return (
    <Link
      href="/dashboard"
      className={cn(
        "group flex items-center gap-3 rounded-xl px-2 py-1.5 outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring",
        className,
      )}
      aria-label="SupplySight AI home"
    >
      <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm transition-transform duration-300 ease-shell group-hover:scale-[1.03]">
        <BrandIcon className="size-5" aria-hidden />
      </span>
      <span
        className={cn(
          "min-w-0 overflow-hidden transition-all duration-300 ease-shell",
          collapsed ? "w-0 opacity-0" : "w-auto opacity-100",
        )}
      >
        <span className="block truncate font-display text-xl leading-none tracking-tight text-foreground sm:text-2xl">
          SupplySight AI
        </span>
        <span className="mt-1.5 block truncate text-xs font-medium uppercase tracking-[0.14em] text-muted-foreground">
          Supply chain analytics
        </span>
      </span>
    </Link>
  );
}
