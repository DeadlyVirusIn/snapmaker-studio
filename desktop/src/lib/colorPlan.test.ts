import { describe, expect, it } from "vitest";
import type { ColorPlan, ColorUse, ColorVerdict } from "@/api";
import {
  groups,
  suggestsSwaps,
  swapPointText,
  useLabel,
  verdictBanner,
  verdictTone,
} from "./colorPlan";

const use = (over: Partial<ColorUse> = {}): ColorUse => ({
  slot: 5,
  color: "#ff0000",
  material: "PLA",
  usage: "layer_based",
  evidence: "the project records a colour change at 8.20 mm",
  from_z_mm: 8.2,
  estimated_layer: 41,
  layer_is_estimated: true,
  ...over,
});

const plan = (over: Partial<ColorPlan> = {}): ColorPlan => ({
  schema_version: "colorplan/1",
  available: true,
  color_count: 6,
  toolheads: 4,
  painted_regions: false,
  simultaneous: [],
  layer_based: [],
  unclassified: [],
  verdict: "fits",
  headline: "",
  summary: "",
  guidance: [],
  ...over,
});

describe("verdictBanner", () => {
  it("matches the engine's four answers", () => {
    const all: ColorVerdict[] = ["fits", "possible_with_swaps", "needs_reduction", "cannot_classify"];
    for (const v of all) expect(verdictBanner(v).length).toBeGreaterThan(0);
    expect(verdictBanner("possible_with_swaps")).toBe("Possible without repainting");
    expect(verdictBanner("needs_reduction")).toBe("Needs colour reduction");
  });

  it("never presents an unclassifiable project as workable", () => {
    const text = verdictBanner("cannot_classify").toLowerCase();
    expect(text).toContain("can’t classify");
    expect(text).not.toContain("possible");
  });
});

describe("verdictTone", () => {
  it("does not colour an unclassified answer as a success", () => {
    expect(verdictTone("cannot_classify")).toBe("muted");
    expect(verdictTone("needs_reduction")).toBe("risk");
    expect(verdictTone("fits")).toBe("ready");
  });
});

describe("suggestsSwaps", () => {
  it("is only true when the engine said so", () => {
    expect(suggestsSwaps(plan({ verdict: "possible_with_swaps" }))).toBe(true);
    expect(suggestsSwaps(plan({ verdict: "cannot_classify" }))).toBe(false);
    expect(suggestsSwaps(plan({ verdict: "needs_reduction" }))).toBe(false);
  });

  it("is false before the answer arrives or when the read failed", () => {
    expect(suggestsSwaps(null)).toBe(false);
    expect(suggestsSwaps(plan({ available: false, verdict: "possible_with_swaps" }))).toBe(false);
  });
});

describe("swapPointText", () => {
  it("leads with the height, which is what the file records", () => {
    expect(swapPointText(use())).toBe("from 8.2 mm up (about layer 41)");
  });

  it("marks a layer number as approximate, never exact", () => {
    expect(swapPointText(use())).toContain("about layer");
  });

  it("omits the layer when it could not be estimated", () => {
    expect(swapPointText(use({ estimated_layer: null, layer_is_estimated: false })))
      .toBe("from 8.2 mm up");
  });

  it("says something honest when there is no height either", () => {
    expect(swapPointText(use({ from_z_mm: null }))).toContain("a height the project records");
  });
});

describe("useLabel", () => {
  it("names the slot and the material", () => {
    expect(useLabel(use())).toBe("Colour 5 PLA");
  });

  it("copes with an unnamed material", () => {
    expect(useLabel(use({ material: null }))).toBe("Colour 5");
  });
});

describe("groups", () => {
  it("is empty before the answer arrives", () => {
    expect(groups(null)).toEqual({ simultaneous: [], layerBased: [], unclassified: [] });
  });

  it("passes the engine's buckets straight through", () => {
    const g = groups(plan({ layer_based: [use()], unclassified: [use({ slot: 6 })] }));
    expect(g.layerBased).toHaveLength(1);
    expect(g.unclassified[0].slot).toBe(6);
  });
});
