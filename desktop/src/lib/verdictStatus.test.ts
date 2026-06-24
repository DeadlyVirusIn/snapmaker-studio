import { describe, it, expect } from "vitest";
import { verdictStatus } from "./simple";

describe("verdictStatus — beginner action labels (advisory, no guarantees)", () => {
  it("maps each verdict to its action phrase", () => {
    expect(verdictStatus("READY").label).toBe("Looks ready to prepare");
    expect(verdictStatus("REPAIRABLE").label).toBe("Needs a fix first");
    expect(verdictStatus("CONVERTIBLE").label).toBe("Can prepare a U1 copy");
    expect(verdictStatus("HIGH_RISK").label).toBe("Review before printing");
  });

  it("is case-insensitive and tolerates junk", () => {
    expect(verdictStatus("ready").label).toBe("Looks ready to prepare");
    expect(verdictStatus(null).label).toBe("Checking…");
    expect(verdictStatus("weird").label).toBe("Checking…");
  });

  it("never uses guarantee language", () => {
    for (const v of ["READY", "REPAIRABLE", "CONVERTIBLE", "HIGH_RISK"]) {
      const l = verdictStatus(v).label.toLowerCase();
      expect(l).not.toMatch(/guarantee|100%|will print|will succeed/);
    }
  });
});
