"use client";

import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

export type FilterOption = { label: string; value: string };

type AnalyticsFilterBarProps = {
  year?: string;
  region?: string;
  market?: string;
  years: FilterOption[];
  regions: FilterOption[];
  markets?: FilterOption[];
  onYearChange: (value: string) => void;
  onRegionChange: (value: string) => void;
  onMarketChange?: (value: string) => void;
  onExportCsv?: () => void;
  onExportExcel?: () => void;
  onExportPdf?: () => void;
  className?: string;
};

function SelectField({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: FilterOption[];
  onChange: (v: string) => void;
}) {
  return (
    <label className="flex min-w-[9rem] flex-1 flex-col gap-1.5 text-xs font-medium text-muted-foreground">
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-10 rounded-xl border border-border bg-background px-3 text-sm text-foreground outline-none ring-offset-background focus:ring-2 focus:ring-ring"
      >
        {options.map((o) => (
          <option key={o.value || o.label} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}

export function AnalyticsFilterBar({
  year = "",
  region = "",
  market = "",
  years,
  regions,
  markets,
  onYearChange,
  onRegionChange,
  onMarketChange,
  onExportCsv,
  onExportExcel,
  onExportPdf,
  className,
}: AnalyticsFilterBarProps) {
  return (
    <Card className={cn(className)}>
      <CardContent className="flex flex-col gap-4 p-4 lg:flex-row lg:items-end lg:justify-between">
        <div className="flex flex-1 flex-wrap gap-3">
          <SelectField label="Year" value={year} options={years} onChange={onYearChange} />
          <SelectField label="Region" value={region} options={regions} onChange={onRegionChange} />
          {markets && onMarketChange ? (
            <SelectField
              label="Market"
              value={market}
              options={markets}
              onChange={onMarketChange}
            />
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2">
          {onExportCsv ? (
            <Button variant="outline" size="sm" onClick={onExportCsv}>
              <Download className="mr-1.5 size-3.5" />
              CSV
            </Button>
          ) : null}
          {onExportExcel ? (
            <Button variant="outline" size="sm" onClick={onExportExcel}>
              <Download className="mr-1.5 size-3.5" />
              Excel
            </Button>
          ) : null}
          {onExportPdf ? (
            <Button variant="outline" size="sm" onClick={onExportPdf}>
              <Download className="mr-1.5 size-3.5" />
              PDF
            </Button>
          ) : null}
        </div>
      </CardContent>
    </Card>
  );
}
