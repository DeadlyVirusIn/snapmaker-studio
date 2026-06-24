# beta.15 implementation checklist (internal) — roadmap items 5,6,7

Branch `beta-15`. From beta.14 (Printer Hub). Commit each item; publish only when all 3 done + tested.

## Item 5 — Plate Color Remap visual preview (frontend only; NO backend/writer change)
- DONE: `plateRemapWizard.ts` → `buildPlatePreview(inspect, plate, sel, dryRun)` returns `PlatePreview` {objects[{id,name,colorHex,colorLabel,painted,paintedCount,protectedAccent,changing,toHex,toLabel}], legend, untouchedPlates, paintedAccentsPresent, swappableCount, changingCount}. All data already in inspect/dry-run.
- TODO: `PlateRemap.tsx` lines ~120-153 — replace the "Colors on this plate" fallback with a 2D plate map: object chips colour-filled by base filament; changing object shows from→to; protected (painted/gold) flagged with Lock; legend source→target + untouched plates + painted-accents preserved. Keep `COPY.previewUnavailable` reworded (no "unavailable"; note 3D render is future). No dead-end when swappableCount===0: still render painted/object map + explanation.
- TODO tests: `plateRemapWizard.test.ts` — buildPlatePreview: base color resolves, changing flagged, gold/painted protected, untouched plates, no-swappable still returns objects, original-not-modified copy intact.

## Item 6 — Print Quality Doctor evidence integration (server-side aggregation; additive)
- Backend `print_quality.py`: 12 symptoms, each {symptom,title,likely_causes,first_checks,orca_paths,hardware_checks,avoid,evidence_needed,disclaimer}.
- Evidence doctors (call with file path): `service.mesh(path)` → overhang{overhang_pct,severe_pct,supports_likely}, stability{tip_risk,margin_mm,height_mm,aspect}, footprint{base_area_mm2,width_x_mm,min_dim_mm}; `service.compatibility_check(path)`/bed_fit → overall_level,findings; `service.insights(path)` → colors,materials[],dimensions_mm,complexity; `service.first_layer(path)` → findings[].
- TODO: new `service.quality_check(symptom, path=None)` — when path given, build `evidence: [{label, level: ok|warn|risk, text, doctor}]` per symptom map:
  - bed_adhesion → mesh.footprint.base_area + stability.margin + first_layer
  - support_failure/fails_even_with_supports → mesh.overhang.supports_likely/severe_pct + stability.tip_risk
  - warping → mesh.footprint.min_dim + stability.aspect/height
  - stringing/under_extrusion/temperature → insights.materials (filament types)
  - color/tool-change → insights.colors vs toolheads
  - first_layer → first_layer.findings + footprint
  - layer_shift/ringing → generic (no strong file signal) → graceful empty
  - Put aggregation in a new `snapstudio_core/quality_evidence.py` (pure-ish; calls mesh/insights). Wrap each doctor call in try/except → evidence optional, never breaks the advisory result.
- `server.py` `/quality_check`: accept optional `path`. `api.ts` `qualityCheck(symptom, path?)`.
- Frontend `PrintQuality.tsx`: file picker (optional) + Evidence panel ("What Studio found" with level badges) before disclaimer. Advisory wording, no guarantees.
- TODO tests: backend `test_quality_evidence.py` — evidence appears for a real fixture per symptom; graceful when no path / doctor fails; no guarantee language. Frontend: evidence render gating.

## Item 7 — File/source ecosystem detection + migration wizard (extend detect; advisory)
- Backend `detect.py`: `detect_source(tm)→SourceInfo{family,application,printer_model,is_u1}`. Detects bambu-family / prusa (Slic3r_PE.config) / cura (Metadata/Cura*) / generic / stl.
- TODO: new `snapstudio_core/source_compatibility.py` → `detect_detailed(path)` returns {source_app, ecosystem, printer_model, readable_settings{}, can_read[], cannot_convert[], risks[], recommended_next_step, is_u1}. Reuse ThreeMF + detect_source + config_io. Per-ecosystem: bambu-family(full read), prusa(INI colors/types/printer), cura(detected, limited read), generic 3MF, STL. Orca==bambu-family (document). Creality → not detected → "unknown source" honest state.
- `service.source_compatibility(path)` + `server.py` `/source_compatibility`. `api.ts` `sourceCompatibility(path)` + type.
- Frontend `lib/sourceWizard.ts` (pure flow) + a "Source Compatibility" card (add to DesignInsights or a small route). States: detect → explain (can_read/cannot_convert) → recommend (U1/Orca) → next step (inspect / prepare safe copy via existing convert / Open in Orca). No full-conversion claims beyond what convert.py already does.
- Fixtures: synthetic `examples/sample_prusa_cube.3mf` (Slic3r_PE.config INI) + `examples/sample_cura_cube.3mf` (Metadata/Cura marker). Build via a tiny script or inline zip in test.
- TODO tests: backend `test_source_detection.py` — STL, generic 3MF, U1/bambu, prusa, cura detection; unknown/creality → honest unknown; no false compatibility claims. Frontend `sourceWizard.test.ts` — copy + recommended step + no false-compat.

## Verify + publish
tsc, vitest, pytest, cargo check, release build, hash, docs (RELEASE_NOTES/README/JUDGE/WHAT_TO_TEST/SCREENSHOTS_BETA15/windows-install), screenshots, commit, merge main, tag v0.4.0-beta.15, gh release --latest, verify.
