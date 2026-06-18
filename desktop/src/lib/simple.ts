// Novice-first presentation helpers — turn engine values into beginner language.
// Pure functions over the existing /doctor result; no new data, no jargon.

export type Tone = "ready" | "repairable" | "convertible" | "risk";

/** 0–100 score → 0..5 (half-star aware). */
export function readinessStars(score: number | null | undefined): { full: number; half: boolean; empty: number } {
  if (score == null) return { full: 0, half: false, empty: 5 };
  const v = Math.max(0, Math.min(5, score / 20));
  const full = Math.floor(v);
  const half = v - full >= 0.5;
  return { full, half, empty: 5 - full - (half ? 1 : 0) };
}

/** Where the design came from, in plain words. */
export function familyLabel(family: string | null | undefined): string {
  switch ((family || "").toLowerCase()) {
    case "bambu":
    case "bambu/orca":
    case "orca": return "from a Bambu / Orca design";
    case "prusa": return "from a PrusaSlicer design";
    case "stl": return "a plain model (STL)";
    default: return "a 3D design";
  }
}

/** Verdict → friendly status (no READY/REPAIRABLE jargon). */
export function verdictStatus(verdict: string | null | undefined): { icon: string; label: string; tone: Tone } {
  switch ((verdict || "").toUpperCase()) {
    case "READY": return { icon: "✅", label: "Ready to print", tone: "ready" };
    case "REPAIRABLE": return { icon: "🛠", label: "Needs a quick fix — we can do it", tone: "repairable" };
    case "CONVERTIBLE": return { icon: "✨", label: "We'll turn this into a print-ready project", tone: "convertible" };
    case "HIGH_RISK": return { icon: "⚠️", label: "Might not print — review needed", tone: "risk" };
    default: return { icon: "•", label: "Checking…", tone: "convertible" };
  }
}

/** "N color" / "N colors", guarding nulls. */
export function colorsLabel(n: number | null | undefined): string | null {
  if (n == null) return null;
  return `${n} color${n === 1 ? "" : "s"}`;
}

export function partsLabel(n: number | null | undefined): string | null {
  if (n == null) return null;
  return `${n} part${n === 1 ? "" : "s"}`;
}
