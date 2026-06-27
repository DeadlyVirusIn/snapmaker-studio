import { describe, it, expect } from "vitest";
import { effectiveModelPath, isExt } from "./modelPath";
import type { FileRef } from "@/store/session";

const stl: FileRef = { path: "C:/m/part.stl", name: "part.stl", ext: "stl" };
const threemf: FileRef = { path: "C:/m/proj.3mf", name: "proj.3mf", ext: "3mf" };

describe("effectiveModelPath — tool pages reuse the loaded model", () => {
  it("reuses the session model when nothing is picked", () => {
    expect(effectiveModelPath(stl, null)).toEqual({ path: stl.path, fromSession: true });
  });
  it("a freshly picked file overrides the session model", () => {
    expect(effectiveModelPath(stl, "C:/other.stl")).toEqual({ path: "C:/other.stl", fromSession: false });
  });
  it("returns nothing when no session model and nothing picked", () => {
    expect(effectiveModelPath(null, null)).toEqual({ path: null, fromSession: false });
  });
  it("a 3MF-only tool ignores a loaded STL", () => {
    expect(effectiveModelPath(stl, null, isExt("3mf"))).toEqual({ path: null, fromSession: false });
  });
  it("a 3MF-only tool reuses a loaded 3MF", () => {
    expect(effectiveModelPath(threemf, null, isExt("3mf"))).toEqual({ path: threemf.path, fromSession: true });
  });
});
