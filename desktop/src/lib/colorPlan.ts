// Presentation logic for colour planning.
//
// Free of JSX so the rule that matters stays testable: the optimistic answer is
// only ever shown when the engine granted it. Telling someone a seven-colour
// project can be swapped when the colours actually share layers costs them a
// whole print.

import type { ColorPlan, ColorUse, ColorVerdict } from "@/api";

export const COLOR_PLAN_TITLE = "Colours and toolheads";

/** A toolhead is the part that melts and lays down one filament. A U1 has four,
 *  so it can print four colours at once without anyone swapping a spool. */
export const TOOLHEAD_EXPLAINER =
  "A toolhead is the part that melts one filament — your U1 has four, so it can print "
  + "four colours at once without you swapping a spool.";

/** The bold line under the headline. Mirrors the engine's verdict exactly. */
export function verdictBanner(verdict: ColorVerdict): string {
  switch (verdict) {
    case "fits":
      return "Every colour has a toolhead";
    case "possible_with_swaps":
      return "Possible without repainting";
    case "needs_reduction":
      return "Needs colour reduction";
    default:
      return "Studio can’t classify this safely";
  }
}

export function verdictTone(verdict: ColorVerdict): "ready" | "risk" | "muted" {
  if (verdict === "fits") return "ready";
  if (verdict === "needs_reduction") return "risk";
  if (verdict === "cannot_classify") return "muted";
  return "ready";
}

/** True only when the engine itself said swaps are on the table. */
export function suggestsSwaps(plan: ColorPlan | null): boolean {
  return plan?.available === true && plan.verdict === "possible_with_swaps";
}

/** Where a swap would happen, in the file's own units. */
export function swapPointText(use: ColorUse): string {
  if (use.from_z_mm === null || use.from_z_mm === undefined) {
    return "at a height the project records";
  }
  const height = `from ${use.from_z_mm.toFixed(1)} mm up`;
  if (use.estimated_layer && use.layer_is_estimated) {
    return `${height} (about layer ${use.estimated_layer})`;
  }
  return height;
}

/** A colour's label for the swatch row. */
export function useLabel(use: ColorUse): string {
  const material = use.material ? ` ${use.material}` : "";
  return `Colour ${use.slot}${material}`;
}

export function groups(plan: ColorPlan | null) {
  return {
    simultaneous: plan?.simultaneous ?? [],
    layerBased: plan?.layer_based ?? [],
    unclassified: plan?.unclassified ?? [],
  };
}
