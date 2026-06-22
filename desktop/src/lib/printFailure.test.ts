import { describe, it, expect } from "vitest";
import {
  FAILURE_STAGES, PRINT_FAILURE_COPY, KNOWN_GOOD_MODE, UNKNOWN_MODE, failureMode, isBlameFree,
} from "./printFailure";
import type { PrintFailureResult } from "@/api";

describe("print failure troubleshooter helpers", () => {
  it("offers the failure stages incl. supports", () => {
    const ids = FAILURE_STAGES.map((s) => s.id);
    expect(ids).toEqual(expect.arrayContaining(["first_layer", "supports", "small_details", "mid_print", "unknown"]));
  });

  it("known-good mode renders the 'may already be printable' guidance", () => {
    const m = failureMode(true);
    expect(m.title).toMatch(/may already be printable/i);
    expect(m.points.join(" ").toLowerCase()).toContain("compare what changed");
    expect(m.points.join(" ").toLowerCase()).toContain("one change at a time");
    expect(m).toBe(KNOWN_GOOD_MODE);
  });

  it("unknown mode renders careful troubleshooting (supports don't guarantee)", () => {
    const m = failureMode(false);
    expect(m.title).toMatch(/troubleshoot supports/i);
    expect(m.points.join(" ").toLowerCase()).toContain("do not guarantee success");
    expect(m).toBe(UNKNOWN_MODE);
  });

  it("required beginner copy present: cooldown, one-change, silk swap, no auto-edit, not a guarantee", () => {
    expect(PRINT_FAILURE_COPY.cooldown).toMatch(/cooldown/i);
    expect(PRINT_FAILURE_COPY.oneChange).toMatch(/one change at a time/i);
    expect(PRINT_FAILURE_COPY.silkSwap).toMatch(/silk pla/i);
    expect(PRINT_FAILURE_COPY.noAutoEdit).toMatch(/does not auto-edit/i);
    expect(PRINT_FAILURE_COPY.notGuarantee).toMatch(/not a guarantee/i);
  });

  it("copy carries no blame / guarantee / auto-fix wording", () => {
    const all = Object.values(PRINT_FAILURE_COPY).join(" ").toLowerCase()
      + KNOWN_GOOD_MODE.points.join(" ").toLowerCase()
      + UNKNOWN_MODE.points.join(" ").toLowerCase();
    for (const bad of ["settings are wrong", "is wrong", "will fail", "too aggressive", "guaranteed", "auto-fix"]) {
      expect(all).not.toContain(bad);
    }
  });

  it("isBlameFree flags a blaming result and passes a clean one", () => {
    const clean: PrintFailureResult = { available: true, summary: "compare what changed", findings: [] };
    expect(isBlameFree(clean)).toBe(true);
    const dirty: PrintFailureResult = { available: true, summary: "these settings are wrong and will fail", findings: [] };
    expect(isBlameFree(dirty)).toBe(false);
  });
});
