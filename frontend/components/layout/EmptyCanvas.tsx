type EmptyCanvasProps = {
  title: string;
  description: string;
};

/** Neutral content placeholder for shell routes (no charts or KPI cards). */
export function EmptyCanvas({ title, description }: EmptyCanvasProps) {
  return (
    <div className="flex min-h-[18rem] items-center justify-center rounded-2xl border border-dashed border-border bg-muted/40 px-6 text-center">
      <div>
        <p className="text-sm font-medium text-foreground">{title}</p>
        <p className="mt-1 max-w-md text-sm text-muted-foreground">{description}</p>
      </div>
    </div>
  );
}
