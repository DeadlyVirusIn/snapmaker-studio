// Symptom list for the First Layer Doctor picker. Ids mirror the backend
// knowledge base (snapstudio_core/first_layer_doctor.py). JSX-free for tests.

export interface SymptomOption { id: string; title: string; }

export const FIRST_LAYER_SYMPTOMS: SymptomOption[] = [
  { id: "not_stick", title: "First layer doesn't stick" },
  { id: "nozzle_too_high", title: "Lines separated / round (nozzle too high)" },
  { id: "nozzle_too_low", title: "Lines transparent / scraped (nozzle too low)" },
  { id: "wrinkles", title: "Wrinkles or waves" },
  { id: "gaps", title: "Gaps between lines" },
  { id: "corners_lifting", title: "Corners lifting / early warping" },
  { id: "blob_drag", title: "Blob dragging through the layer" },
  { id: "area_specific", title: "Only in one area of the plate" },
  { id: "toolhead_specific", title: "Only with one toolhead" },
  { id: "breaks_loose", title: "Tall / small-footprint breaks loose" },
];

export const FIRST_LAYER_INTRO =
  "Fix the first layer before wasting filament. Pick what you see — Studio shows " +
  "likely causes and safe first checks (beginner steps first, advanced marked). " +
  "Advisory only: Studio never changes your printer config, slicer settings or " +
  "g-code, and never tells you to ignore a bad first layer.";

/** Advanced checks are tagged with a leading "(advanced)" by the backend. */
export function isAdvanced(text: string): boolean {
  return text.trim().toLowerCase().startsWith("(advanced)");
}
