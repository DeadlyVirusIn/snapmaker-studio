# U1 Adaptive Profiles — Research Note

> Research only — nothing here is implemented. Concepts are adapted from
> Slic3r/PrusaSlicer and OctoPrint (license note at the end); **no upstream code is
> copied.** Priority is real Snapmaker U1 behavior (Klipper/Moonraker, 4 toolheads),
> with Orca as the slicing handoff.

## Why "adaptive" profiles

Studio prepares a design for the U1 and hands off to Snapmaker Orca to slice. The U1 is
a **4-independent-toolhead** machine on Klipper/Moonraker — not a single-nozzle MMU. A
profile system should therefore *adapt* a small base to the specific design (toolhead
count used, materials present, nozzle/variant) rather than ship one frozen blob per case.

## The preset model to adopt (from Slic3r/Prusa, improved)

Adopt the **three-axis preset taxonomy** as the spine — it is the lingua franca across
Prusa/Orca/Bambu, so mapping is clean:

- **Process** (layer height, perimeters, infill, speeds, supports) — prefer Orca/Bambu's
  term "Process" over Prusa's "Print settings."
- **Filament** (temps, flow, cooling; per material).
- **Printer** (bed size, **G-code flavor = Klipper**, kinematic/firmware limits, toolhead
  count = 4).

Keep two Slic3r concepts and **improve one**:

1. **Inheritance (`inherits`)** — a thin base U1 profile + small override children
   (per material, per nozzle variant, per toolhead). **Improve on Prusa:** resolve
   inheritance **live at runtime**, not lossily expanded at import, so a base tweak
   propagates to children.
2. **Compatibility conditions** (`compatible_printers_condition`-style) — gate filament/
   process profiles so only U1-valid ones surface.
3. **System vs user presets** — shipped U1 packs vs local user edits, kept separate.

## What "adaptive" adds on top

- **Toolhead-aware base.** A base `u1` printer profile declares 4 toolheads; the active
  profile adapts to *how many* the design actually uses (1–4) and which materials are
  assigned, rather than assuming a fixed layout.
- **Material-driven children.** Filament children (PLA/PETG/etc.) attach by inheritance;
  selection is driven by the canonical model's detected materials (see
  `MULTI_ECOSYSTEM_ARCHITECTURE.md`).
- **Variant overrides.** Nozzle size / hardware variant as override children, exactly like
  Prusa's `[printer_model]` variants — without copying the vendor-bundle code.

## Where the U1 diverges from single-nozzle slicers (important)

Prusa's MMU model assumes **one nozzle, many filaments fed sequentially**, which drives a
heavy **purge/flush matrix (N×N)** and a **wipe tower**. The U1's 4 dedicated toolheads
have **no in-nozzle cross-contamination on tool change**, so:

- **Map cleanly:** extruder/volume tool index → toolhead 0–3; per-face paint segmentation →
  per-toolhead assignment. These are the most reusable concepts.
- **Drop / minimize for the U1:** the N×N purge matrix and a large wipe tower are largely
  unnecessary. A U1 process profile should replace them with a **small per-toolhead
  prime/wipe**, not inherit Prusa's purge-volume model. Studio may still *read* an incoming
  purge matrix (for fidelity from single-nozzle sources) but treats it as **advisory**.

This divergence is exactly where U1 adaptive profiles should reflect real hardware rather
than copying slicer defaults.

## Validation tie-in

Adaptive selection must stay honest: the Validation Center already checks bed-fit and
"U1 handles N colors on 4 toolheads." Profile adaptation feeds those checks — e.g. a design
using >4 distinct materials is flagged, not silently remapped.

## Open questions (need a real U1 / Moonraker spike)

- Real Klipper object/section names for the 4 toolheads and any prime/wipe macros.
- Whether Orca's U1 profile already encodes toolhead priming Studio should mirror vs. set.
- Nozzle/variant axis: which variants the U1 actually ships.

These resolve in the read-only Moonraker spike described in `../design/PRINTER_HUB.md`.

## License note

Slic3r is GPLv3; PrusaSlicer / OrcaSlicer / BambuStudio are AGPLv3; OctoPrint is AGPLv3.
**Reusable:** file-format knowledge, preset/inheritance/compatibility *concepts*, the
Process/Filament/Printer vocabulary, and multi-material *representation* concepts.
**Must not copy:** any upstream source — preset/inheritance engine, wipe-tower generator,
MMU segmentation/painting, purge-matrix code. Reimplement independently.
