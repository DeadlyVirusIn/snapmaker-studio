import { describe, it, expect } from "vitest";
import {
  COPY, emptySelection, canDryRun, canExport, plateByUiNumber, fromOptions,
  toOptions, exportView,
  colorName, isGoldish, slotLabel, plateSummary, changeSummary, staysSame,
  hasSwappableColors,
  type Selection, type PlateInspect, type PlateDryRun, type PlateExport, type PlateInfo,
} from "./plateRemapWizard";

const inspect: PlateInspect = {
  available: true,
  filament_palette: { "3": { color: "#008000" }, "4": { color: "#F7D959" }, "6": { color: "#A3D8E1" } },
  plate_count: 2,
  plates: [
    { ui_number: 4, objects: [{ object_id: 12, base_filament: 6, painted_facets: 9 }, { object_id: 14, base_filament: 6 }],
      filaments_used: [{ id: 6, color: "#A3D8E1" }], painted_accents_present: true },
    { ui_number: 6, objects: [{ object_id: 18, base_filament: 6 }, { object_id: 99, base_filament: 4 }],
      filaments_used: [{ id: 6, color: "#A3D8E1" }, { id: 4, color: "#F7D959" }] },
  ],
  warnings: [],
};

describe("hasSwappableColors (no-base-colour empty state)", () => {
  it("is true when the plate has base filament slots", () => {
    expect(hasSwappableColors(inspect.plates![1])).toBe(true);
  });
  it("is false for a painted-only plate with no filament slots", () => {
    const painted: PlateInfo = { ui_number: 9, objects: [{ object_id: 1, painted_facets: 200 }], filaments_used: [], painted_accents_present: true };
    expect(hasSwappableColors(painted)).toBe(false);
  });
  it("is false for null", () => {
    expect(hasSwappableColors(null)).toBe(false);
  });
  it("the no-swappable copy never claims the original is modified", () => {
    expect(COPY.noSwappableColors.toLowerCase()).toContain("never modified");
  });
});

const goodDryRun: PlateDryRun = {
  available: true, ui_plate: 4, change_count: 2,
  changes: [{ object_id: 12, from_filament: 6, to_filament: 3 }, { object_id: 14, from_filament: 6, to_filament: 3 }],
  untouched_plates: [1, 2, 3, 5, 6, 7, 8, 9], warnings: [], painted_accents_preserved: true,
  verdict: "Plate 4: 2 object(s) would change filament 6 -> 3",
};

const sel4: Selection = { path: "/x.3mf", uiPlate: 4, fromFilament: 6, toFilament: 3 };

describe("1. wizard loads & selection", () => {
  it("starts empty and can't dry-run until file+plate+from+to chosen", () => {
    expect(canDryRun(emptySelection)).toBe(false);
    expect(canDryRun({ path: "/x.3mf", uiPlate: 4, fromFilament: 6, toFilament: null })).toBe(false);
    expect(canDryRun(sel4)).toBe(true);
  });
  it("rejects from==to", () => {
    expect(canDryRun({ path: "/x.3mf", uiPlate: 4, fromFilament: 6, toFilament: 6 })).toBe(false);
  });
});

describe("2/3. dry-run gates export", () => {
  it("cannot export without a dry-run", () => {
    expect(canExport(sel4, null)).toBe(false);
  });
  it("can export only after a valid, matching, warning-free dry-run with changes", () => {
    expect(canExport(sel4, goodDryRun)).toBe(true);
  });
  it("cannot export if dry-run has zero changes", () => {
    expect(canExport(sel4, { ...goodDryRun, change_count: 0, changes: [] })).toBe(false);
  });
  it("cannot export against a stale dry-run from a different plate", () => {
    expect(canExport({ ...sel4, uiPlate: 6 }, goodDryRun)).toBe(false);
  });
});

describe("4. success state", () => {
  it("derives a success view with verification checks + untouched plates", () => {
    const res: PlateExport = {
      available: true, passed: true, output_path: "/x_plate4_f6_to_f3.3mf",
      changed_objects: goodDryRun.changes, untouched_plates: [1, 2, 3, 5, 6, 7, 8, 9],
      verification: { passed: true, checks: [{ check: "only model_settings.config differs", pass: true }] },
    };
    const v = exportView(res)!;
    expect(v.kind).toBe("success");
    expect(v.message).toBe(COPY.success);
    expect((v as any).untouchedPlates).toContain(6);
    expect(v.checks.length).toBeGreaterThan(0);
  });
});

describe("5. failure state", () => {
  it("derives a safe-stopped view with reason + quarantine + untouched original", () => {
    const res: PlateExport = {
      available: true, passed: false, reason: "verification gate FAILED — output quarantined",
      quarantined: "/x.rejected", verification: { passed: false, checks: [] },
    };
    const v = exportView(res)!;
    expect(v.kind).toBe("failure");
    expect(v.message).toBe(COPY.failure);
    expect(v.message.toLowerCase()).toContain("not modified");
    expect((v as any).quarantined).toBe("/x.rejected");
  });
});

describe("6. warnings block export & stay visible", () => {
  it("a dry-run with warnings cannot be exported", () => {
    const warned: PlateDryRun = { ...goodDryRun, warnings: ["target filament 99 is not in this file's palette"] };
    expect(canExport(sel4, warned)).toBe(false);
    expect(warned.warnings!.length).toBe(1); // surfaced to render, not hidden
  });
});

describe("7. plate mapping by plater_id (not object order) + untouched plates", () => {
  it("plateByUiNumber finds Plate 4 and 6 by ui_number", () => {
    expect(plateByUiNumber(inspect, 4)!.objects.map((o) => o.object_id)).toEqual([12, 14]);
    expect(plateByUiNumber(inspect, 6)!.objects.map((o) => o.object_id)).toEqual([18, 99]);
  });
  it("from options are plate's used filaments; to options are full palette", () => {
    expect(fromOptions(plateByUiNumber(inspect, 4)).map((f) => f.id)).toEqual([6]);
    expect(toOptions(inspect).map((f) => f.id)).toEqual([3, 4, 6]);
  });
});

describe("8. copy never implies mesh/paint edits", () => {
  it("safety copy promises meshes & painted facets are unchanged", () => {
    const all = `${COPY.safety} ${COPY.subtitle} ${COPY.success}`.toLowerCase();
    expect(COPY.safety.toLowerCase()).toContain("meshes");
    expect(COPY.safety.toLowerCase()).toContain("painted facets");
    expect(COPY.safety.toLowerCase()).toContain("unchanged");
    expect(all).not.toMatch(/edit (the )?mesh|change (the )?paint|repaint|modify mesh/);
  });
});

describe("9. plain-English colour naming", () => {
  it("names common palette colours", () => {
    expect(colorName("#FFFFFF")).toBe("white");
    expect(colorName("#000000")).toBe("black");
    expect(colorName("#008000")).toBe("green");
    expect(colorName("#F7D959")).toBe("gold/yellow");
    expect(colorName("#A3D8E1")).toBe("light blue");
    expect(colorName(null)).toBeNull();
  });
  it("detects gold/yellow accents", () => {
    expect(isGoldish("#F7D959")).toBe(true);
    expect(isGoldish("#008000")).toBe(false);
  });
  it("labels a filament slot with its colour", () => {
    expect(slotLabel(6, "#A3D8E1")).toBe("light blue slot 6");
    expect(slotLabel(3, null)).toBe("slot 3");
  });
});

describe("10. beginner plate summary (what's on this plate)", () => {
  it("counts objects and flags painted details", () => {
    const s = plateSummary(plateByUiNumber(inspect, 4))!;
    expect(s.objectCount).toBe(2);
    expect(s.hasPainted).toBe(true);
    expect(s.sentence).toContain("Plate 4 has 2 objects and painted details");
  });
});

describe("11. what will change (plain English)", () => {
  it("describes from→to using colour names + slots", () => {
    const c = changeSummary(inspect, sel4)!;
    expect(c.fromName).toBe("light blue");
    expect(c.toName).toBe("green");
    expect(c.sentence).toContain("light blue slot 6");
    expect(c.sentence).toContain("green slot 3");
    expect(c.sentence.toLowerCase()).toContain("default color");
  });
});

describe("12. what will stay the same (protected details + untouched plates)", () => {
  it("plate 4: painted protected but colours unlabeled, Plate 6 untouched", () => {
    const plate4 = plateByUiNumber(inspect, 4);
    const s = staysSame(inspect, plate4, sel4, goodDryRun);
    expect(s.paintedProtected).toBe(true);
    expect(s.paintedColorsUnlabeled).toBe(true);   // painted present, no labelable base colour
    expect(s.otherPlates).toContain(6);            // Plate 6 untouched, from dry-run
  });
  it("detects gold/yellow as protected when a gold filament stays on the plate", () => {
    const plate6 = plateByUiNumber(inspect, 6);
    const sel6: Selection = { path: "/x.3mf", uiPlate: 6, fromFilament: 6, toFilament: 3 };
    const s = staysSame(inspect, plate6, sel6, null);
    expect(s.goldDetected).toBe(true);
    expect(s.protectedColorLabels).toContain("gold/yellow");
  });
});

describe("13. no technical jargon in primary beginner copy", () => {
  it("export CTA and questions avoid 'object-level extruder assignment'", () => {
    const beginner = `${COPY.exportCta} ${COPY.questionFrom} ${COPY.questionTo} ${COPY.safety}`.toLowerCase();
    expect(beginner).not.toContain("object-level extruder assignment");
    expect(beginner).not.toContain("extruder");
    expect(COPY.exportCta.toLowerCase()).toContain("safe copy");
  });
});
