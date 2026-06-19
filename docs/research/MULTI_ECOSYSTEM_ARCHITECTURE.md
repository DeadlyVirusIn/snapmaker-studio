# Multi-Ecosystem Architecture (research — no code)

**Date:** 2026-06-18 · **Goal:** define Studio's printer-agnostic canonical project
model so "any ecosystem in, any printer out" stops being Bambu-shaped assumptions.

## The four ecosystems (observed this project)
| | Bambu | Orca | Prusa | Snapmaker U1 |
|---|---|---|---|---|
| Container | 3MF (OPC zip) | 3MF | 3MF | 3MF |
| Settings format | JSON `project_settings.config` | JSON (Orca = Bambu fork) | **INI** `Slic3r_PE.config` | JSON (Bambu-derived) |
| Model config | `model_settings.config` (objects→extruder, plates) | same | `Slic3r_PE_model.config` (XML) | `model_settings.config` |
| Geometry | `3D/Objects/*.model` (split) | split | one `3D/3dmodel.model` | split |
| Multi-material | AMS (1 nozzle, N filaments) | AMS/MMU | toolchanger (N heads) **or** MMU | **4 toolheads** |
| Identity keys | `printer_settings_id`, `*_settings_id`, `version` | same | `printer_settings_id`, INI ids | U1 stock ids |
| "Customized" marker | `different_settings_to_system` | same | "- Copy" preset names | (must be empty) |
| Print sequence | `print_sequence` by layer/object | same | `complete_objects` | by layer |
| Firmware/runtime | cloud + Bambu MQTT | (none — slicer) | PrusaLink/Connect | **open Klipper/Moonraker** |

## What is common (the canonical core)
Across all four, a "project" decomposes into the same printer-agnostic concepts:
- **Geometry**: a set of objects → volumes → meshes, with transforms (verbatim, never reinterpreted).
- **Layout**: objects placed on one or more **plates/beds**, with positions.
- **Materials**: an ordered list of materials (type, color, vendor) — *logical colors*, independent of how a machine realizes them.
- **Tool/color assignment**: per-object (and per-volume/face for painting) → a material index.
- **Process intent**: layer height, supports on/off, infill, speed *class*, wipe/purge — captured as **intent**, not vendor keys.
- **Provenance**: source ecosystem, source file, creator/license (the Prusa fixture literally carries `source_file`).

## What is printer-specific (the adapter edges)
- **Config dialect** (JSON vs INI; key names; enum values/schema version).
- **Multi-material realization**: AMS-on-one-nozzle vs N-toolhead toolchanger vs 4-head U1 → **capacity + assignment semantics differ**.
- **Identity / preset system** (what makes a file read as "stock" vs "customized").
- **Build volume, nozzle, kinematics, purge model**.
- **Runtime/transport** (cloud, MQTT, Moonraker, PrusaLink).

## Studio's canonical project model (proposed IR)
A single in-memory representation that every importer targets and every exporter renders from:

```
CanonicalProject
├─ provenance        { source_ecosystem, source_file, creator?, license? }
├─ materials[]       { index, type, color, vendor?, name? }     # logical colors
├─ plates[]          { id, objects[] }
│   └─ objects[]     { id, name, transform,
│                       material_index|painted_map,            # color/tool intent
│                       volumes[] { mesh_ref, transform } }
├─ geometry          { meshes (preserved verbatim, ref-counted) }
├─ process_intent    { layer_height, supports, infill, speed_class,
│                       purge/wipe, sequence }                  # intent, not vendor keys
└─ warnings[]        # what couldn't be represented losslessly
```

**Pipeline:** `Importer(ecosystem) → CanonicalProject → Validator → Exporter(target printer)`.
- **Importers**: `bambu` (JSON), `orca` (JSON), `prusa` (INI+XML), `stl/geometry` (mesh-only). Each is the *only* place that knows a vendor dialect.
- **Exporters**: `snapmaker_u1` first; later Bambu/Prusa/others (Printer Profiles). The exporter owns capacity rules (e.g. **U1 = 4 toolheads**) and emits a *clean stock* project for that target.
- **Capacity adapter**: when `materials.count > target.toolheads` (Prusa 5 → U1 4), the canonical model holds all 5; the exporter applies an explicit **merge/remap policy** (with a UX surface) rather than silently dropping — the model never loses information, only the *export* reconciles it and records `warnings[]`.

**Why this shape:** today's engine bakes Bambu assumptions into the U1 path. The IR
inverts that — vendor knowledge lives only at the import/export edges, the middle is
universal, and validation + intelligence + reporting operate on the canonical model
once (not per-vendor). It also makes **Project Intelligence** and **Validation Center**
ecosystem-agnostic by construction.

## Migration from today (non-breaking)
Current engine already does Bambu→U1 well. The IR can be introduced incrementally:
1. Wrap the existing Bambu/Orca repair as a `bambu` importer + `u1` exporter behind the IR (behavior-preserving).
2. Add a `prusa` importer (the Sprint-1 gap) — first real proof the IR isn't Bambu-shaped.
3. Generalize the U1 exporter's capacity/identity logic.
No big-bang rewrite; each step ships working software (matches the project's discipline).

## Decision flagged (architectural, non-binding here)
Adopting a canonical IR is a **direction-setting** choice. This document recommends it
but does **not** implement it — per the research-only rule and the "architecture lock"
stop condition. Build sign-off belongs to the roadmap (Sprint 4) + an explicit go-ahead.

---

## External research integration — Slic3r/PrusaSlicer (concepts only)

Slic3r/PrusaSlicer (GPL/AGPL) was reviewed for format + profile concepts. **Format
knowledge, field/key names, and terminology are reusable; no C++ implementation may be
copied** (3MF reader/writer, preset/inheritance engine, wipe-tower, MMU segmentation).

- **Two-layer 3MF split → the canonical import shape.** Both Prusa and Bambu/Orca split
  a project into (1) a **config-snapshot** file + (2) a **scene/model-tree** file, over a
  shared spec-compliant `3D/3dmodel.model`. They differ only in filename, serialization,
  and key vocabulary:
  - Prusa: `Metadata/Slic3r_PE.config` (flat **INI**) + `Metadata/Slic3r_PE_model.config`
    (**XML** object→volume tree, per-object overrides, painting). Identified by the
    `Slic3r_PE`-prefixed files.
  - Bambu/Orca: `Metadata/project_settings.config` (**JSON**) + `Metadata/model_settings.config`
    (**XML**), plus Bambu/Orca-only `slice_info.config`, per-plate configs, `filament_maps`.
  → The IR adopts this split: a **config layer** + a **scene layer (objects→volumes,
  overrides, painting)**, with per-ecosystem parsers normalizing into one schema. Geometry
  in `3dmodel.model` is the reliable common substrate; config is best-effort mapped (no
  cross-slicer key translation survives a round trip).
- **Three-axis preset model → the IR's settings spine.** Process/Print × Filament × Printer
  is the lingua franca across Prusa/Orca/Bambu — map all three onto it. Keep a
  **system-vs-user** preset split and a `compatible_printers_condition`-style gate so
  U1-only profiles surface only for the U1.
- **Terminology to adopt:** Process (prefer Orca/Bambu's term over "Print settings"),
  Filament, Printer; **config bundle**; **modifier meshes**; **per-object/volume overrides**.
- **Multi-material → per-volume tool index + per-face paint.** Represent MM as an extruder/
  tool index per volume plus optional per-triangle paint segmentation. This maps **cleanly
  to the U1's 4 toolheads** (extruder 0–3 → toolhead 0–3). Carry an import-side purge/flush
  matrix field for fidelity from single-nozzle slicers, but mark it **advisory** — see the
  adaptive-profiles note for why the U1 drops it.

**Use:** the two-layer split, three-axis preset taxonomy + inheritance + compatibility
conditions, the canonical vocabulary, per-volume tool index + face-paint representation.
**Don't use:** GPL/AGPL implementation code; Prusa's lossy expand-at-import inheritance
(Studio should resolve inheritance live); the single-nozzle purge model for U1 toolchanges.

See `U1_ADAPTIVE_PROFILES.md` for how the preset/inheritance concept becomes U1 adaptive
profiles, and `../design/PRINTER_HUB.md` for the OctoPrint/Moonraker monitoring integration.
