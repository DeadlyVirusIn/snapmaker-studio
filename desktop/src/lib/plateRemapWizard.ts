// Pure logic + copy for the Plate Color Remap wizard (Commit D). No React here so
// it's unit-testable: validation, the export-gating rule, and the success/failure
// view derivation all live as pure functions over the backend's JSON shapes.

export const COPY = {
  title: "Plate Color Remap",
  subtitle: "Change one plate's filament assignment without touching other plates, meshes, or painted details.",
  safety: "Studio only rewrites the selected plate's object-level extruder assignment. Meshes, painted facets, gold accents, and other plates remain unchanged.",
  success: "Verified export complete. Only the selected plate objects changed; all other plates and model data were preserved.",
  failure: "Export was stopped because verification failed. Your original file was not modified.",
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
