import { describe, expect, it } from "vitest";
import type { FidelityReport, FidelityRow, FidelityStatus } from "@/api";
import {
  countsLine,
  fidelityHeadline,
  groupedRows,
  mayClaimNothingLost,
  looksBetterThanItIs,
  objectSettingsLine,
  targetNote,
  statusLabel,
  statusTone,
} from "./fidelity";

const row = (over: Partial<FidelityRow> = {}): FidelityRow => ({
  element: "Thing",
  status: "preserved_exact",
  detail: "byte-for-byte identical",
  reason: null,
  part: null,
  ...over,
});

const report = (over: Partial<FidelityReport> = {}): FidelityReport => ({
  schema_version: "fidelity/1",
  available: true,
  rows: [],
  counts: {},
  kept: [],
  changed: [],
  not_carried: [],
  unverified: [],
  claims: {
    geometry_unchanged: true,
    nothing_removed: true,
    fully_accounted: true,
    may_claim_nothing_lost: true,
  },
  summary: "",
  ...over,
});

describe("mayClaimNothingLost", () => {
  it("is only true when the engine granted the claim", () => {
    expect(mayClaimNothingLost(report())).toBe(true);
  });

  it("is false when anything was removed or could not be verified", () => {
    const withdrawn = report({
      claims: {
        geometry_unchanged: true,
        nothing_removed: false,
        fully_accounted: true,
        may_claim_nothing_lost: false,
      },
    });
    expect(mayClaimNothingLost(withdrawn)).toBe(false);
  });

  it("is false before the report arrives and when it failed", () => {
    expect(mayClaimNothingLost(null)).toBe(false);
    expect(mayClaimNothingLost(report({ available: false }))).toBe(false);
  });
});

describe("fidelityHeadline", () => {
  it("waits rather than claiming anything", () => {
    expect(fidelityHeadline(null)).toContain("Checking");
  });

  it("only makes the strong claim when it was granted", () => {
    expect(fidelityHeadline(report())).toContain("Everything Studio can identify");
  });

  it("never makes the strong claim when something is unverified", () => {
    const r = report({
      unverified: [row({ status: "unverified" })],
      claims: {
        geometry_unchanged: false,
        nothing_removed: true,
        fully_accounted: false,
        may_claim_nothing_lost: false,
      },
    });
    const headline = fidelityHeadline(r);
    expect(headline).not.toContain("Everything Studio can identify");
    // A message that names a problem must also say what to do about it.
    expect(headline).toContain("Snapmaker Orca");
    expect(headline).toContain("report it");
  });

  it("falls back to listing changes when nothing is unverified but something went", () => {
    const r = report({
      claims: {
        geometry_unchanged: true,
        nothing_removed: false,
        fully_accounted: true,
        may_claim_nothing_lost: false,
      },
    });
    expect(fidelityHeadline(r)).toContain("with the reason");
  });

  it("surfaces the engine's own reason when the audit could not run", () => {
    expect(fidelityHeadline(report({ available: false, summary: "Could not open it." })))
      .toBe("Could not open it.");
  });
});

describe("statusLabel and statusTone", () => {
  it("does not present an unchecked element as preserved", () => {
    expect(statusLabel("unverified")).toBe("Couldn’t check");
    expect(statusTone("unverified")).toBe("risk");
    expect(statusTone("unsupported")).toBe("risk");
  });

  it("marks both kinds of preservation as good", () => {
    expect(statusTone("preserved_exact")).toBe("ready");
    expect(statusTone("preserved_semantic")).toBe("ready");
  });

  it("treats a deliberate change as neutral, not as damage", () => {
    expect(statusTone("changed")).toBe("muted");
    expect(statusTone("removed")).toBe("muted");
    expect(statusTone("added")).toBe("muted");
  });

  it("has a label for every status", () => {
    const all: FidelityStatus[] = [
      "preserved_exact", "preserved_semantic", "changed",
      "added", "removed", "unsupported", "unverified",
    ];
    for (const s of all) expect(statusLabel(s).length).toBeGreaterThan(0);
  });
});

describe("groupedRows and countsLine", () => {
  it("is empty and silent before the report arrives", () => {
    expect(groupedRows(null)).toEqual({ kept: [], changed: [], notCarried: [], unverified: [] });
    expect(countsLine(null)).toBe("");
  });

  it("only lists non-empty groups", () => {
    const r = report({ kept: [row(), row()] });
    expect(countsLine(r)).toBe("2 kept");
  });

  it("names everything outstanding", () => {
    const r = report({
      kept: [row()],
      changed: [row({ status: "changed" })],
      not_carried: [row({ status: "removed" })],
      unverified: [row({ status: "unverified" })],
    });
    expect(countsLine(r)).toBe("1 kept · 1 changed · 1 not carried over · 1 unchecked");
  });
});

describe("objectSettingsLine", () => {
  const setting = (status: FidelityStatus, on = "cube"): FidelityRow =>
    row({ element: `Settings set on ${on}`, status });

  it("says nothing when the project set none", () => {
    expect(objectSettingsLine(report({ kept: [row()] }))).toBeNull();
  });

  it("counts a setting that crossed under a different name as preserved", () => {
    const r = report({ kept: [setting("preserved_semantic"), setting("preserved_exact")] });
    expect(objectSettingsLine(r)).toBe("2 object-specific settings preserved.");
  });

  it("names the ones that stayed behind", () => {
    const r = report({ not_carried: [setting("unsupported")] });
    expect(objectSettingsLine(r)).toBe(
      "1 object-specific setting was not carried — the list below says why.");
  });

  it("reports both halves when a project has some of each", () => {
    const r = report({
      kept: [setting("preserved_exact")],
      not_carried: [setting("unsupported"), setting("unsupported")],
    });
    expect(objectSettingsLine(r)).toBe(
      "1 object-specific setting preserved; 2 not carried — the list below says why.");
  });

  it("counts a setting the copy got wrong as not preserved", () => {
    const r = report({ changed: [setting("changed")] });
    expect(objectSettingsLine(r)).toContain("not carried");
  });

  it("says nothing for a report that is not available", () => {
    expect(objectSettingsLine(report({ available: false }))).toBeNull();
    expect(objectSettingsLine(null)).toBeNull();
  });
});

describe("targetNote", () => {
  it("says nothing about a fact the slicer was measured to read", () => {
    expect(targetNote(row({ target: "reaches_target" }))).toBeNull();
  });

  it("says nothing about a fact nobody has classified", () => {
    expect(targetNote(row({}))).toBeNull();
  });

  it("names a fact Orca rebuilds for itself", () => {
    expect(targetNote(row({ target: "reconstructed" }))).toContain("rebuilds");
  });

  it("names a fact Orca does not read", () => {
    expect(targetNote(row({ target: "ignored" }))).toContain("does not read");
  });

  it("says plainly when nobody has established it", () => {
    expect(targetNote(row({ target: "not_established" }))).toContain("not established");
  });
});

describe("looksBetterThanItIs", () => {
  it("flags a preserved fact the slicer rebuilds anyway", () => {
    expect(looksBetterThanItIs(
      row({ status: "preserved_exact", target: "reconstructed" }))).toBe(true);
  });

  it("does not flag a preserved fact the slicer reads", () => {
    expect(looksBetterThanItIs(
      row({ status: "preserved_exact", target: "reaches_target" }))).toBe(false);
  });

  it("does not flag a change, which is already not a win", () => {
    expect(looksBetterThanItIs(
      row({ status: "changed", target: "ignored" }))).toBe(false);
  });
});
