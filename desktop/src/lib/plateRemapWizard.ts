// Pure logic + copy for the Plate Color Remap wizard (Commit D). No React here so
// it's unit-testable: validation, the export-gating rule, and the success/failure
// view derivation all live as pure functions over the backend's JSON shapes.

export const COPY = {
  title: "Plate Color Remap",
  subtitle: "Change one plate's color safely. Studio makes a verified copy — your original file is never changed.",
  safety: "Studio changes only the selected plate's default color assignment. Meshes, painted facets, gold accents, and other plates stay unchanged — your original file is never modified.",
  success: "Verified safe copy created — only the selected plate's color changed; painted details, other filaments, and all other plates were preserved.",
  failure: "Export was stopped because verification failed. Your original file was not modified.",
  // beginner-facing wording (Problem B)
  questionFrom: "What color on this plate do you want to change?",
  questionTo: "What color should it become?",
  exportCta: "Create safe copy — original stays unchanged",
  confirmTitle: "Review before creating copy",
  proofTitle: "Verified safe copy created",
  previewUnavailable: "Visual preview is not available for this file yet. Studio still verified the file data. Open the exported copy in Orca before printing.",
  paintedUnlabeled: "Painted details are protected by verification, but Studio cannot label their exact colors yet.",
} as const;

// ---- backend JSON shapes (subset we use) ----
export interface PlateFilament { id: number; color?: string | null; type?: string | null; role?: string; }
export interface PlateObject { object_id: number; name?: string | null; base_filament?: number | null; painted_facets?: number; }
export interface PlateInfo {
  ui_number: number | null; name?: string;
  objects: PlateObject[]; filaments_used: PlateFilament[]; painted_accents_present?: boolean;
}
export interface PlateInspect {
  available: boolean; reason?: string;
  filament_palette?: Record<string, { color?: string; type?: string }>;
  plate_count?: number; plates?: PlateInfo[]; warnings?: string[];
}
export interface DryRunChange { object_id: number; name?: string | null; from_filament: number; to_filament: number; painted_facets_preserved?: number; }
export interface PlateDryRun {
  available: boolean; reason?: string; ui_plate?: number;
  change_count?: number; changes?: DryRunChange[];
  untouched_plates?: number[]; warnings?: string[];
  painted_accents_preserved?: boolean; verdict?: string;
}
export interface VerificationCheck { check: string; pass: boolean; detail?: string; }
export interface PlateExport {
  available: boolean; passed: boolean; reason?: string;
  output_path?: string; quarantined?: string | null;
  changed_objects?: DryRunChange[]; untouched_plates?: number[];
  verification?: { passed: boolean; checks: VerificationCheck[] };
  warnings?: string[]; verdict?: string;
}

// ---- wizard selection state ----
export interface Selection {
  path: string | null;
  uiPlate: number | null;
  fromFilament: number | null;
  toFilament: number | null;
}

export const emptySelection: Selection = { path: null, uiPlate: null, fromFilament: null, toFilament: null };

/** Can we run a dry-run? Needs a file, a chosen plate, and from != to. */
export function canDryRun(s: Selection): boolean {
  return !!s.path && s.uiPlate != null && s.fromFilament != null &&
         s.toFilament != null && s.fromFilament !== s.toFilament;
}

/** Hard gate: export is ONLY allowed after a valid, warning-free dry-run that
 *  matches the current selection and actually changes something. */
export function canExport(s: Selection, dr: PlateDryRun | null): boolean {
  if (!dr || !dr.available) return false;
  if ((dr.change_count ?? 0) === 0) return false;
  if (dr.warnings && dr.warnings.length > 0) return false;
  // dry-run must correspond to the current selection
  return dr.ui_plate === s.uiPlate;
}

/** The plate the user picked (by plater_id / ui_number, never object order). */
export function plateByUiNumber(inspect: PlateInspect | null, ui: number | null): PlateInfo | null {
  if (!inspect?.plates || ui == null) return null;
  return inspect.plates.find((p) => p.ui_number === ui) ?? null;
}

/** Filaments the user can pick as the source: those actually used on the plate. */
export function fromOptions(plate: PlateInfo | null): PlateFilament[] {
  return plate?.filaments_used ?? [];
}

/** Target options: the full palette (so the user can pick any loaded slot). */
export function toOptions(inspect: PlateInspect | null): { id: number; color?: string }[] {
  const pal = inspect?.filament_palette ?? {};
  return Object.keys(pal)
    .map((k) => ({ id: Number(k), color: pal[k]?.color }))
    .sort((a, b) => a.id - b.id);
}

export type ExportStatus = "idle" | "inspecting" | "validating" | "exporting" | "complete" | "failed";

/** Derive the user-facing result panel from the backend export response. */
export function exportView(res: PlateExport | null) {
  if (!res) return null;
  if (res.passed) {
    return {
      kind: "success" as const,
      message: COPY.success,
      outputPath: res.output_path ?? null,
      changedObjects: res.changed_objects ?? [],
      untouchedPlates: res.untouched_plates ?? [],
      checks: res.verification?.checks ?? [],
    };
  }
  return {
    kind: "failure" as const,
    message: COPY.failure,
    reason: res.reason ?? "verification failed",
    quarantined: res.quarantined ?? null,
    checks: res.verification?.checks ?? [],
    nextAction: "Your original file is untouched. Re-check the plate and filament selection, then run the preview again.",
  };
}

// ---- beginner-friendly colour naming + summaries (pure; no backend change) ----
// All derived from the existing inspect/dry-run JSON — no writer change, no
// source mutation. Lets the UI answer "will the gold star stay gold?" in plain
// language.

function hexToRgb(hex?: string | null): [number, number, number] | null {
  if (!hex) return null;
  let h = hex.trim().replace(/^#/, "");
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  if (!/^[0-9a-fA-F]{6}$/.test(h)) return null;
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

function rgbToHsl(r: number, g: number, b: number): [number, number, number] {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
  const l = (max + min) / 2;
  const s = d === 0 ? 0 : d / (1 - Math.abs(2 * l - 1));
  let h = 0;
  if (d !== 0) {
    if (max === r) h = ((g - b) / d) % 6;
    else if (max === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h *= 60; if (h < 0) h += 360;
  }
  return [h, s, l];
}

/** Plain-English colour name for a hex, or null if it can't be parsed. */
export function colorName(hex?: string | null): string | null {
  const rgb = hexToRgb(hex);
  if (!rgb) return null;
  const [h, s, l] = rgbToHsl(rgb[0], rgb[1], rgb[2]);
  if (l >= 0.92 && s < 0.1) return "white";
  if (l <= 0.12) return "black";
  if (s < 0.12) return l > 0.6 ? "light gray" : "gray";
  if (h < 15 || h >= 345) return "red";
  if (h < 45) return "orange";
  if (h < 65) return "gold/yellow";
  if (h < 160) return "green";
  if (h < 200) return l > 0.6 ? "light blue" : "teal";
  if (h < 255) return "blue";
  if (h < 290) return "purple";
  return "pink";
}

/** True for gold/yellow accents that must be called out as protected. */
export function isGoldish(hex?: string | null): boolean {
  const rgb = hexToRgb(hex);
  if (!rgb) return false;
  const [h, s, l] = rgbToHsl(rgb[0], rgb[1], rgb[2]);
  return h >= 40 && h <= 65 && s >= 0.3 && l >= 0.4;
}

/** "white slot 6" style label for a filament id using its palette colour. */
export function slotLabel(id: number, color?: string | null): string {
  const name = colorName(color);
  return name ? `${name} slot ${id}` : `slot ${id}`;
}

function paletteColor(inspect: PlateInspect | null, id: number | null): string | null {
  if (!inspect?.filament_palette || id == null) return null;
  return inspect.filament_palette[String(id)]?.color ?? null;
}

export interface PlateSummary { objectCount: number; hasPainted: boolean; sentence: string; }

/** Beginner one-liner about the selected plate. */
export function plateSummary(plate: PlateInfo | null): PlateSummary | null {
  if (!plate) return null;
  const objectCount = plate.objects.length;
  const hasPainted = !!plate.painted_accents_present || plate.objects.some((o) => (o.painted_facets ?? 0) > 0);
  const sentence = `Plate ${plate.ui_number} has ${objectCount} object${objectCount === 1 ? "" : "s"}${hasPainted ? " and painted details" : ""}.`;
  return { objectCount, hasPainted, sentence };
}

export interface ChangeSummary {
  fromId: number; toId: number;
  fromColor: string | null; toColor: string | null;
  fromName: string | null; toName: string | null;
  sentence: string;
}

/** "What will change" — from/to colours in plain language. */
export function changeSummary(inspect: PlateInspect | null, sel: Selection): ChangeSummary | null {
  if (sel.fromFilament == null || sel.toFilament == null) return null;
  const fromColor = paletteColor(inspect, sel.fromFilament);
  const toColor = paletteColor(inspect, sel.toFilament);
  const sentence = `The selected plate's default color will change from ${slotLabel(sel.fromFilament, fromColor)} to ${slotLabel(sel.toFilament, toColor)}.`;
  return {
    fromId: sel.fromFilament, toId: sel.toFilament,
    fromColor, toColor, fromName: colorName(fromColor), toName: colorName(toColor), sentence,
  };
}

export interface StaysSame {
  paintedProtected: boolean;
  protectedColorLabels: string[];
  goldDetected: boolean;
  otherFilaments: { id: number; color: string | null; name: string | null }[];
  otherPlates: number[];
  paintedColorsUnlabeled: boolean;
}

/** "What will stay the same" — derived from inspect + (when present) dry-run. */
export function staysSame(
  inspect: PlateInspect | null, plate: PlateInfo | null,
  sel: Selection, dryRun: PlateDryRun | null,
): StaysSame {
  const hasPainted = !!plate?.painted_accents_present || !!plate?.objects.some((o) => (o.painted_facets ?? 0) > 0);
  const otherFilaments = (plate?.filaments_used ?? [])
    .filter((f) => f.id !== sel.fromFilament)
    .map((f) => ({ id: f.id, color: f.color ?? null, name: colorName(f.color) }));
  const protectedColorLabels = otherFilaments.map((f) => f.name).filter((n): n is string => !!n);
  const goldDetected = (plate?.filaments_used ?? []).some((f) => f.id !== sel.fromFilament && isGoldish(f.color));
  const otherPlates = dryRun?.untouched_plates && dryRun.untouched_plates.length
    ? dryRun.untouched_plates
    : (inspect?.plates ?? []).map((p) => p.ui_number).filter((n): n is number => n != null && n !== plate?.ui_number);
  return {
    paintedProtected: hasPainted,
    protectedColorLabels,
    goldDetected,
    otherFilaments,
    otherPlates,
    paintedColorsUnlabeled: hasPainted && protectedColorLabels.length === 0,
  };
}
