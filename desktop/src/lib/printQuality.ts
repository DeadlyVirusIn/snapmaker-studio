// Symptom list for the Print Quality Doctor picker. Ids mirror the backend
// knowledge base (snapstudio_core/print_quality.py). Kept JSX-free for testing.

export interface SymptomOption { id: string; title: string; }

export const QUALITY_SYMPTOMS: SymptomOption[] = [
  { id: "stringing", title: "Stringing / wisps" },
  { id: "ringing", title: "Ringing / ghosting" },
  { id: "layer_shift", title: "Layer shift" },
  { id: "warping", title: "Warping / lifting corners" },
  { id: "bed_adhesion", title: "Won't stick / lets go of the bed" },
  { id: "first_layer", title: "Missing / poor first layer" },
  { id: "blobs", title: "Blobs / zits" },
  { id: "under_extrusion", title: "Under-extrusion" },
  { id: "rough_surface", title: "Rough / inconsistent surface" },
  { id: "bridging", title: "Poor bridging / overhangs" },
  { id: "support_failure", title: "Supports fail or won't separate" },
  { id: "color_bleed", title: "Color bleeding / waste (multi-material)" },
];

export const QUALITY_INTRO =
  "Pick what your print looks like. Studio shows likely causes and safe first " +
  "checks — advisory only. It never changes your settings or g-code, and never " +
  "tells you to ignore a bad slice preview.";
