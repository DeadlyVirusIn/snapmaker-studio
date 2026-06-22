// Pure helpers + copy for the Print Failure Troubleshooter ("Fails even with
// supports"). No React, no I/O. Advisory, known-good-aware: never claims the
// file/profile is wrong.
import type { PrintFailureResult } from "@/api";

export const FAILURE_STAGES = [
  { id: "first_layer", label: "First layer" },
  { id: "supports", label: "Supports" },
  { id: "small_details", label: "Small details" },
  { id: "mid_print", label: "Mid-print" },
  { id: "unknown", label: "Not sure" },
];

export const PRINT_FAILURE_COPY = {
  cooldown: "A low temperature shown after the print stops may be cooldown, not the print temperature.",
  oneChange: "Do not change many settings at once — do one change at a time.",
  silkSwap: "If it printed with one silk PLA but fails with another, start with material and temperature checks.",
  notGuarantee: "This is troubleshooting guidance, not a guarantee of print success.",
  noAutoEdit: "Studio does not auto-edit your slicer settings, printer profile, or g-code.",
};

export const KNOWN_GOOD_MODE = {
  title: "This file may already be printable.",
  points: [
    "Compare what changed.",
    "Start with material, dryness, active print temperature, first layer, support contact, cooling, and toolhead calibration.",
    "Try speed changes only as a troubleshooting pass.",
    "Do one change at a time.",
  ],
};

export const UNKNOWN_MODE = {
  title: "Troubleshoot supports, material, and speed carefully.",
  points: [
    "Supports help, but they do not guarantee success.",
    "Check support contact and first layer.",
    "Silk PLA can need slower troubleshooting settings.",
    "Try one conservative pass before changing many settings.",
  ],
};

export function failureMode(knownGood: boolean | null | undefined) {
  return knownGood ? KNOWN_GOOD_MODE : UNKNOWN_MODE;
}

// Defence-in-depth: the UI must never render blame wording even if a finding
// somehow contained it.
const _BLAME = [/too aggressive/i, /\bbad profile\b/i, /settings are bad/i,
  /\bare wrong\b/i, /\bis wrong\b/i, /will fail/i, /\bunsafe\b/i, /you must slow/i];

export function isBlameFree(r: PrintFailureResult): boolean {
  const blob = JSON.stringify(r).toLowerCase();
  return !_BLAME.some((re) => re.test(blob)) && !blob.includes("guaranteed");
}
