import { describe, expect, it, beforeEach } from "vitest";
import { useSliced } from "./sliced";

describe("the sliced job store", () => {
  beforeEach(() => useSliced.getState().clear());

  it("shows a file name, never a home directory", () => {
    // This was a real defect: the separator class was written with one backslash
    // instead of two, so a Windows path never split and the page displayed
    // "C:\Users\someone\Downloads\job.gcode" where the file name belonged —
    // including in a recorded demo.
    useSliced.getState().setSliced(String.raw`C:\Users\someone\Downloads\job_PLA_2h13m.gcode`);
    expect(useSliced.getState().name).toBe("job_PLA_2h13m.gcode");
  });

  it("handles posix paths too", () => {
    useSliced.getState().setSliced("/home/someone/prints/job.gcode");
    expect(useSliced.getState().name).toBe("job.gcode");
  });

  it("keeps the full path for the engine, which needs it", () => {
    const full = String.raw`C:\Users\someone\job.gcode`;
    useSliced.getState().setSliced(full);
    expect(useSliced.getState().path).toBe(full);
  });

  it("falls back to the whole string when there is no separator", () => {
    useSliced.getState().setSliced("job.gcode");
    expect(useSliced.getState().name).toBe("job.gcode");
  });

  it("clears both", () => {
    useSliced.getState().setSliced(String.raw`C:\a\b.gcode`);
    useSliced.getState().clear();
    expect(useSliced.getState().path).toBeNull();
    expect(useSliced.getState().name).toBeNull();
  });
});
