// Presentation logic for the three post-slice answers: what happens during the
// print, what to load, and whether to send.
//
// JSX-free so the rules stay testable. The rules: a blocker is never softened, a
// warning is never promoted, an unknown is neither, and nothing here ever says a
// print will succeed.

import type { MaterialPlan, MaterialSlot, PrintPlan, SendCheck, SendItem } from "@/api";

export const PLAN_TITLE = "What happens during this print";
export const PLAN_SUBTITLE =
  "Read in order from the sliced file. Every line names the G-code it came from.";

export const MATERIALS_TITLE = "What to load";
export const MATERIALS_SUBTITLE =
  "The job's tool assignments are fixed once it is sliced — this is what each slot needs.";

export const SEND_TITLE = "Ready to send?";

/** Never renders a missing timeline as an empty print. */
export function planHeadline(plan: PrintPlan | null): string {
  if (!plan) return "Reading the print…";
  if (!plan.available) return plan.error ?? "Studio could not read that file.";
  return plan.summary ?? "";
}

export function planLines(plan: PrintPlan | null) {
  return plan?.available ? plan.narration ?? [] : [];
}

export function planIsTruncated(plan: PrintPlan | null): boolean {
  return Boolean(plan?.truncated);
}

/** Slot state → what a person should feel about it. */
export function slotTone(state: MaterialSlot["state"]): "ready" | "risk" | "muted" | "warn" {
  switch (state) {
    case "ready":
      return "ready";
    case "empty":
    case "wrong_material":
      return "risk";
    case "different_colour":
      return "warn";
    default:
      return "muted";
  }
}

export function slotLabel(state: MaterialSlot["state"]): string {
  switch (state) {
    case "ready":
      return "Ready";
    case "empty":
      return "Empty";
    case "wrong_material":
      return "Wrong material";
    case "different_colour":
      return "Different colour";
    case "unused":
      return "Not used by this job";
    default:
      return "Studio can't tell";
  }
}

/** Slots worth acting on first, then the rest. Unused slots sink to the bottom. */
export function orderedSlots(plan: MaterialPlan | null): MaterialSlot[] {
  const rank: Record<string, number> = {
    empty: 0, wrong_material: 1, different_colour: 2, unknown: 3, ready: 4, unused: 5,
  };
  return [...(plan?.slots ?? [])].sort(
    (a, b) => (rank[a.state ?? "unknown"] ?? 9) - (rank[b.state ?? "unknown"] ?? 9),
  );
}

export function materialsHeadline(plan: MaterialPlan | null): string {
  if (!plan) return "Checking what is loaded…";
  return plan.summary;
}

export function changeCount(plan: MaterialPlan | null): number {
  return plan?.to_change?.length ?? 0;
}

// --- the send confirmation --------------------------------------------------

export function sendHeadline(check: SendCheck | null): string {
  if (!check) return "Checking whether this job is ready…";
  return check.headline;
}

export function sendTone(verdict: SendCheck["verdict"] | undefined): "ready" | "risk" | "warn" | "muted" {
  switch (verdict) {
    case "ready":
      return "ready";
    case "blocker":
      return "risk";
    case "warning":
      return "warn";
    default:
      return "muted";
  }
}

export function itemLabel(kind: SendItem["kind"]): string {
  switch (kind) {
    case "blocker":
      return "Will stop the print";
    case "warning":
      return "Worth settling first";
    default:
      return "Studio can't check this";
  }
}

/**
 * Whether the send button should be discouraged.
 *
 * Deliberately not "disabled": Studio does not overrule a person at their own
 * printer. A blocker makes the action secondary and the reason loud.
 */
export function shouldDiscourageSend(check: SendCheck | null): boolean {
  return check?.verdict === "blocker";
}

export function itemsOfKind(check: SendCheck | null, kind: SendItem["kind"]): SendItem[] {
  return (check?.items ?? []).filter((i) => i.kind === kind);
}
