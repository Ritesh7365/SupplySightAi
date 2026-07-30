"use client";

import { Search } from "lucide-react";

import { cn } from "@/lib/utils";

type SearchBarProps = {
  className?: string;
};

export function SearchBar({ className }: SearchBarProps) {
  return (
    <label
      className={cn(
        "group relative flex min-w-0 flex-1 items-center",
        className,
      )}
    >
      <span className="sr-only">Search workspace</span>
      <Search
        className="pointer-events-none absolute left-3 size-4 text-muted-foreground transition-colors group-focus-within:text-primary"
        aria-hidden
      />
      <input
        type="search"
        placeholder="Search orders, customers, products…"
        className="h-10 w-full rounded-xl border border-border bg-background/80 pl-10 pr-16 text-sm text-foreground shadow-sm outline-none transition-all placeholder:text-muted-foreground focus:border-primary/40 focus:ring-2 focus:ring-ring/30"
      />
      <kbd className="pointer-events-none absolute right-2.5 hidden rounded-md border border-border bg-muted px-1.5 py-0.5 font-mono text-[10px] font-medium text-muted-foreground sm:inline-block">
        ⌘K
      </kbd>
    </label>
  );
}
