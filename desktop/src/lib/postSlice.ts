// Presentation logic for the Post-Slice Doctor.
//
// Free of JSX so the rules that make it trustworthy stay testable: a job Studio
// could not read never reads as a job that is fine, an unknown never reads as a
// pass, and the filament total is never split into model/purge when the slicer
// did not separate them.

import type { PostSlice, PreflightCheck, PreflightResult, SlicedCost, SlicedJob } from "@/api";

export const POST_SLICE_TITLE = "What the printer will actually do";

export const POST_SLICE_SUBTITLE =
  "Read from the sliced file itself, and compared against your printer right now.";

export const POST_SLICE_EXPLAINER =
  "Everything else in Studio checks your project. This checks the G-code your slicer " +
  "produced — the file the printer really executes. Studio does not slice; Snapmaker " +
  "Orca does.";

/** The headline. Never invents reassurance the report did not give. */
export function postSliceHeadline(report: PostSlice | null): string {
  if (!report) return "Reading the sliced file…";
  return report.summary;
}

export function isUnreadable(report: PostSlice | null): boolean {
  return Boolean(report && !report.available);
}

export function problemCount(report: PostSlice | null): number {
  if (!report) return 0;
  return (report.counts?.attention ?? 0) + (report.counts?.blocked ?? 0);
}

export function unknownCount(report: PostSlice | null): number {
  return report?.counts?.unknown ?? 0;
}

export function orderedChecks(report: PostSlice | null): PreflightCheck[] {
  return report?.checks ?? [];
}

/** Human duration from seconds. Returns null rather than "0m" for missing data. */
export function humanDuration(seconds: number | null | undefined): string | null {
  if (!seconds || seconds <= 0) return null;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.round((seconds % 3600) / 60);
  if (hours && minutes) return `${hours} h ${minutes} min`;
  if (hours) return `${hours} h`;
  return `${minutes} min`;
}

export function humanSize(bytes: number | null | undefined): string | null {
  if (!bytes || bytes <= 0) return null;
  const mb = bytes / (1024 * 1024);
  if (mb >= 1) return `${mb.toFixed(mb >= 10 ? 0 : 1)} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

/** "slot 1, slot 3" — 1-based, because the user's spools are labelled that way. */
export function slotList(tools: number[] | null | undefined): string | null {
  if (!tools || !tools.length) return null;
  return tools.map((t) => `slot ${t + 1}`).join(", ");
}

/** The facts worth putting at the top of the card, each one straight from the file. */
export function jobFacts(job: SlicedJob | undefined): Array<{ label: string; value: string }> {
  if (!job) return [];
  const rows: Array<{ label: string; value: string }> = [];
  if (job.slicer) {
    rows.push({ label: "Sliced by", value: [job.slicer, job.slicer_version].filter(Boolean).join(" ") });
  }
  if (job.printer_model) rows.push({ label: "For", value: job.printer_model });
  const slots = slotList(job.tools_used);
  if (slots) rows.push({ label: "Prints from", value: slots });
  if (job.layer_count) {
    const height = job.layer_height_mm ? ` at ${job.layer_height_mm} mm` : "";
    rows.push({ label: "Layers", value: `${job.layer_count}${height}` });
  }
  const time = humanDuration(job.estimated_seconds);
  if (time) rows.push({ label: "Estimated time", value: time });
  if (job.total_g != null) rows.push({ label: "Filament", value: `${job.total_g} g` });
  const size = humanSize(job.size_bytes);
  if (size) rows.push({ label: "File", value: size });
  return rows;
}

/**
 * What may be said about waste.
 *
 * Snapmaker Orca reports one filament total per slot and does not separate
 * purge from printed material. Studio says that plainly instead of splitting a
 * number it cannot split.
 */
export function wasteNote(job: SlicedJob | undefined): string | null {
  const purge = job?.purge;
  if (!purge) return null;
  return purge.detail;
}

/** Cost lines the user can trust, labelled by where each number came from. */
export function costSourceLabel(source: string): string {
  switch (source) {
    case "measured":
      return "measured by the slicer";
    case "derived":
      return "from measured figures and your prices";
    case "assumption":
      return "an assumption you can change";
    default:
      return "not stated in the file";
  }
}

export function costHeadline(cost: SlicedCost | null): string {
  if (!cost) return "Costing this job…";
  return cost.summary;
}

export function resultLabel(result: PreflightResult): string {
  switch (result) {
    case "ok":
      return "Looks right";
    case "attention":
      return "Needs attention";
    case "blocked":
      return "Won't run on this printer";
    default:
      return "Studio can't tell";
  }
}

export function resultTone(result: PreflightResult): "ready" | "risk" | "muted" {
  if (result === "ok") return "ready";
  if (result === "unknown") return "muted";
  return "risk";
}
