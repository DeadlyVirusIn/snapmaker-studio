# Prusa XL Deep Audit (research — no code)

**Date:** 2026-06-18 · **Fixtures:** `Liberty Eagle_Prusa XL Plate1.3mf` (42 MB) +
`Plate2.3mf` (92 MB), real user PrusaSlicer projects. **Research only.**

## What a Prusa XL project actually contains
Extracted from the fixtures (not assumed):

| Part | Format | Role |
|---|---|---|
| `3D/3dmodel.model` | 3MF XML | **all** geometry in one file (213 MB uncompressed); Bambu/Orca split per-object under `3D/Objects/` |
| `Metadata/Slic3r_PE.config` | **INI** (`key = value`) | print + filament + printer settings (380 keys) — *not* JSON |
| `Metadata/Slic3r_PE_model.config` | XML | per-object/volume metadata: name, **`extruder`** assignment, source-file provenance, transforms |
| `Metadata/Prusa_Slicer_wipe_tower_information.xml` | XML | wipe-tower position per bed |
| `Metadata/thumbnail.png` | PNG | preview |

## Prusa-specific concepts found
- **Printer:** `printer_model = XL5IS`, `printer_settings_id = "Original Prusa XL - 5T Input Shaper 0.4 nozzle"` → **5-toolhead toolchanger**, 360×360 bed, FFF.
- **Toolheads:** `nozzle_diameter = 0.4,0.4,0.4,0.4,0.4` (5 tools), `single_extruder_multi_material = 0` → **5 independent physical heads** (true toolchanger, not an AMS/MMU on one nozzle).
- **Filaments:** 5× `filament_settings_id` ("Sunlu PLA+ 2.0 @XL - Copy"), `filament_type = PLA;PLA;PLA;PLA;PLA`, `filament_colour = 5× #FF8000`. `extruder_colour` = 5 distinct slot colors.
- **Per-object tool mapping:** `Slic3r_PE_model.config` → `<object … key="extruder" value="2">` — each object/volume assigned to a specific tool.
- **Process:** `print_settings_id = "0.20mm SPEED @XLIS 0.4 - Copy"`, `support_material = 1`, `wipe_tower = 1`. Note "- Copy" suffix → **customized presets** (same class of trigger as the Clean Import bug).
- **Multi-plate:** two `.3mf` plate files; wipe-tower info lists `bed_idx 0` and `1`.
- **Provenance:** per-object `source_file = "Liberty Eagle BBL.3mf"` → this design originated as a **Bambu** project, imported into Prusa. (Makers move designs across all three ecosystems — exactly Studio's thesis.)

## Comparison

| Dimension | Prusa XL | Snapmaker U1 | Current Studio engine |
|---|---|---|---|
| Config format | INI (`Slic3r_PE.config`) | JSON (`project_settings.config`) | parses **Bambu/Orca JSON only** |
| Geometry layout | one big `3dmodel.model` | Bambu-style objects | wrap preserves geometry verbatim ✅ |
| Toolheads | **5** | **4** | n/a (settings dropped) |
| Multi-material model | true 5-tool toolchanger, per-object `extruder` | 4 toolheads | not mapped |
| Process settings | Prusa keys (speed/IS profiles) | U1 keys | dropped |
| Today's result | — | — | **geometry-only wrap** → clean U1 *blob*, **all tool/color/support intent lost** |

**Key gap:** Studio detects "no Bambu `project_settings.config`" → routes Prusa to
`wrap_geometry_3mf`, producing a *clean but single-color* U1 project. Geometry and
print-readiness survive; **multi-material intent does not.**

## Compatibility matrix
| Concept | Easy | Difficult | Impossible (today) |
|---|---|---|---|
| Mesh / geometry | ✅ preserved verbatim | | |
| Bed fit (360 vs U1 bed) | | ⚠ rescale/reposition check | |
| ≤4 colors, per-object tool map | | ⚠ parse INI + remap tools → U1 4 heads | |
| **5 colors → 4 toolheads** | | | ❌ 1:1 impossible — must merge/drop a color |
| Filament type (PLA→PLA) | ✅ trivial | | |
| Support settings | | ⚠ map Prusa→U1 support params | |
| Wipe tower | | ⚠ U1 purge model differs | |
| Process profile (speed/IS "- Copy") | | ⚠ no direct key map; use U1 stock + preserve geometry | |
| Multi-plate project | | ⚠ choose/scope a plate | |

## Risks
- **Silent multi-material loss** — today a 5-color Prusa design becomes a 1-color U1 blob with no warning. Worst kind of failure (looks fine, prints wrong).
- **5>4 toolheads** — a hard physical limit; any honest Prusa support must surface "merge/choose colors," not silently drop.
- **INI parser needed** — Prusa config is INI, not JSON; a new `prusa` adapter must parse `Slic3r_PE.config` + the model-config XML.
- **Memory** — 213 MB single mesh; streaming/limits matter.
- **Customized presets ("- Copy")** — same Clean-Import trigger class; the new validator gate already guards U1 output.

## Opportunities
- A **Prusa adapter** that reads tool assignments and maps per-object `extruder` → U1 toolheads when colors ≤ 4, preserving multi-material intent (the real differentiator vs "geometry blob").
- A **"5 colors → 4 toolheads" UX** (choose what to merge) — turns an impossible 1:1 into a guided, honest decision; novice-friendly and unique.
- This is the concrete forcing function for the **canonical project model** (Sprint 2): Prusa proves Studio needs a printer-agnostic internal representation, not Bambu-shaped assumptions.

## Verdict — what it takes to "truly support Prusa"
1. **Detect** Prusa 3MF (presence of `Slic3r_PE.config`) as a first-class source family (today it's lumped into "geometry-only").
2. **Parse** Prusa INI + model-config into Studio's canonical model (objects, per-object tool, filament list, process intent).
3. **Map** to U1: colors/tools (with the ≤4 constraint + merge UX), filament types, support, bed fit.
4. **Validate** (existing U1 gate) + **report** what was preserved vs remapped vs dropped.
Geometry support is essentially free today; **multi-material fidelity is the work**, and it's the same work that unlocks every ecosystem (Sprint 2).
