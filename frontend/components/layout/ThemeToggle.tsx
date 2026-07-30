"use client";

import { Moon, Sun } from "lucide-react";

import { useTheme } from "@/components/layout/ThemeProvider";
import { cn } from "@/lib/utils";

type ThemeToggleProps = {
  className?: string;
};

export function ThemeToggle({ className }: ThemeToggleProps) {
  const { theme, toggleTheme, ready } = useTheme();
  const isDark = theme === "dark";

  return (
    <button
      type="button"
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      disabled={!ready}
      onClick={toggleTheme}
      className={cn(
        "relative inline-flex size-10 items-center justify-center rounded-xl border border-border bg-card text-foreground shadow-sm transition-all hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:opacity-60",
        className,
      )}
    >
      <Sun
        className={cn(
          "absolute size-4 transition-all duration-300 ease-shell",
          isDark ? "rotate-90 scale-0 opacity-0" : "rotate-0 scale-100 opacity-100",
        )}
        aria-hidden
      />
      <Moon
        className={cn(
          "size-4 transition-all duration-300 ease-shell",
          isDark ? "rotate-0 scale-100 opacity-100" : "-rotate-90 scale-0 opacity-0",
        )}
        aria-hidden
      />
    </button>
  );
}
