import { describe, it, expect } from "vitest";
import { QUALITY_SYMPTOMS, QUALITY_INTRO } from "./printQuality";

describe("Print Quality Doctor symptom picker", () => {
  it("offers all symptoms with unique ids, incl. bed adhesion + support failure", () => {
    expect(QUALITY_SYMPTOMS).toHaveLength(12);
    const ids = QUALITY_SYMPTOMS.map((s) => s.id);
    expect(new Set(ids).size).toBe(12);
    for (const id of ["stringing", "ringing", "warping", "under_extrusion", "color_bleed",
                      "bed_adhesion", "support_failure"]) {
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
