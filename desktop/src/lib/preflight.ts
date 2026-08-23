// Presentation logic for the project ↔ printer preflight.
//
// Free of JSX so the two rules that make this trustworthy stay testable: an
// unknown never reads as a pass or a failure, and the headline never promises
// a successful print.

import type { Preflight, PreflightCheck, PreflightResult } from "@/api";

export const PREFLIGHT_TITLE = "Before you slice";

export const PREFLIGHT_SUBTITLE =
  "How this project compares to the printer Studio can see right now.";

/** Beginner-facing label for a result. Deliberately not "fail" or "pass". */
export function resultLabel(result: PreflightResult): string {
  switch (result) {
    case "ok":
      return "Looks right";
    case "attention":
      return "Needs attention";
    case "blocked":
      return "Can't work as-is";
    default:
      return "Studio can't tell";
  }
}

/** Tailwind-ish token name for the result colour, resolved by the component. */
export function resultTone(result: PreflightResult): "ready" | "risk" | "muted" {
  if (result === "ok") return "ready";
  if (result === "unknown") return "muted";
  return "risk";
}

/**
 * The headline.
 *
 * An unknown is counted separately from a problem, because "Studio can't check
 * this for you" is a different instruction from "this is wrong" — and collapsing
 * them is exactly how a tool starts lying.
 */
export function preflightHeadline(pre: Preflight | null): string {
  if (!pre) return "Comparing this project to your printer…";
  return pre.summary;
}

/** Checks worth showing first: problems, then the things only a human can settle. */
export function orderedChecks(pre: Preflight | null): PreflightCheck[] {
  return pre?.checks ?? [];
}

export function attentionCount(pre: Preflight | null): number {
  if (!pre) return 0;
  return (pre.counts.attention ?? 0) + (pre.counts.blocked ?? 0);
}

export function unknownCount(pre: Preflight | null): number {
  return pre?.counts.unknown ?? 0;
}

/** True when the whole panel is really just "connect a printer". */
export function isPrinterMissing(pre: Preflight | null): boolean {
  return Boolean(pre && !pre.printer_reachable);
}
