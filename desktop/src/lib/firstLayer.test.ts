import { describe, it, expect } from "vitest";
import { FIRST_LAYER_SYMPTOMS, FIRST_LAYER_INTRO, isAdvanced } from "./firstLayer";

describe("First Layer Doctor symptom picker", () => {
  it("offers all ten symptoms with unique ids", () => {
    expect(FIRST_LAYER_SYMPTOMS).toHaveLength(10);
    const ids = FIRST_LAYER_SYMPTOMS.map((s) => s.id);
    expect(new Set(ids).size).toBe(10);
    for (const id of ["not_stick", "nozzle_too_high", "toolhead_specific", "breaks_loose"]) {
      expect(ids).toContain(id);
    }
  });

  it("intro is advisory — no auto-fix/guaranteed, states read-only", () => {
    const t = FIRST_LAYER_INTRO.toLowerCase();
    expect(t).not.toMatch(/auto-?fix|guaranteed?/);
    expect(t).toContain("advisory");
    expect(t).toContain("never changes your printer config");
  });

  it("flags advanced checks by their (advanced) prefix", () => {
    expect(isAdvanced("(advanced) re-run heated bed leveling")).toBe(true);
    expect(isAdvanced("clean the build plate")).toBe(false);
  });
});
