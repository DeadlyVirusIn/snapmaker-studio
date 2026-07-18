/// <reference types="vite/client" />
import { describe, expect, it } from "vitest";

const BANNED = ["optimized", "safe settings", "we fixed", "best", "ready", "clean"];
const BANNED_PATTERNS = [/\bsafe\b/i, /print-ready/i, /guaranteed/i];
const sources = import.meta.glob([
  "./PrepareModeChooser.tsx",
  "./PrepareSettingsSummary.tsx",
  "../routes/Compatibility.tsx",
  "../routes/DesignInsights.tsx",
  "../routes/LiveWorkspace.tsx",
], { query: "?raw", import: "default", eager: true }) as Record<string, string>;

// Pre-existing non-prepare UI state/style lines. These line-specific exceptions
// keep the guard focused on user-facing prepare/settings copy.
const allowlistedRouteLines: Record<string, number[]> = {
  "Compatibility.tsx": [43, 89, 90, 178],
  "DesignInsights.tsx": [139, 143, 144, 147, 154, 226, 277, 315, 316, 319, 336, 349, 350, 353, 372, 430, 439, 461, 470, 496, 504, 529],
  "LiveWorkspace.tsx": [90, 115, 139, 148, 216, 222, 277, 305, 311],
};

function sourceWithoutAllowlistedLines(path: string, source: string) {
  const filename = path.split("/").pop() ?? "";
  const allowed = new Set(allowlistedRouteLines[filename] ?? []);
  return source.split("\n").filter((_, index) => !allowed.has(index + 1)).join("\n");
}

describe("prepare copy", () => {
  it("contains none of the disallowed wording", () => {
    const text = Object.entries(sources).map(([path, source]) => sourceWithoutAllowlistedLines(path, source)).join("\n");
    expect([
      ...BANNED.filter((word) => text.toLowerCase().includes(word)),
      ...BANNED_PATTERNS.filter((pattern) => pattern.test(text)).map(String),
    ]).toEqual([]);
  });
});
