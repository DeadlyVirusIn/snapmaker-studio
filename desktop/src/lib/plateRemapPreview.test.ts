import { describe, it, expect } from "vitest";
import { buildPlatePreview, type PlateInspect, type Selection } from "./plateRemapWizard";

const inspect: PlateInspect = {
  available: true,
  filament_palette: {
    "6": { color: "#88ccff" }, // light blue
    "4": { color: "#d4af37" }, // gold
    "7": { color: "#333333" }, // dark gray
  },
  plates: [
    {
      ui_number: 4,
      objects: [
        { object_id: 1, name: "Frame", base_filament: 6, painted_facets: 0 },
        { object_id: 2, name: "Star", base_filament: 4, painted_facets: 0 },
        { object_id: 3, name: "Logo", base_filament: 6, painted_facets: 9 },
      ],
      filaments_used: [
        { id: 6, color: "#88ccff" }, { id: 4, color: "#d4af37" }, { id: 7, color: "#333333" },
      ],
      painted_accents_present: true,
    },
    {
      ui_number: 5,
      objects: [{ object_id: 9, name: "Lid", base_filament: 7, painted_facets: 0 }],
      filaments_used: [{ id: 7, color: "#333333" }],
    },
  ],
};

const plate4 = inspect.plates![0];
const sel = (p: Partial<Selection> = {}): Selection =>
  ({ path: "x.3mf", uiPlate: 4, fromFilament: null, toFilament: null, ...p });

describe("buildPlatePreview (Plate Color Remap visual preview)", () => {
  it("resolves each object's base-filament colour into the preview", () => {
    const pv = buildPlatePreview(inspect, plate4, sel(), null)!;
    expect(pv.objects.map((o) => o.name)).toEqual(["Frame", "Star", "Logo"]);
    expect(pv.objects.find((o) => o.name === "Frame")!.colorHex).toBe("#88ccff");
    expect(pv.objects.find((o) => o.name === "Frame")!.colorLabel).toBe("blue");
  });

  it("flags the changing object from→to when source/target picked", () => {
    const pv = buildPlatePreview(inspect, plate4, sel({ fromFilament: 6, toFilament: 7 }), null)!;
    const frame = pv.objects.find((o) => o.name === "Frame")!;
    expect(frame.changing).toBe(true);
    expect(frame.toHex).toBe("#333333");
    expect(pv.changingCount).toBe(2); // Frame + Logo both base 6
    expect(pv.legend).toEqual(expect.objectContaining({ fromHex: "#88ccff", toHex: "#333333" }));
  });

  it("marks painted and gold objects as protected accents", () => {
    const pv = buildPlatePreview(inspect, plate4, sel({ fromFilament: 6, toFilament: 7 }), null)!;
    expect(pv.objects.find((o) => o.name === "Logo")!.protectedAccent).toBe(true);  // painted
    expect(pv.objects.find((o) => o.name === "Star")!.protectedAccent).toBe(true);  // gold
    expect(pv.objects.find((o) => o.name === "Star")!.changing).toBe(false);        // not the source
  });

  it("lists other plates as untouched (from inspect when no dry-run)", () => {
    const pv = buildPlatePreview(inspect, plate4, sel({ fromFilament: 6, toFilament: 7 }), null)!;
    expect(pv.untouchedPlates).toEqual([5]);
  });

  it("no-base-color plate is NOT a dead end — still renders the object map", () => {
    const painted: PlateInspect["plates"] = [{
      ui_number: 1,
      objects: [{ object_id: 1, name: "Bust", base_filament: null, painted_facets: 1200 }],
      filaments_used: [], // painted per-face only → no swappable base slot
      painted_accents_present: true,
    }];
    const pv = buildPlatePreview({ ...inspect, plates: painted }, painted![0], { path: "x", uiPlate: 1, fromFilament: null, toFilament: null }, null)!;
    expect(pv.swappableCount).toBe(0);
    expect(pv.objects).toHaveLength(1);           // still shows the object
    expect(pv.objects[0].painted).toBe(true);
    expect(pv.paintedAccentsPresent).toBe(true);
  });

  it("returns null with no plate selected", () => {
    expect(buildPlatePreview(inspect, null, sel(), null)).toBeNull();
  });
});
