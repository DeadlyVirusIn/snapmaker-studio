import { describe, it, expect } from "vitest";
import { PRIMARY_NAV, SECONDARY_NAV, isKnownRoute } from "./nav";
import { DOCTORS } from "./doctors";

const primaryLabels = PRIMARY_NAV.map((n) => n.label);
const primaryRoutes = PRIMARY_NAV.map((n) => n.to);

// Cost / Pricing / Profit are one combined "Cost & Pricing Doctor" page, so they
// share a single sidebar entry instead of three duplicates.
const BIZ_IDS = new Set(["cost", "pricing", "profit"]);

describe("1. sidebar exposes core Doctors directly", () => {
  it("every non-business Doctor is reachable from the primary sidebar", () => {
    for (const d of DOCTORS) {
      if (BIZ_IDS.has(d.id)) continue; // consolidated into one item below
      expect(primaryRoutes).toContain(d.route);
    }
  });
  it("Cost/Pricing/Profit are one combined sidebar item, not three", () => {
    const bizItems = PRIMARY_NAV.filter((n) => n.doctorId && BIZ_IDS.has(n.doctorId));
    expect(bizItems).toHaveLength(1);
    expect(bizItems[0].label).toBe("Cost & Pricing Doctor");
  });
  it("old Cost/Pricing/Profit routes still resolve (aliases, no crash)", () => {
    for (const id of BIZ_IDS) {
      expect(isKnownRoute(`/doctor/${id}`)).toBe(true);
    }
  });
  it("core P0 doctors are present by name", () => {
    for (const name of ["Project Doctor", "Printer Doctor", "First Layer Doctor", "Multi-Material Doctor"]) {
      expect(primaryLabels).toContain(name);
    }
  });
});

describe("2. Why Studio? is not in primary workflow nav", () => {
  it("lives in secondary, not primary", () => {
    expect(primaryLabels).not.toContain("Why Studio?");
    expect(SECONDARY_NAV.map((n) => n.label)).toContain("Why Studio?");
  });
});

describe("3. Plate Color Remap grouped near Multi-Material Doctor", () => {
  it("sits immediately next to the Multi-Material Doctor", () => {
    const mm = primaryLabels.indexOf("Multi-Material Doctor");
    const remap = primaryLabels.indexOf("Plate Color Remap");
    expect(mm).toBeGreaterThanOrEqual(0);
    expect(remap).toBeGreaterThanOrEqual(0);
    expect(Math.abs(remap - mm)).toBe(1);
  });
});

describe("4. Dashboard Doctor cards route to matching pages / safe landings", () => {
  it("every Doctor route resolves to a known route", () => {
    for (const d of DOCTORS) {
      expect(isKnownRoute(d.route)).toBe(true);
    }
  });
});

describe("5. no broken routes / blank pages", () => {
  it("every primary + secondary nav target is a known route", () => {
    for (const n of [...PRIMARY_NAV, ...SECONDARY_NAV]) {
      expect(isKnownRoute(n.to)).toBe(true);
    }
  });
  it("rejects an unknown route", () => {
    expect(isKnownRoute("/doctor/does-not-exist")).toBe(false);
    expect(isKnownRoute("/nope")).toBe(false);
  });
});
