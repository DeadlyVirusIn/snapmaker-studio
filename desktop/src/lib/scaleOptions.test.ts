import { describe, it, expect } from "vitest";
import {
  SCALE_LADDER_COPY, recommendBlurb, isRecommended, isCaution, riskLabel,
  fmtDims, partLabel,
} from "./scaleOptions";
import type { ScaleOptionsResult } from "@/api";

const R: ScaleOptionsResult = {
  available: true,
  build_volume: { x: 270, y: 270, z: 270 },
  group_scaling_recommended: true,
  limiting_part: "Plate 1",
  limiting_axis: "x",
  recommended_scale_percent: 128,
  current_parts: [
    { plate_index: 1, name: "P1", dimensions: { x: 200.93, y: 200.93, z: 117.28 } },
    { plate_index: 2, name: "P2", dimensions: { x: 191.99, y: 192, z: 22 } },
  ],
  options: [
    { label: "Safest novice max", scale_percent: 128, risk_level: "low", recommendation: "Recommended starting point",
      dimensions_by_part: [
        { plate_index: 1, name: "P1", dimensions: { x: 257.2, y: 257.2, z: 150.1 } },
        { plate_index: 2, name: "P2", dimensions: { x: 245.8, y: 245.8, z: 28.2 } }],
      explanation: "safe" },
    { label: "Still reasonable, tight margin", scale_percent: 130, risk_level: "medium", recommendation: "Usable",
      dimensions_by_part: [], explanation: "tight" },
    { label: "Theoretical max, too close", scale_percent: 134, risk_level: "high", recommendation: "Not recommended",
      dimensions_by_part: [], explanation: "edge" },
    { label: "Absolute limit, not recommended", scale_percent: 134.3, risk_level: "high", recommendation: "Not recommended",
      dimensions_by_part: [], explanation: "limit" },
  ],
  warnings: [SCALE_LADDER_COPY.notGuarantee, "Brim or raft needs extra space beyond these sizes."],
  next_steps: ["Studio recommends starting with 128%."],
};

describe("scale options ladder helpers", () => {
  it("ladder has 4 options and per-part dims for the safe row", () => {
    expect(R.options).toHaveLength(4);
    expect(R.options![0].dimensions_by_part).toHaveLength(2);
    expect(fmtDims(R.options![0].dimensions_by_part[0].dimensions)).toContain("257.2");
  });
  it("size-only ladder is NOT marked recommended; blurb tells user to verify in Orca", () => {
    // No placement_verified -> Orca may reject on placement, so never 'recommended'.
    expect(isRecommended(R.options![0], R)).toBe(false);
    const b = recommendBlurb(R);
    expect(b).toContain("size only");
    expect(b).toContain("Orca");
  });
  it("placement-verified ladder marks the recommended row", () => {
    const V = { ...R, placement_verified: true } as typeof R;
    expect(isRecommended(V.options![0], V)).toBe(true);
    expect(isRecommended(V.options![2], V)).toBe(false);
    expect(recommendBlurb(V)).toContain("verified");
  });
  it("theoretical + absolute are caution / not recommended", () => {
    expect(isCaution(R.options![2])).toBe(true);
    expect(isCaution(R.options![3])).toBe(true);
    expect(isCaution(R.options![0])).toBe(false);
    expect(R.options![3].label.toLowerCase()).toContain("not recommended");
  });
  it("risk labels map", () => {
    expect(riskLabel("low")).toBe("Recommended");
    expect(riskLabel("medium")).toBe("Tight");
    expect(riskLabel("high")).toBe("Risky");
  });
  it("multi-plate part labels render", () => {
    expect(partLabel(R.current_parts![0] as any)).toBe("Plate 1");
    expect(partLabel(R.current_parts![1] as any)).toBe("Plate 2");
  });
  it("group warning + no guarantee copy present, no guarantee-of-success claim", () => {
    expect(SCALE_LADDER_COPY.groupSeparate).toMatch(/do not scale/i);
    expect(SCALE_LADDER_COPY.notGuarantee).toMatch(/not a guarantee/i);
    const all = Object.values(SCALE_LADDER_COPY).join(" ").toLowerCase();
    expect(all).not.toContain("guaranteed");
  });
});
