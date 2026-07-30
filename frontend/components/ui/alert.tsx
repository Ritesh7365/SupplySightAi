import type { ReactNode } from "react";
import { AlertCircle } from "lucide-react";

import { cn } from "@/lib/utils";

export function Alert({
  className,
  title,
  description,
  action,
}: {
  className?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div
      role="alert"
      className={cn(
        "flex gap-3 rounded-2xl border border-destructive/30 bg-destructive/5 p-4 text-foreground",
        className,
      )}
    >
      <AlertCircle className="mt-0.5 size-5 shrink-0 text-destructive" aria-hidden />
      <div className="min-w-0 flex-1">
        <p className="font-semibold">{title}</p>
        {description ? <p className="mt-1 text-sm text-muted-foreground">{description}</p> : null}
        {action ? <div className="mt-3">{action}</div> : null}
      </div>
    </div>
  );
}
