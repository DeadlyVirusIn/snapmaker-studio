/// <reference types="vite/client" />
import { describe, expect, it } from "vitest";

// beta.21: no future-tense promises or dead-end wording in user-facing copy.
// Code comments are allowed (they aren't rendered), so strip them first.
const BANNED = ["coming soon", "is coming", "will live", "coming later"];

const sources = import.meta.glob("../**/*.{ts,tsx}", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

function stripComments(src: string): string {
  return src
    .replace(/\/\*[\s\S]*?\*\//g, "")   // block comments (incl. {/* jsx */})
    .replace(/^\s*\/\/.*$/gm, "")        // line comments
    .replace(/\s\/\/[^"'`\n]*$/gm, "");  // trailing line comments
}

describe("user-facing copy", () => {
  it("contains no future-tense promise wording", () => {
    const offenders: string[] = [];
    for (const [path, text] of Object.entries(sources)) {
      if (path.endsWith(".test.ts") || path.endsWith(".test.tsx")) continue;
      const clean = stripComments(text).toLowerCase();
      for (const phrase of BANNED) {
        if (clean.includes(phrase)) offenders.push(`${path}: "${phrase}"`);
      }
    }
    expect(offenders).toEqual([]);
  });
});
