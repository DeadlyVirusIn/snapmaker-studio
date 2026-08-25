import { describe, expect, it } from "vitest";
import type { ColorPlan, ColorUse, ColorVerdict } from "@/api";
import {
  COLOR_PLAN_TITLE,
  TOOLHEAD_EXPLAINER,
  groups,
  paintedDisclosure,
  paintedHeadline,
  paintedHeightRange,
  paintedLimit,
  paintedMeasurement,
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
  toolheads_measured: false,
  toolheads_source: "the Snapmaker U1's published four toolheads",
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
    expect(verdictBanner("needs_reduction")).toBe("More colours than toolheads to reserve");
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

// --- painted colour ---------------------------------------------------------
//
// The rule these protect: a beginner is told what is painted in one sentence,
// an expert can see every number behind it, and neither is told that painting
// cannot be read — because it now is.

function paintedPlan(overrides: Partial<ColorPlan["painted"]> = {}): ColorPlan {
  return {
    schema_version: "colorplan/1",
    available: true,
    color_count: 4,
    toolheads: 4,
    toolheads_measured: false,
    toolheads_source: "the Snapmaker U1's published four toolheads",
    painted_regions: true,
    painted: {
      available: true,
      painted: true,
      dialect: "bambu",
      format_version: 1,
      format_version_known: true,
      slots: [2, 3],
      unlisted_slots: [],
      painted_facets: 1240,
      malformed_facets: 0,
      facets_outside_mesh: 0,
      truncated: false,
      confidence: "confirmed",
      objects: [{
        object_id: "1",
        part: "3D/Objects/object_1.model",
        name: "shell",
        triangle_count: 5000,
        painted_triangle_count: 1240,
        mesh_area_mm2: 12000,
        default_slot: 1,
        default_slot_source: "this part is assigned slot 1 in the project's own part settings",
        transform_known: true,
        malformed_triangle_count: 0,
        facets_outside_mesh: 0,
        assignments: [],
      }],
      coexistence: { pairs: [], note: "" },
      headline: "Parts of this model are painted with 2 filament colours.",
      evidence: "1,240 painted facets",
      ...overrides,
    },
    simultaneous: [],
    layer_based: [],
    unclassified: [],
    verdict: "fits",
    headline: "4 colours, 4 toolheads — every colour has a toolhead.",
    summary: "Nothing to resolve.",
    guidance: [],
  } as ColorPlan;
}

const paintedUse: ColorUse = {
  slot: 3,
  color: "#FF0000",
  material: "PLA",
  usage: "layer_based",
  evidence: "painted only between 38.20 mm and 61.00 mm",
  painted: true,
  painted_facets: 812,
  painted_area_mm2: 3450.5,
  painted_z_min_mm: 38.2,
  painted_z_max_mm: 61,
};

describe("painted colour", () => {
  it("gives a beginner one sentence and nothing about file formats", () => {
    const line = paintedHeadline(paintedPlan());
    expect(line).toBe("Parts of this model are painted with 2 filament colours.");
    expect(line).not.toMatch(/paint_color|mmu_segmentation|facet/i);
  });

  it("says nothing at all when a project has no painting", () => {
    const plan = paintedPlan({ painted: false, headline: null });
    expect(paintedHeadline(plan)).toBeNull();
    expect(paintedDisclosure(plan)).toEqual([]);
    expect(paintedLimit(plan)).toBeNull();
  });

  it("measures a painted colour in facets, surface and height", () => {
    expect(paintedMeasurement(paintedUse)).toBe("812 painted facets · 34.5 cm² of surface · 38.2–61.0 mm");
  });

  it("shows nothing for a colour that is not painted on", () => {
    expect(paintedMeasurement({ ...paintedUse, painted: false })).toBe("");
  });

  it("states a single height rather than a range when the paint is flat", () => {
    expect(paintedHeightRange({ ...paintedUse, painted_z_min_mm: 12, painted_z_max_mm: 12 }))
      .toBe("at 12.0 mm");
  });

  it("puts the file-level facts in the expert panel, not the headline", () => {
    const rows = paintedDisclosure(paintedPlan());
    const labels = rows.map((r) => r.label);
    expect(labels).toContain("Read from");
    expect(labels).toContain("Painted facets");
    expect(rows.find((r) => r.label === "Read from")?.value).toMatch(/paint_color/);
    expect(rows.find((r) => r.label === "Painting format version")?.value).toBe("1");
  });

  it("says a version is undeclared rather than inventing one", () => {
    const rows = paintedDisclosure(paintedPlan({ format_version: null, format_version_known: false }));
    expect(rows.find((r) => r.label === "Painting format version")?.value)
      .toBe("not declared by this project");
  });

  it("surfaces a slot the project paints with but never lists", () => {
    const rows = paintedDisclosure(paintedPlan({ unlisted_slots: [6] }));
    expect(rows.some((r) => r.label.includes("never lists") && r.value === "6")).toBe(true);
  });

  it("marks truncated figures as a floor rather than a total", () => {
    const rows = paintedDisclosure(paintedPlan({ truncated: true }));
    expect(rows.find((r) => r.label === "Coverage")?.value).toMatch(/floor/);
  });

  it("says overlapping heights do not prove a shared layer", () => {
    const plan = paintedPlan({
      coexistence: {
        pairs: [{ slots: [2, 3], verdict: "overlaps", reason: "both painted between 0 and 10 mm" }],
        note: "",
      },
    });
    expect(paintedLimit(plan)).toMatch(/decided when Orca slices it/);
  });

  it("adds no caveat when every painted colour is proven separate", () => {
    const plan = paintedPlan({
      coexistence: {
        pairs: [{ slots: [2, 3], verdict: "separate", reason: "slot 2 ends below slot 3" }],
        note: "",
      },
    });
    expect(paintedLimit(plan)).toBeNull();
  });
});

// --- what an overlap is allowed to claim ------------------------------------
//
// Overlapping heights prove two colours *can* meet on a layer. Studio plans
// conservatively for that — a toolhead is reserved either way — but the copy
// must not tell the user a shared layer was proven, because it was not.

describe("overlap wording", () => {
  it("never tells the user that colours share layers", () => {
    const banned = /share (the same )?layers?|shares a layer|are on the same layer/i;
    expect(banned.test(verdictBanner("needs_reduction"))).toBe(false);
    expect(banned.test(verdictBanner("possible_with_swaps"))).toBe(false);
    expect(banned.test(TOOLHEAD_EXPLAINER)).toBe(false);
  });

  it("keeps the conservative plan: an overlap is never offered as a swap", () => {
    expect(suggestsSwaps(plan({ verdict: "needs_reduction" }))).toBe(false);
    expect(suggestsSwaps(plan({ verdict: "cannot_classify" }))).toBe(false);
  });
});
