// Source Compatibility / migration wizard — pure logic (no React, no I/O), so the
// recommendation flow is unit-testable. Advisory only: it never claims a full
// conversion Studio doesn't actually perform.
import type { SourceCompatibilityReport } from "@/api";

export type NextAction = "open_orca" | "prepare" | "inspect";

/** Overall readiness for the U1, in plain terms. */
export function readiness(r: SourceCompatibilityReport): "ready" | "prepare" | "unknown" {
  if (r.ecosystem === "unknown") return "unknown";
  if (r.ecosystem === "bambu-family" && r.is_u1) return "ready";
  return "prepare";
}

/** The single recommended next step (drives the primary CTA). */
export function nextAction(r: SourceCompatibilityReport): NextAction {
  if (r.ecosystem === "unknown") return "inspect";
  if (r.ecosystem === "bambu-family" && r.is_u1) return "open_orca";
  return "prepare"; // prusa / cura / generic / non-U1 bambu → make a clean U1 copy
}

export function nextActionLabel(a: NextAction): string {
  switch (a) {
    case "open_orca": return "Open in Snapmaker Orca";
    case "prepare": return "Prepare a clean U1 copy";
    case "inspect": return "Open & inspect";
  }
}

/** One-line beginner summary of what was detected. */
export function summaryLine(r: SourceCompatibilityReport): string {
  if (r.ecosystem === "unknown") return "Studio couldn't read this as a 3D model.";
  if (readiness(r) === "ready") return `Detected: ${r.ecosystem_label} — already a Snapmaker U1 project.`;
  return `Detected: ${r.ecosystem_label} — Studio can read the model, but it's not a U1 project yet.`;
}

export interface WizardStep { phase: "detect" | "read" | "limits" | "recommend"; title: string; items: string[]; }

/** The migration wizard steps, derived from the report. */
export function wizardSteps(r: SourceCompatibilityReport): WizardStep[] {
  const steps: WizardStep[] = [
    { phase: "detect", title: "What Studio detected", items: [r.source_app ? `${r.ecosystem_label} (${r.source_app})` : r.ecosystem_label] },
  ];
  if (r.can_read.length) steps.push({ phase: "read", title: "What Studio can read", items: r.can_read });
  if (r.cannot_convert.length) steps.push({ phase: "limits", title: "What needs Snapmaker Orca", items: r.cannot_convert });
  steps.push({ phase: "recommend", title: "Recommended next step", items: [r.recommended_next_step] });
  return steps;
}
