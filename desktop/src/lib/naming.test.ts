/// <reference types="vite/client" />
import { describe, expect, it } from "vitest";

// The user-facing feature is "Printer Hub" (registry id `printer`). "Printer
// Doctor" is banned in current UI copy — naming drift confused beta testers.
const BANNED = "Printer" + " Doctor"; // split so this file never matches itself

const sources = import.meta.glob("../**/*.{ts,tsx,css}", {
  query: "?raw",
  import: "default",
  eager: true,
}) as Record<string, string>;

describe("feature naming", () => {
  it(`desktop/src contains no "${BANNED}" copy (feature is Printer Hub)`, () => {
    const offenders = Object.entries(sources)
      .filter(([path]) => !path.endsWith("naming.test.ts"))
      .filter(([, text]) => text.includes(BANNED))
      .map(([path]) => path);
    expect(offenders).toEqual([]);
  });
});
