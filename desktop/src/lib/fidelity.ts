// Presentation logic for the fidelity report.
//
// Free of JSX so the one rule that matters stays testable: Studio may only say
// "nothing was lost" when the audit proved it for that project. Everything else
// here is grouping and wording.

import type { FidelityReport, FidelityRow, FidelityStatus } from "@/api";

export const FIDELITY_TITLE = "What survived preparing this copy";

/** The three questions the report answers, in the order a user asks them. */
export const FIDELITY_HEADINGS = {
  kept: "What stayed the same",
  changed: "What Studio changed",
  notCarried: "What Studio could not carry over",
  unverified: "What Studio could not check",
} as const;

export function statusLabel(status: FidelityStatus): string {
  switch (status) {
    case "preserved_exact":
      return "Identical";
    case "preserved_semantic":
      return "Same meaning";
    case "changed":
      return "Changed";
    case "added":
      return "Added";
    case "removed":
      return "Not carried over";
    case "unsupported":
      return "Not checked — Studio can’t read it";
    default:
      return "Couldn’t check";
  }
}

export function statusTone(status: FidelityStatus): "ready" | "risk" | "muted" {
  if (status === "preserved_exact" || status === "preserved_semantic") return "ready";
  if (status === "unverified" || status === "unsupported") return "risk";
  return "muted";
}

/**
 * The headline sentence.
 *
 * The strong claim is only available when the audit's own `claims` block grants
 * it. Anything short of that gets a sentence that names what is outstanding.
 */
export function fidelityHeadline(report: FidelityReport | null): string {
  if (!report) return "Checking what survived…";
  if (!report.available) return report.summary;
  if (report.claims.may_claim_nothing_lost) {
    return "Everything Studio can identify came through, and every change is listed below.";
  }
  if (report.unverified.length) {
    const n = report.unverified.length;
    return `${n} thing${n === 1 ? "" : "s"} in this file changed in a way Studio cannot explain. Open the prepared copy in Snapmaker Orca and compare it with your original before printing — and please report it, because Studio should be able to account for everything it changed.`;
  }
  return "Every change and everything not carried over is listed below, with the reason.";
}

/** True only when the engine granted the strongest claim. Never inferred. */
export function mayClaimNothingLost(report: FidelityReport | null): boolean {
  return Boolean(report?.available && report.claims.may_claim_nothing_lost);
}

export function groupedRows(report: FidelityReport | null): {
  kept: FidelityRow[];
  changed: FidelityRow[];
  notCarried: FidelityRow[];
  unverified: FidelityRow[];
} {
  return {
    kept: report?.kept ?? [],
    changed: report?.changed ?? [],
    notCarried: report?.not_carried ?? [],
    unverified: report?.unverified ?? [],
  };
}

/** A compact "12 kept · 3 changed · 1 not carried over" line. */
export function countsLine(report: FidelityReport | null): string {
  if (!report?.available) return "";
  const g = groupedRows(report);
  const bits: string[] = [`${g.kept.length} kept`];
  if (g.changed.length) bits.push(`${g.changed.length} changed`);
  if (g.notCarried.length) bits.push(`${g.notCarried.length} not carried over`);
  if (g.unverified.length) bits.push(`${g.unverified.length} unchecked`);
  return bits.join(" · ");
}

/**
 * One plain sentence about the settings somebody set on individual objects.
 *
 * A project where one part prints at 0.3 mm layers and another at 0.2 is making
 * a decision, and a copy that silently flattens it prints a different thing.
 * Two of the three settings Studio can carry are spelled differently in
 * Snapmaker Orca, so "preserved" here means the setting arrived, not that the
 * word did.
 *
 * Returns null when the project has none, so the card says nothing rather than
 * saying "0 settings".
 */
export function objectSettingsLine(report: FidelityReport | null): string | null {
  if (!report?.available) return null;
  const rows = [...(report.kept ?? []), ...(report.changed ?? []),
                ...(report.not_carried ?? []), ...(report.unverified ?? [])]
    .filter((row) => row.element.startsWith("Settings set on"));
  if (!rows.length) return null;

  const kept = rows.filter(
    (row) => row.status === "preserved_exact" || row.status === "preserved_semantic").length;
  const missed = rows.length - kept;
  const count = (n: number) => `${n} object-specific setting${n === 1 ? "" : "s"}`;
  if (missed === 0) return `${count(kept)} preserved.`;
  const was = missed === 1 ? "was" : "were";
  if (kept === 0) return `${count(missed)} ${was} not carried — the list below says why.`;
  return `${count(kept)} preserved; ${missed} not carried — the list below says why.`;
}
