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

// --- painted colour ---------------------------------------------------------
//
// A beginner should get one sentence: how many colours are painted on, and what
// that means for the print. An expert should be able to open a panel and see
// every number it came from — which slots, how many facets, how much area, at
// what heights, and out of which part of the file. Neither audience should be
// told painting "cannot be read": Studio reads it.

/** The one-line version. Null when the project has no painting. */
export function paintedHeadline(plan: ColorPlan | null): string | null {
  const painted = plan?.painted;
  if (!painted?.painted || !painted.headline) return null;
  return painted.headline;
}

/** What painting a single colour is measured to cover. Empty when the colour is
 *  not painted on, so a caller can render nothing rather than "0 mm²". */
export function paintedMeasurement(use: ColorUse): string {
  if (!use.painted) return "";
  const parts: string[] = [];
  if (use.painted_facets) {
    parts.push(`${use.painted_facets.toLocaleString()} painted facet${use.painted_facets === 1 ? "" : "s"}`);
  }
  if (use.painted_area_mm2) parts.push(`${formatArea(use.painted_area_mm2)} of surface`);
  const span = paintedHeightRange(use);
  if (span) parts.push(span);
  return parts.join(" · ");
}

/** The height band a painted colour occupies, in the file's own millimetres. */
export function paintedHeightRange(use: ColorUse): string {
  const low = use.painted_z_min_mm;
  const high = use.painted_z_max_mm;
  if (low === null || low === undefined || high === null || high === undefined) return "";
  if (Math.abs(high - low) < 0.005) return `at ${low.toFixed(1)} mm`;
  return `${low.toFixed(1)}–${high.toFixed(1)} mm`;
}

function formatArea(mm2: number): string {
  if (mm2 >= 100) return `${(mm2 / 100).toFixed(1)} cm²`;
  return `${mm2.toFixed(1)} mm²`;
}

/** The line that says what could not be settled without slicing — shown only
 *  when the project actually has painting, because otherwise it is noise. */
export function paintedLimit(plan: ColorPlan | null): string | null {
  const painted = plan?.painted;
  if (!painted?.painted) return null;
  const pairs = painted.coexistence?.pairs ?? [];
  const overlapping = pairs.filter((p) => p.verdict === "overlaps").length;
  if (overlapping === 0) return null;
  return "Colours whose painted heights overlap can meet on a layer. Whether a "
    + "printed layer really carries both is decided when Orca slices it.";
}

/** Rows for the expert panel: every measured fact, in the order they were read. */
export function paintedDisclosure(plan: ColorPlan | null): { label: string; value: string }[] {
  const painted = plan?.painted;
  if (!painted?.painted) return [];
  const rows: { label: string; value: string }[] = [];
  rows.push({
    label: "Read from",
    value: painted.dialect === "prusa"
      ? "the project's slic3rpe:mmu_segmentation facet data"
      : "the project's paint_color facet data",
  });
  rows.push({
    label: "Painting format version",
    value: painted.format_version_known
      ? String(painted.format_version)
      : "not declared by this project",
  });
  rows.push({ label: "Painted facets", value: (painted.painted_facets ?? 0).toLocaleString() });
  rows.push({ label: "Slots painted with", value: (painted.slots ?? []).join(", ") || "none" });
  if (painted.unlisted_slots?.length) {
    rows.push({
      label: "Painted with slots the project never lists",
      value: painted.unlisted_slots.join(", "),
    });
  }
  if (painted.facets_outside_mesh) {
    rows.push({
      label: "Painted facets pointing outside their mesh",
      value: `${painted.facets_outside_mesh.toLocaleString()} — their slot is known, their place is not`,
    });
  }
  if (painted.malformed_facets) {
    rows.push({
      label: "Facets whose paint could not be decoded",
      value: painted.malformed_facets.toLocaleString(),
    });
  }
  if (painted.truncated) {
    rows.push({
      label: "Coverage",
      value: "this project's painting is larger than Studio decodes in full, so these figures are a floor",
    });
  }
  for (const object of painted.objects ?? []) {
    const name = object.name || object.object_id || "mesh";
    rows.push({
      label: `Mesh ${name}`,
      value: `${object.painted_triangle_count.toLocaleString()} of ${object.triangle_count.toLocaleString()} facets painted`
        + (object.transform_known ? "" : " · heights are the mesh's own, not placed on the plate"),
    });
    rows.push({
      label: `Mesh ${name} — unpainted area`,
      value: object.default_slot === null
        ? object.default_slot_source
        : `prints in slot ${object.default_slot} — ${object.default_slot_source}`,
    });
  }
  return rows;
}
