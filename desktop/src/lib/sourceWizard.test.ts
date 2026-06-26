import { describe, it, expect } from "vitest";
import { readiness, nextAction, summaryLine, wizardSteps } from "./sourceWizard";
import type { SourceCompatibilityReport } from "@/api";

const base: SourceCompatibilityReport = {
  schema_version: "source/1", ecosystem: "generic", ecosystem_label: "Generic 3MF",
  source_app: "Generic 3MF", printer_model: null, is_u1: false, readable_settings: {},
  can_read: ["3D model geometry"], cannot_convert: ["no slicer settings are present in this file"],
  risks: [], recommended_next_step: "Open it and run Project Doctor, then set up the print in Snapmaker Orca.",
};
const r = (p: Partial<SourceCompatibilityReport>): SourceCompatibilityReport => ({ ...base, ...p });

describe("source migration wizard (pure)", () => {
  it("a U1 project is ready → open in Orca", () => {
    const rep = r({ ecosystem: "bambu-family", ecosystem_label: "Bambu-family 3MF", is_u1: true, cannot_convert: [],
      recommended_next_step: "This is already a Snapmaker U1 project — run Project Doctor, then Open in Snapmaker Orca to slice." });
    expect(readiness(rep)).toBe("ready");
    expect(nextAction(rep)).toBe("open_orca");
    expect(summaryLine(rep)).toMatch(/U1-family/);
    expect(summaryLine(rep)).not.toMatch(/print-ready|ready to slice/i);
  });

  it("a PrusaSlicer project → prepare a clean U1 copy", () => {
    const rep = r({ ecosystem: "prusa", ecosystem_label: "PrusaSlicer project", source_app: "PrusaSlicer" });
    expect(readiness(rep)).toBe("prepare");
    expect(nextAction(rep)).toBe("prepare");
    expect(summaryLine(rep)).toMatch(/not a U1 project yet/);
  });

  it("cura/generic also prepare (not a U1 project)", () => {
    expect(nextAction(r({ ecosystem: "cura", ecosystem_label: "Cura project" }))).toBe("prepare");
    expect(nextAction(base)).toBe("prepare");
  });

  it("unknown file → inspect, honest summary", () => {
    const rep = r({ ecosystem: "unknown", ecosystem_label: "Unrecognized file" });
    expect(readiness(rep)).toBe("unknown");
    expect(nextAction(rep)).toBe("inspect");
    expect(summaryLine(rep)).toMatch(/couldn't read/i);
  });

  it("wizard steps cover detect → read → limits → recommend", () => {
    const steps = wizardSteps(r({ ecosystem: "prusa", ecosystem_label: "PrusaSlicer project", source_app: "PrusaSlicer" }));
    expect(steps.map((s) => s.phase)).toEqual(["detect", "read", "limits", "recommend"]);
  });

  it("makes no false full-conversion claim", () => {
    for (const eco of ["prusa", "cura", "generic"] as const) {
      const steps = wizardSteps(r({ ecosystem: eco }));
      const blob = steps.flatMap((s) => s.items).join(" ").toLowerCase();
      expect(blob).not.toMatch(/fully convert|full conversion|100%|guarantee/);
    }
  });
});

describe("sourceWizard wording — source compat is not print readiness (beta.19)", () => {
  const u1: SourceCompatibilityReport = {
    ...base, ecosystem: "bambu-family", ecosystem_label: "Bambu/Orca 3MF", is_u1: true,
  };
  it("U1-family source is detected, not called print-ready", () => {
    const line = summaryLine(u1).toLowerCase();
    expect(line).toContain("u1-family");
    expect(line).not.toContain("already a snapmaker u1 project");
    expect(line).not.toMatch(/ready to slice|u1-ready/);
  });
});
