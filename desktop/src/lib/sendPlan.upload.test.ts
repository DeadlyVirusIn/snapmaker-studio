import { describe, expect, it } from "vitest";
import { orderedSlots, slotLabel, slotTone, uploadTitle, uploadTone } from "./sendPlan";
import type { MaterialPlan, MaterialSlot } from "@/api";

/**
 * The words after a send, and the order of the slots before one.
 *
 * Both were places where a real distinction was being flattened: four different
 * upload outcomes reading as one failure, and two different kinds of "short of
 * filament" reading as "Studio can't tell".
 */
describe("what Studio says happened to an upload", () => {
  it("never lets four different situations read as one failure", () => {
    const said = [
      "verified", "pending_verification", "not_listed", "mismatch",
      "refused_by_printer", "not_accepted", "changed",
    ].map((state) => uploadTitle(state as never));
    expect(new Set(said).size).toBe(said.length);
  });

  it("does not present a file the printer is still reading as a failure", () => {
    expect(uploadTone("pending_verification")).toBe("muted");
    expect(uploadTitle("pending_verification")).toContain("still reading");
  });

  it("says plainly when nothing was sent because the world moved", () => {
    expect(uploadTitle("changed")).toContain("Nothing was sent");
  });

  it("only calls an upload done when the printer confirmed it", () => {
    expect(uploadTone("verified")).toBe("ready");
    expect(uploadTone(undefined)).toBe("muted");
    expect(uploadTitle(undefined)).toContain("could not confirm");
  });
});

describe("slots that may not have enough filament", () => {
  it("tells a tracked shortfall apart from an uncertain one", () => {
    expect(slotLabel("not_enough")).toBe("Not enough filament");
    expect(slotLabel("maybe_not_enough")).toBe("May not have enough");
    expect(slotTone("not_enough")).toBe("risk");
    expect(slotTone("maybe_not_enough")).toBe("warn");
  });

  it("puts what will stop the print above what merely might", () => {
    const slots = [
      { tool: 0, state: "ready" },
      { tool: 1, state: "maybe_not_enough" },
      { tool: 2, state: "not_enough" },
      { tool: 3, state: "empty" },
      { tool: 4, state: "unused" },
    ] as MaterialSlot[];
    const order = orderedSlots({ slots } as MaterialPlan).map((s) => s.tool);
    expect(order).toEqual([3, 2, 1, 0, 4]);
  });
});
