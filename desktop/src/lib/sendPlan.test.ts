import { describe, expect, it } from "vitest";
import type { MaterialPlan, PrintPlan, SendCheck } from "@/api";
import {
  changeCount, itemLabel, itemsOfKind, materialsHeadline, orderedSlots, planHeadline,
  planIsTruncated, planLines, sendHeadline, sendTone, shouldDiscourageSend, slotLabel, slotTone,
} from "./sendPlan";

const plan = (over: Partial<PrintPlan> = {}): PrintPlan => ({
  schema_version: "printplan/1", available: true, layers_seen: 281,
  tools_seen: [0, 1, 2, 3], tool_changes: 764, pauses: 0, truncated: false,
  narration: [{ at: "Start", text: "Prints with slot 3", evidence: "T2 before any layer change" }],
  summary: "281 layers, slots 1, 2, 3, 4, 764 tool changes.", ...over,
});

const materials = (over: Partial<MaterialPlan> = {}): MaterialPlan => ({
  schema_version: "materialplan/1", available: true, printer_known: true,
  slots: [], to_change: [], ready: [], summary: "Nothing to change.", ...over,
});

const slot = (over: Partial<MaterialPlan["slots"][number]>): MaterialPlan["slots"][number] => ({
  tool: 0, label: "slot 1", needed: true, wants_material: "PLA", wants_colour: "#FF0000",
  has_material: "PLA", has_colour: "#FF0000", state: "ready", detail: null, action: null, ...over,
});

const check = (over: Partial<SendCheck> = {}): SendCheck => ({
  schema_version: "sendcheck/1", available: true, printer_reachable: true,
  verdict: "ready", counts: {}, items: [],
  headline: "Everything Studio can check looks right.",
  disclaimer: "Studio never sends anything on its own.", ...over,
});

describe("the print plan", () => {
  it("waits rather than showing an empty print", () => {
    expect(planHeadline(null)).toContain("Reading");
    expect(planLines(null)).toEqual([]);
  });

  it("surfaces the engine's own error instead of inventing one", () => {
    expect(planHeadline(plan({ available: false, error: "that file does not exist" })))
      .toBe("that file does not exist");
    expect(planLines(plan({ available: false }))).toEqual([]);
  });

  it("keeps the evidence attached to every line", () => {
    expect(planLines(plan())[0].evidence).toContain("T2");
  });

  it("says when it stopped early", () => {
    expect(planIsTruncated(plan({ truncated: true }))).toBe(true);
    expect(planIsTruncated(plan())).toBe(false);
  });
});

describe("what to load", () => {
  it("puts the slots that need action first and unused ones last", () => {
    const p = materials({ slots: [
      slot({ tool: 3, label: "slot 4", state: "unused" }),
      slot({ tool: 0, label: "slot 1", state: "ready" }),
      slot({ tool: 1, label: "slot 2", state: "empty" }),
      slot({ tool: 2, label: "slot 3", state: "different_colour" }),
    ] });
    expect(orderedSlots(p).map((s) => s.state))
      .toEqual(["empty", "different_colour", "ready", "unused"]);
  });

  it("tones an empty slot as a risk and a colour difference as a warning", () => {
    expect(slotTone("empty")).toBe("risk");
    expect(slotTone("wrong_material")).toBe("risk");
    expect(slotTone("different_colour")).toBe("warn");
    expect(slotTone("unused")).toBe("muted");
    expect(slotTone("unknown")).toBe("muted");
  });

  it("never labels an unknown as ready", () => {
    expect(slotLabel("unknown")).toBe("Studio can't tell");
    expect(slotLabel("unused")).toBe("Not used by this job");
  });

  it("counts only real changes", () => {
    expect(changeCount(materials({ to_change: [1, 2] }))).toBe(2);
    expect(changeCount(null)).toBe(0);
  });

  it("uses the engine's summary verbatim", () => {
    expect(materialsHeadline(materials({ summary: "Change slot 2." }))).toBe("Change slot 2.");
  });
});

describe("ready to send", () => {
  it("waits rather than claiming readiness", () => {
    expect(sendHeadline(null)).toContain("Checking");
    expect(sendTone(undefined)).toBe("muted");
  });

  it("keeps blockers, warnings and unknowns apart", () => {
    const c = check({ verdict: "blocker", items: [
      { kind: "blocker", title: "Slot 2 is empty", detail: "", action: null, source: null },
      { kind: "warning", title: "Different colour", detail: "", action: null, source: null },
      { kind: "unknown", title: "Nozzle", detail: "", action: null, source: null },
    ] });
    expect(itemsOfKind(c, "blocker")).toHaveLength(1);
    expect(itemsOfKind(c, "warning")).toHaveLength(1);
    expect(itemsOfKind(c, "unknown")).toHaveLength(1);
  });

  it("discourages sending only on a real blocker", () => {
    expect(shouldDiscourageSend(check({ verdict: "blocker" }))).toBe(true);
    expect(shouldDiscourageSend(check({ verdict: "warning" }))).toBe(false);
    expect(shouldDiscourageSend(check({ verdict: "unknown" }))).toBe(false);
    expect(shouldDiscourageSend(null)).toBe(false);
  });

  it("labels an unknown as something Studio cannot check, not as a fault", () => {
    expect(itemLabel("unknown")).toBe("Studio can't check this");
    expect(itemLabel("blocker")).toBe("Will stop the print");
  });

  it("never promises a successful print", () => {
    const text = (check().headline + check().disclaimer).toLowerCase();
    for (const promise of ["will print", "guaranteed", "100%"]) {
      expect(text).not.toContain(promise);
    }
  });
});
