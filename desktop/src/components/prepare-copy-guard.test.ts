/// <reference types="vite/client" />
import { describe, expect, it } from "vitest";

const BANNED = ["optimized", "safe settings", "we fixed", "best", "ready", "clean"];
const sources = import.meta.glob(["./PrepareModeChooser.tsx", "./PrepareSettingsSummary.tsx"], { query: "?raw", import: "default", eager: true }) as Record<string, string>;

describe("prepare copy", () => {
  it("contains none of the disallowed wording", () => {
    const text = Object.values(sources).join("\n").toLowerCase();
    expect(BANNED.filter((word) => text.includes(word))).toEqual([]);
  });
});
