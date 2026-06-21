# Snapmaker Studio v0.4.0-beta.2

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

## The Intelligence Layer for Open 3D Printing
Orca slices. Fluidd monitors. **Studio decides.** Before a layer is sliced, Studio
reads your model and your Snapmaker U1 (read-only) and tells you whether it will
print, what it costs, and what to sell it for — one screen, plain language.

### Doctor pillars
- **Project Doctor** — will it fit and print on your U1? Catches out-of-bounds and
  printability problems before Orca does.
- **Printer Doctor** — a 0–100 health score from the U1's own signals.
- **Cost Doctor** — true cost, suggested price, and profit (with Pricing/Profit).

The **Studio Intelligence Report** synthesises these into one verdict; the Doctors
become the supporting evidence.

## New in this release — Plate Color Remap
Change **one plate's** filament assignment without touching anything else.

- **Verified per-plate remapping.** Targets plates by their plate number
  (`plater_id`), never object order — so the right plate changes, every time.
- **Safety by construction.** Studio rewrites only the selected plate's
  object-level extruder assignment in `model_settings.config`. **Meshes, painted
  facets, gold accents, and all other plates are never edited.** The original file
  is never mutated — export always writes a new, verified copy.
- **Verification gate.** Every export reopens the output and confirms only the
  intended objects changed and every mesh/paint entry is byte-identical; if any
  check fails, the output is quarantined and the export is reported as failed.
- **Real-file validated (Freedom Torch).** Plate 4, filament 6 -> 3, objects 12 and
  14 changed; Plate 6 unchanged; gold accents and meshes byte-identical; only
  `model_settings.config` differs; original byte-identical. Confirmed by automated
  tests and a manual in-app UI pass.
- **Orca-compatible.** Verified against the OrcaSlicer 3MF reader — editing only
  `model_settings.config` object extruders is safe to open in Snapmaker Orca.

### Known limitation
Large projects (e.g. ~90 MB) can take around **30 seconds** to export, because
Studio re-zips and then re-opens the result to run the full verification gate. The
UI stays responsive and shows progress.

## Compatibility
- **U1 compatibility troubleshooting checklist.** A new beginner-friendly guide
  covers the most common community errors — "invalid values found in the 3MF"
  (out-of-range profile settings carried in from foreign/stale project files) and
  the relative-extruder / `G92 E0` layer-gcode warning — with the safest next step
  for each. See [docs/u1-compatibility-troubleshooting.md](u1-compatibility-troubleshooting.md).
- Studio diagnoses and explains; it does not auto-fix these today. A read-only
  Compatibility Doctor is planned for a future release (not in this build).

## Quality
- Backend: 186 automated tests passing.
- Frontend: vitest 12/12; TypeScript clean; production build clean.
- Local installer builds, launches, sidecar starts, `/health` 200, 0 orphan
  processes on exit.

_Beta — local-first; nothing leaves your computer._
