import { describe, it, expect } from "vitest";
import { QUALITY_SYMPTOMS, QUALITY_INTRO } from "./printQuality";

describe("Print Quality Doctor symptom picker", () => {
  it("offers all ten symptoms with unique ids", () => {
    expect(QUALITY_SYMPTOMS).toHaveLength(10);
    const ids = QUALITY_SYMPTOMS.map((s) => s.id);
    expect(new Set(ids).size).toBe(10);
    for (const id of ["stringing", "ringing", "warping", "under_extrusion", "color_bleed"]) {
      expect(ids).toContain(id);
    }
  });

  it("intro is advisory — no auto-fix / guaranteed claims, states read-only", () => {
    const t = QUALITY_INTRO.toLowerCase();
    expect(t).not.toMatch(/auto-?fix|guaranteed?/);
    expect(t).toContain("advisory");
    expect(t).toContain("never changes your settings");
  });
});
