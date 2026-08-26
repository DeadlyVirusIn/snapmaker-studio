# Handoff — unreleased work on `main` after v0.8.0, second instalment

> **Superseded by `HANDOFF_main_04f7910.md`.** Two of the things this document
> states have since been measured differently: a slot above four is dropped
> because of the *declared filament count*, not the four toolheads, and
> translating the paint dialect is only half of what painting needs. Read this
> for how the round-trip method was arrived at, not for the current state.

Written 2026-08-25. **Nothing here is released.** Supersedes
`HANDOFF_main_2b06ed6.md`, which describes the state one sprint earlier; read
`HANDOFF_v0.8.0.md` for the released product.

## Exact state

| | |
|---|---|
| Current stable release | **v0.8.0**, published, latest, untouched |
| Release tag | `v0.8.0` → commit `e12bc59` |
| `main` HEAD | **`e418dc0`** |
| Working tree | clean |
| Release evidence | `docs/internal/evidence/0.8.0.json` unchanged; no snapshot edited |

Commits on `main` since the previous handoff:

```
e418dc0 fix(fidelity): "preserved" now says what the slicer will do with it
1cb5d13 docs(truth): what Orca did, read out of the file Orca wrote
1828b53 feat(prepare): a modifier crosses as a modifier, not as plastic
e8b09b1 style(multipart): one newline per line
6d986a1 docs(internal): handoff for the unreleased work on main
```

## Current verification on `main`

Backend **1509 passed / 4 skipped** · desktop **321** · `u1convert selfcheck`
**27/27** · `tsc --noEmit` clean · `cargo check` clean · production build clean.

**Not run against `main`:** installed-app acceptance and the real-U1 hardware
harness. Those were last run against the v0.8.0 final installer (34/34 and 39/39).
`main` has changed runtime code since, so **`main` is not hardware verified** and
those numbers must not be cited for it.

## The evidence gap is closed, and the method is reusable

The previous sprint could say only "Snapmaker Orca opens the prepared multi-part
project and recognises it as a U1 project". It can now say what Orca *understood*,
because Orca was made to write it down.

**The method.** Studio starts its own Orca on a project — never touching one
already running — waits for it to load, drives **Save Project As** through the
file dialog, and reads the archive Orca saved. Where the question is about
printing rather than about words, the plate is sliced first (Ctrl+R) and the
footprint Orca records in `Metadata/plate_1.json` is read back.

**Why the save and not the list.** Orca's object list is custom-drawn: neither the
UIA control view nor the raw view exposes a row, at any depth, so there is nothing
to read there. The list itself *is* reachable by mouse — the previous sprint's
synthetic click failed for a duller reason than the control being unreachable. The
script was DPI-unaware, so Windows handed it a virtualised 2560-wide desktop while
the screen is 3840 at 150%, and its coordinates landed two thirds of the way to
the target. Declaring per-monitor DPI awareness first fixed it. But a photograph
of a list is not a value, which is why every claim below comes from a file.

**What did not work, for the next person:** invoking a wxWidgets context-menu item
through UIA reports success and does nothing, and a synthetic click on one does
not select it either, so authoring a modifier inside Orca was abandoned in favour
of writing candidate files and reading what came back. Typing a long path into the
save dialog races its autocomplete and loses characters — paste it. `GetWindowText`
on that dialog's filename field returns empty across the process boundary; UIA's
value pattern reads it correctly.

## What Orca was measured doing

Full detail in `docs/internal/PRUSA_SEMANTICS.md`. The headlines:

- **Two parts, one object, and filament 2**: the prepared multi-part project came
  back from Orca as one composite object with two components, both part digests
  identical to what Studio wrote, part 1 on filament 2, the object's own
  assignment still unassigned.
- **Filament 5 did not survive.** The U1 profile configures four filaments and a
  slot above that is discarded to unassigned rather than clamped. Isolated by
  changing one number: parts on 2 and 4 both survive exactly. Studio still writes
  5, because the source says 5.
- **The four helper role words are real**: `modifier_part`, `negative_part`,
  `support_blocker`, `support_enforcer` all round-trip, and an invented word comes
  back rewritten to `normal_part`. That control is what makes the other rows
  evidence rather than pass-through.
- **They do not print**: two cubes that do not touch, sliced; 500 mm² of plate
  with the second cube as a `normal_part`, 400 mm² as any of the four, plate
  thumbnails byte-identical across the four.
- **Painting in PrusaSlicer's dialect does not reach Orca at all**: 8 painted
  facets in, 0 out, because Orca reads `paint_color`.

## What changed in Studio

**Helper volumes cross.** A modifier, a negative volume, a support enforcer and a
support blocker each become their own part with the word Orca uses, over geometry
typed `other`. A helper part states no filament — it prints nothing, and a genuine
Orca project states none on any of its eight modifier parts either.

**The writer will not invent a role.** `part_records`, `objects_model_xml` and
`object_type_for` raise on a role with no proven target meaning instead of falling
back to `normal_part`. An unrecognised source role still declines the split, so
the object crosses whole and the audit names the consequence.

**The old behaviour is described properly.** "Modifier not carried" hid what
actually happened: the volume's facets stayed inside the single prepared mesh, so
the geometry crossed as printable solid and Orca printed it. That is what the
fidelity row says now, for the roles that still cannot be carried.

**Three things the audit could not see:**

- the geometry row counted only the root model, so a multi-part copy looked like
  every facet had vanished and an intact copy was reported *unverified*; it counts
  the object files the meshes moved into now;
- a new row re-cuts the source's volume ranges and compares each part's shape with
  the volume it came from, facet by facet in winding order;
- the role row asked whether a role appeared *anywhere* in the copy, which passes a
  file where two parts swapped roles — the modifier printing and the solid gone. It
  compares position now.

**Two "preserved" rows now say what happens next**: a filament above the profile's
count, and painting in a dialect the target does not read. Both are still
`preserved_exact` — they are true of the two files — with a reason that names what
Orca does and what to do about it.

**The validator** checks that a part's role and the geometry under it agree, and
that a role word Studio has not proven is a problem rather than a detail.

## Backlog, reranked

1. **Translate the paint dialect on the way out.** Measured: painting written as
   `slic3rpe:mmu_segmentation` reaches Snapmaker Orca as nothing. Studio already
   reads both dialects (`painted_color.py` has the attribute names and the version
   metadata for each); nothing writes the target's. This is the largest known
   silent loss in the crossing and it now has a measurement behind it.
2. **Run the structural validator on Studio's own output.** `multipart.validate_archive`
   exists, catches twelve corruptions, and is called only from tests. Nothing in the
   prepare path runs it, so Snapmaker Orca would still be the first thing to notice.
3. **The prepared copy lands at the plate corner.** The fixture crosses at build
   transform `10 10 10`, so a 20 mm cube occupies 0–20 in x and y and Orca's object
   list files it under **Outside** with a warning. Not introduced by the multi-part
   work — the transform is the same on both paths — but a project that opens
   "outside the plate" is a poor first impression and worth its own look.
4. **Second material provider** — Spoolman is still the only implementation.
5. **Per-object overrides** — still **category D, not established**. The genuine
   Orca projects in the fixtures carry only `name` and `extruder` at object level.
   The round-trip harness in this sprint is exactly how to settle it: write a
   candidate `layer_height` on a part, hand it to Orca, read what comes back, and
   use an invented key as the control.
6. **OBJ/GLB input** — unchanged, still last.

## Release policy from here

No release until a convergence sprint that re-runs, against the **final** built
installer: backend, desktop, selfcheck, installed acceptance, the v0.8.0 → next
in-place upgrade, and the real-U1 hardware harness. `main` carries user-facing
capability, so the next release is a **minor** — v0.9.0, not v0.8.1.

## Things that will bite

Everything in `HANDOFF_main_2b06ed6.md` under this heading still applies. Added:

- **Declare per-monitor DPI awareness before touching any window API.** A
  DPI-unaware process is shown a virtualised desktop, so a screenshot, a UIA
  rectangle and a cursor position can each be in a different coordinate system.
  That is what made the previous sprint's click miss.
- **A menu item is not clickable through UIA.** Its Invoke pattern reports success
  and does nothing.
- **Orca overwrites the file it was opened from** if a save is confirmed with the
  default filename. Keep a pristine copy, or mark it read-only, and always save to
  a fresh path.
- **A background script cannot take the foreground** without attaching to the
  foreground window's input thread first — and another application can take it back
  mid-run, which is why every keystroke is gated on our own process still owning it.
- **Splitting a 6-facet half of a cube gives an open shell.** Fine for structure
  and digests, unreliable for slicing; build closed solids for anything that must
  be sliced.
