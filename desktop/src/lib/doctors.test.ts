import { describe, it, expect } from "vitest";
import { DOCTORS, doctorById } from "./doctors";

// Locks the DoctorLanding honesty contract at the data layer: a valid id resolves
// to a Doctor, an unknown id resolves to null (the route renders NotFound).
describe("doctorById (DoctorLanding routing contract)", () => {
  it("resolves a known Doctor id", () => {
    const d = doctorById("project");
    expect(d).not.toBeNull();
    expect(d!.name).toBe("Project Doctor");
    expect(d!.route).toBeTruthy();
  });
  it("returns null for an unknown id (→ NotFound)", () => {
    expect(doctorById("does-not-exist")).toBeNull();
    expect(doctorById(undefined)).toBeNull();
  });
  it("every Doctor has a non-empty route and answer", () => {
    for (const d of DOCTORS) {
      expect(d.route).toBeTruthy();
      expect(d.answers.length).toBeGreaterThan(0);
    }
  });
});
