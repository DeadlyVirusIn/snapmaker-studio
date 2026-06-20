import { describe, it, expect } from "vitest";
import {
  COPY, emptySelection, canDryRun, canExport, plateByUiNumber, fromOptions,
  toOptions, exportView,
  type Selection, type PlateInspect, type PlateDryRun, type PlateExport,
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
