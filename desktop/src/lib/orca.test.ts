import { describe, it, expect } from "vitest";
import { orcaErrorMessage, ORCA_RELEASES_URL, ORCA_HANDOFF_LINE } from "./orca";

describe("orcaErrorMessage", () => {
  it("maps orca-not-found to install guidance", () => {
    expect(orcaErrorMessage(new Error("orca-not-found"))).toMatch(/Install Snapmaker Orca/);
  });
  it("maps prepared-file-missing to a prepare-again hint", () => {
    expect(orcaErrorMessage(new Error("prepared-file-missing"))).toMatch(/prepared file/i);
  });
  it("maps launch-failed to a fallback hint", () => {
    expect(orcaErrorMessage(new Error("launch-failed: os error 2"))).toMatch(/open the file from Orca/i);
  });
  it("handles a bare string and unknown errors without leaking it", () => {
    const m = orcaErrorMessage("C:/Users/secret/path.3mf blew up");
    expect(m).not.toMatch(/secret/);
    expect(m.length).toBeGreaterThan(0);
  });
  it("never claims Studio slices or controls Orca", () => {
    const line = ORCA_HANDOFF_LINE.toLowerCase();
    expect(line).not.toMatch(/studio slices/);
    expect(line).not.toMatch(/studio controls/);
    expect(line).toContain("snapmaker orca slices it next");
  });
  it("links to the official Snapmaker Orca releases page", () => {
    expect(ORCA_RELEASES_URL).toBe("https://github.com/Snapmaker/OrcaSlicer/releases");
  });
});
