# Snapmaker Studio v0.4.0-beta.3

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

## New in beta.3 — clearer navigation
- **Every Doctor is directly reachable from the sidebar** — Project, Printer, First
  Layer, Multi-Material, Cost, Pricing and Profit Doctors each have their own
  destination; no more hunting through the dashboard.
- **"Why Studio?" moved to a secondary/help area** (with Docs/Help and Settings) so
  it supports the story without interrupting the core workflow.
- **Plate Color Remap is grouped next to the Multi-Material Doctor** — the colour
  tools sit together.
- Dashboard Doctor cards are now links to each Doctor; honest landing pages explain
  Doctors that run on an open model (no faked features).

## New in beta.3 — beginner-friendly Plate Color Remap
Plain-language proof, no slicer jargon:
- **What will change** — from→to shown with colour names and swatches, plus the
  count of objects on the selected plate only.
- **What will stay the same** — painted details and gold/yellow accents protected,
  other colours on the plate unchanged, **other plates untouched**, and your
  original file never changed.
- **"Create safe copy — original stays unchanged"** replaces the old technical
  export wording.
- **Verified safe copy** success card lists changed objects, untouched plates,
  painted/mesh unchanged, original unchanged, and the output path.
- A clear note when a visual preview isn't available for a file.
- **Visual 3D plate preview is still deferred** — beta.3 ships a colour/part
  summary fallback; a rendered preview is planned for a later release.

## Plate Color Remap — how it stays safe
Change **one plate's** colour without touching anything else.

- **Verified per-plate remapping.** Targets plates by their plate number
  (`plater_id`), never object order — so the right plate changes, every time.
- **Safety by construction.** Studio changes only the selected plate's default
  colour assignment. **Meshes, painted facets, gold accents, and all other plates
  are never edited.** The original file is never mutated — export always writes a
  new, verified copy.
- **Verification gate.** Every export reopens the output and confirms only the
  intended objects changed and every mesh/paint entry is byte-identical; if any
  check fails, the output is quarantined and the export is reported as failed.
- **Real-file validated (real 9-plate multicolor U1 project).** Plate 4, filament
  6 -> 3, objects 12 and 14 changed; Plate 6 unchanged; gold accents and meshes
  byte-identical; only `model_settings.config` differs; original byte-identical.
  Confirmed by automated tests and a manual in-app UI pass. Real-world validation
  fixtures are not included in the repository because they may be copyrighted or
  commercially licensed.
- **Orca-compatible.** Verified against the OrcaSlicer 3MF reader — editing only
  `model_settings.config` object extruders is safe to open in Snapmaker Orca.

### Known limitation
Large projects (e.g. ~90 MB) can take around **30 seconds** to export, because
Studio re-zips and then re-opens the result to run the full verification gate. The
UI stays responsive and shows progress.

## Compatibility
- **U1 compatibility troubleshooting checklist.** A beginner-friendly guide covers
  the most common community errors — "invalid values found in the 3MF" (out-of-range
  profile settings carried in from foreign/stale project files) and the
  relative-extruder / `G92 E0` layer-gcode warning — with the safest next step for
  each. See [docs/u1-compatibility-troubleshooting.md](u1-compatibility-troubleshooting.md).
- Studio diagnoses and explains; it does not auto-fix these today. A read-only
  Compatibility Doctor is planned (not in this build).

## Windows install (unsigned beta)
This beta installer is **currently unsigned**, so Windows SmartScreen may show
**"Unknown publisher."** That is expected for an unsigned beta. Only download it
from the official GitHub release, and verify the checksum before installing.

```
File:    Snapmaker.Studio_0.4.0-beta.3_x64-setup.exe
Size:    16,028,790 bytes
SHA256:  B1935D66F96E448DB4EF8C34D95294A14FAEAC88BE938A0EADDC8775F5DF15D3
```

Full guidance: [docs/windows-install.md](windows-install.md). Code signing is
planned before any wider public launch (a signed file can still take time to
build SmartScreen reputation).

## Quality
- Backend: 186 automated tests (184 passed, 2 conditional real-fixture tests skip
  when the fixture is absent).
- Frontend: vitest 27/27; TypeScript clean; production build clean.
- Local installer builds, launches, sidecar starts, `/health` 200, 0 orphan
  processes on exit.

_Beta — local-first; nothing leaves your computer._
