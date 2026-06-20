import * as React from "react";
import { cn } from "@/lib/utils";

export type Verdict = "READY" | "REPAIRABLE" | "CONVERTIBLE" | "HIGH_RISK";

const VERDICT_STYLES: Record<Verdict, string> = {
  READY: "bg-ready/10 text-ready",
  REPAIRABLE: "bg-repairable/10 text-repairable",
  CONVERTIBLE: "bg-convertible/10 text-convertible",
  HIGH_RISK: "bg-risk/10 text-risk",
};

// Plain-language labels so cards never show raw engine enums to a novice.
// The raw verdict is kept in title/aria-label for power users & debugging.
const VERDICT_LABEL: Record<Verdict, string> = {
  READY: "Print-ready",
  REPAIRABLE: "Fixable",
  CONVERTIBLE: "Needs prep",
  HIGH_RISK: "Needs review",
};

export function Badge({ className, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-muted text-muted-foreground", className)}
      {...props}
    />
  );
}

export function StatusBadge({ verdict, className }: { verdict: Verdict; className?: string }) {
  return (
    <span
      className={cn("inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-semibold", VERDICT_STYLES[verdict], className)}
      title={verdict}
      aria-label={`Status: ${VERDICT_LABEL[verdict]}`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {VERDICT_LABEL[verdict]}
    </span>
  );
}
