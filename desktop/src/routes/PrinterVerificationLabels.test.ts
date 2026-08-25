/**
 * The one thing the UI must never do with a second printer: round it up.
 *
 * "Profile verified" and "verified" are different claims. The first says Studio
 * ran its real printer logic against facts from a published configuration; the
 * second says a machine was connected and answered. Only the U1 has earned the
 * second, and a label that drops the qualifier turns an architecture proof into a
 * hardware claim nobody made.
 *
 * These labels live in the route file rather than being fetched, so this test
 * reads the source. That is deliberate: the point is to catch someone shortening
 * the string while tidying up, and a test that imported a mock would not.
 */
import { describe, expect, it } from "vitest";
import source from "./Printers.tsx?raw";

const LABELS = /const PRINTER_LABELS[\s\S]*?\n};/.exec(source)?.[0] ?? "";

describe("printer verification labels", () => {
  it("declares a label block at all", () => {
    expect(LABELS).not.toBe("");
  });

  it("keeps the qualifier on any printer that is not hardware verified", () => {
    expect(LABELS).toContain("profile verified — hardware not tested by this project");
  });

  it("reserves hardware verification for the U1", () => {
    const hardware = [...LABELS.matchAll(/(\w+):\s*\{[^}]*"hardware verified"/g)]
      .map((m) => m[1]);
    expect(hardware).toEqual(["snapmaker_u1"]);
  });

  it("never describes a second printer as supported, tested or simply verified", () => {
    const voron = /voron_2_4_250:\s*\{[\s\S]*?\}/.exec(LABELS)?.[0] ?? "";
    expect(voron).not.toBe("");
    expect(voron).not.toMatch(/"fully supported"|level:\s*"supported"/);
    expect(voron).not.toMatch(/level:\s*"tested"/);
    expect(voron).not.toMatch(/level:\s*"verified"/);
    expect(voron).not.toMatch(/level:\s*"hardware verified"/);
  });
});

describe("printer discovery wording", () => {
  it("does not call an answering Moonraker host a U1", () => {
    // A host that answered is a printer. Which printer it is comes from
    // identification, not from which hostname was probed.
    expect(source).not.toContain('"U1 found — ready"');
    expect(source).not.toContain('"not a U1"');
  });
});
