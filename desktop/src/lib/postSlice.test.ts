import { describe, expect, it } from "vitest";
import type { PostSlice, SlicedCost, SlicedJob } from "@/api";
import {
  costHeadline,
  costSourceLabel,
  humanDuration,
  humanSize,
  isUnreadable,
  jobFacts,
  postSliceHeadline,
  problemCount,
  resultLabel,
  resultTone,
  slotList,
  unknownCount,
  wasteNote,
} from "./postSlice";

const job = (over: Partial<SlicedJob> = {}): SlicedJob => ({
  slicer: "Snapmaker Orca",
  slicer_version: "2.3.4",
  printer_model: "Snapmaker U1",
  layer_count: 45,
  layer_height_mm: 0.2,
  max_z_mm: 9.05,
  estimated_seconds: 391,
  tools_used: [1],
  total_g: 0.91,
  size_bytes: 350527,
  purge: { separable: false, expected: false, detail: "Single-tool job: no tool-change purge." },
  ...over,
});

const report = (over: Partial<PostSlice> = {}): PostSlice => ({
  schema_version: "post_slice/1",
  available: true,
  printer_reachable: true,
  job: job(),
  checks: [],
  counts: {},
  summary: "Everything Studio can check looks right.",
  disclaimer: "Studio does not slice.",
  ...over,
});

describe("headline and state", () => {
  it("waits rather than claiming anything", () => {
    expect(postSliceHeadline(null)).toContain("Reading");
  });

  it("uses the engine's own summary, never its own wording", () => {
    expect(postSliceHeadline(report({ summary: "1 thing to sort out." }))).toBe("1 thing to sort out.");
  });

  it("knows an unreadable file from a healthy one", () => {
    expect(isUnreadable(report())).toBe(false);
    expect(isUnreadable(report({ available: false }))).toBe(true);
    expect(isUnreadable(null)).toBe(false);
  });

  it("counts blocked with attention, and unknown separately", () => {
    const r = report({ counts: { attention: 2, blocked: 1, unknown: 3, ok: 4 } });
    expect(problemCount(r)).toBe(3);
    expect(unknownCount(r)).toBe(3);
  });
});

describe("slots are shown the way spools are labelled", () => {
  it("is 1-based, because slot 0 means nothing to a user", () => {
    expect(slotList([0, 2])).toBe("slot 1, slot 3");
  });

  it("says nothing rather than 'none' when the file did not state it", () => {
    expect(slotList(null)).toBeNull();
    expect(slotList([])).toBeNull();
  });
});

describe("job facts", () => {
  it("lists only what the file actually stated", () => {
    const rows = jobFacts(job({ estimated_seconds: null, total_g: null }));
    const labels = rows.map((r) => r.label);
    expect(labels).toContain("Sliced by");
    expect(labels).toContain("Prints from");
    expect(labels).not.toContain("Estimated time");
    expect(labels).not.toContain("Filament");
  });

  it("is empty for a job that could not be read", () => {
    expect(jobFacts(undefined)).toEqual([]);
  });
});

describe("durations and sizes", () => {
  it("never renders a missing figure as zero", () => {
    expect(humanDuration(null)).toBeNull();
    expect(humanDuration(0)).toBeNull();
    expect(humanSize(null)).toBeNull();
  });

  it("reads naturally", () => {
    expect(humanDuration(391)).toBe("7 min");
    expect(humanDuration(3600 * 2 + 60 * 13)).toBe("2 h 13 min");
    expect(humanSize(350527)).toBe("342 KB");
    expect(humanSize(263790071)).toBe("252 MB");
  });
});

describe("waste and cost honesty", () => {
  it("passes the engine's own explanation through unchanged", () => {
    expect(wasteNote(job())).toContain("no tool-change purge");
  });

  it("labels every cost line by where the number came from", () => {
    expect(costSourceLabel("measured")).toContain("slicer");
    expect(costSourceLabel("assumption")).toContain("change");
    expect(costSourceLabel("unknown")).toContain("not stated");
  });
});

describe("result wording", () => {
  it("never says pass or fail", () => {
    expect(resultLabel("ok")).toBe("Looks right");
    expect(resultLabel("unknown")).toBe("Studio can't tell");
    expect(resultLabel("blocked")).toBe("Won't run on this printer");
  });

  it("tones an unknown as neutral, not as a problem", () => {
    expect(resultTone("unknown")).toBe("muted");
    expect(resultTone("attention")).toBe("risk");
    expect(resultTone("ok")).toBe("ready");
  });
});

describe("cost headline", () => {
  it("waits rather than showing a zero", () => {
    expect(costHeadline(null)).toContain("Costing");
  });

  it("uses the engine's own summary", () => {
    const cost = { schema_version: "slicedcost/1", available: true,
                   summary: "About $0.02 for 0.91 g." } as SlicedCost;
    expect(costHeadline(cost)).toBe("About $0.02 for 0.91 g.");
  });
});
