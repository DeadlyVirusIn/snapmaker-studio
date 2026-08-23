import { describe, expect, it } from "vitest";
import type { FidelityReport, FidelityRow, FidelityStatus } from "@/api";
import {
  countsLine,
  fidelityHeadline,
  groupedRows,
  mayClaimNothingLost,
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
