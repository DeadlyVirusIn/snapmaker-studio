import { describe, expect, it } from "vitest";
import type { Preflight, PreflightCheck } from "@/api";
import {
  attentionCount,
  isPrinterMissing,
  preflightHeadline,
  resultLabel,
  resultTone,
  unknownCount,
} from "./preflight";

const check = (over: Partial<PreflightCheck> = {}): PreflightCheck => ({
  id: "x",
  title: "X",
  result: "ok",
  evidence: "because",
  confidence: "confirmed",
  consequence: "so what",
  action: null,
  source: "test",
  ...over,
});

const pre = (over: Partial<Preflight> = {}): Preflight => ({
  schema_version: "preflight/1",
  checks: [],
  counts: { ok: 0, attention: 0, unknown: 0, blocked: 0 },
  needs_attention: [],
  unknowns: [],
  printer_reachable: true,
  summary: "",
  disclaimer: "advisory",
  ...over,
});

describe("resultLabel", () => {
  it("never calls an unknown a pass or a failure", () => {
    expect(resultLabel("unknown")).toBe("Studio can't tell");
    expect(resultLabel("unknown")).not.toContain("Looks right");
    expect(resultLabel("unknown")).not.toContain("attention");
  });

  it("uses beginner wording rather than pass/fail", () => {
    expect(resultLabel("ok")).toBe("Looks right");
    expect(resultLabel("attention")).toBe("Needs attention");
    expect(resultLabel("blocked")).toBe("Can't work as-is");
  });
});

describe("resultTone", () => {
  it("gives an unknown its own neutral tone, not a warning colour", () => {
    expect(resultTone("unknown")).toBe("muted");
    expect(resultTone("ok")).toBe("ready");
    expect(resultTone("attention")).toBe("risk");
    expect(resultTone("blocked")).toBe("risk");
  });
});

describe("counts", () => {
  it("counts problems and unknowns separately", () => {
    const p = pre({ counts: { ok: 3, attention: 2, unknown: 4, blocked: 1 } });
    expect(attentionCount(p)).toBe(3);
    expect(unknownCount(p)).toBe(4);
  });

  it("is zero before the check returns", () => {
    expect(attentionCount(null)).toBe(0);
    expect(unknownCount(null)).toBe(0);
  });
});

describe("preflightHeadline", () => {
  it("waits rather than claiming anything before the check returns", () => {
    expect(preflightHeadline(null)).toContain("Comparing");
  });

  it("uses the engine's own summary rather than inventing one", () => {
    expect(preflightHeadline(pre({ summary: "Nothing to resolve." })))
      .toBe("Nothing to resolve.");
  });
});

describe("isPrinterMissing", () => {
  it("is false before the check returns", () => {
    expect(isPrinterMissing(null)).toBe(false);
  });

  it("detects the connect-a-printer case", () => {
    expect(isPrinterMissing(pre({ printer_reachable: false }))).toBe(true);
    expect(isPrinterMissing(pre({ printer_reachable: true }))).toBe(false);
  });
});

describe("wording guard", () => {
  it("no label promises a print will succeed", () => {
    const labels = (["ok", "attention", "unknown", "blocked"] as const).map(resultLabel);
    for (const label of labels) {
      const lowered = label.toLowerCase();
      expect(lowered).not.toContain("ready to print");
      expect(lowered).not.toContain("will print");
      expect(lowered).not.toContain("guaranteed");
      expect(lowered).not.toContain("safe");
    }
  });

  it("an unknown check keeps its own wording rather than borrowing a verdict", () => {
    const c = check({ result: "unknown", title: "Nozzle size — check this yourself" });
    expect(resultLabel(c.result)).toBe("Studio can't tell");
  });
});
