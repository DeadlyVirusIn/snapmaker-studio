# Handoff — unreleased work on `main` after v0.8.0, fifth instalment

Written 2026-08-26. **Nothing here is released.** Supersedes
`HANDOFF_main_e38e468.md`; read `HANDOFF_v0.8.0.md` for the released product.

## Exact state

| | |
|---|---|
| Current stable release | **v0.8.0**, published, latest, untouched |
| Release tag | `v0.8.0` → commit `e12bc59` |
| `main` HEAD | **`85716a1`** — this document; the runtime work ends at `ff1aef2` |
| Working tree | clean |
| Release evidence | `docs/internal/evidence/0.8.0.json` unchanged; no snapshot edited |

Commits since the previous handoff:

```
85716a1 docs(internal): handoff after the placement work      <- this file
ff1aef2 fix(placement): a modifier off the plate is not an object off the plate
f0b8205 docs(internal): handoff after the volume and multi-object work
```

## Current verification on `main`

Backend **1606 passed / 4 skipped** · desktop **321** · `u1convert selfcheck`
**27/27** · `tsc --noEmit` clean · `cargo check` clean · production build clean.

**Not run against `main`:** installed-app acceptance and the real-U1 hardware
harness. `main` is **not hardware verified**.

## Start here

```
cd "D:/STL Files/snapmaker-studio"
git rev-parse HEAD          # expect 85716a1, and origin/main the same
git status --short           # expect clean
cd backend && py -m pytest -q # expect 1606 passed, 4 skipped
```

Python is `py` on this machine — there is no `python` on PATH and no virtualenv.
Backend tests must be run from `backend/`; the desktop gates are
`npm run test`, `npx tsc --noEmit` and `npm run build` from `desktop/`, and
`cargo check` from `desktop/src-tauri`. The selfcheck is
`py -c "from u1convert.cli import cli; cli(['selfcheck'])"`.

**The next task** is per-object overrides — the last unsettled category-D
question. The method is the round-trip harness below, with an invented key as the
control: a key that survives when nonsense also survives has proved nothing.

**Tooling from the last two instalments lives in a session scratchpad and is
gone when that session is.** Neither is in the repository, and neither should be:

* the Orca automation harness — starts an Orca only when none is running, own
  temporary directory, own process id, ownership proved before every keystroke,
  Save Project As driven through the file dialog, never force-kills, audits the
  machine afterwards;
* PrusaSlicer 2.9.6, portable, fetched from the project's GitHub release and
  verified with `--version`. **It is not installed on this machine.**

Rebuilding either is an hour's work and the methods are described in this
document and in `PRUSA_SEMANTICS.md`. Do not treat their absence as evidence that
something cannot be measured.

## Read this before planning placement work

The previous handoff listed "tell the person when a prepared object is off the U1
bed, and offer an explicit reposition" as the top backlog item. **Most of it was
already shipped**, and the sprint that acted on that line started by building a
parallel implementation before finding out.

Already in the product, from an earlier release:

* `snapstudio_core/plate_placement.py` — the check and the fix;
* `/placement_check` and `/prepare_placed` on the local API, with
  `snapstudio_api/service.py` recording the fix in the ledger;
* `u1convert placement` on the CLI;
* `desktop/src/components/PlacementCard.tsx` — names the object, the edge and
  the millimetres, and offers a button that writes a new copy;
* 28 tests, plus rows in the selfcheck, preflight, and several judge-facing docs.

The lesson is the project's own state-reconciliation rule: **grep the codebase
for the feature before designing it.** A backlog line describes what a previous
session noticed, not what the product lacks.

## What this instalment actually changed

### A helper volume off the plate is not an object off the plate

The shipped check measured each object from *all* its geometry. A modifier cube
400 mm from the plate made Studio report the object 270 mm off it and offer to
move an arrangement that is fine.

Measured against Orca 2.3.5 with a control:

| the second cube is | Orca sliced |
|---|---|
| absent | yes |
| a `normal_part` 400 mm away | **no — the plate did not slice** |
| a `modifier_part` 400 mm away | **yes** |

Orca does not count helper geometry, so neither does Studio. The footprint is
printable parts only.

### The smallest move, not the middle of the plate

`_centering_offset` moved the arrangement to the centre of the bed. A print
arranged half a millimetre off the edge was moved half a metre. The move is now
the point in the fitting interval nearest to not moving at all — smallest,
deterministic, and unchanged across runs. The 0.5 mm edge margin stays: skirt,
brim and prime tower all need room.

### The copy is proved, not only re-checked

Re-running the placement check on the output proves the objects are on the plate
and nothing else. `verify_only_placement_moved` compares the copy with the
original entry by entry — file list, every entry but the root model
byte-identical, the root's geometry and components unchanged, one shared
translation with no rotation, rescale or height change, structure still valid,
painting unchanged — and the copy is deleted rather than handed over if any of
that fails.

### `placement.py`, the geometry underneath

New module: transform composition (twelve-number build items and sixteen-number
part matrices both parsed and checked against each other), footprints followed
through the component graph the multi-object writer produces, containment against
the project's **own printable polygon**, and five states kept apart — `inside`,
`touching_boundary`, `partly_outside`, `fully_outside`, `too_large_to_fit`. An
L-shaped bed in the tests proves the polygon matters; nothing in the U1's own
rectangular outline could.

### The audit keeps two facts apart

Studio preserving a placement exactly and the target being unable to print it
there are different things. Target fit is reported beside the rows rather than as
one of them, so a preserved placement is never counted as a loss. A whole plate
moved together is `preserved_semantic` naming the offset; one object drifting away
from the others is `changed`.

## The Orca before/after

| | Studio | Orca |
|---|---|---|
| the known outside fixture | 1 object outside, left 0.5 / front 1.0 | **would not slice** |
| after `+1.0 mm X, +1.5 mm Y` | every object on the plate | **sliced** — the cube and a wipe tower |
| three objects shifted −60, −50 | 2 outside, one move of +30.5, +21 fits | sliced only the object still on the plate |
| after one move of `+31.0, +21.5` | every object on the plate | one rigid translation, verification passed |

Every run reported a clean automation audit: no pre-existing Orca, own temporary
directory, own process id, closed cleanly, nothing outside its directory written.

## Not done, deliberately

* **Individual per-object moves.** Phase 9 of the sprint brief made it optional
  and rigid translation sufficient. Not implemented, so no UX surface exists for
  it and none is implied.
* **Auto-packing or nesting.** Explicitly out of scope, and it would move an
  arrangement somebody chose.

## Backlog, reranked

1. **Per-object overrides** — still category D, not established. The Orca
   round-trip harness with an invented key as the control is how to settle it.
2. **Second material provider** — Spoolman is still the only implementation.
3. **Individual per-object placement**, if the product ever wants it: the check
   already reports which objects are off the plate, and it needs its own explicit
   user intent and its own audit rows.
4. **OBJ/GLB input** — unchanged, still last.

## Release policy from here

No release until a convergence sprint that re-runs, against the **final** built
installer: backend, desktop, selfcheck, installed acceptance, the v0.8.0 → next
in-place upgrade, and the real-U1 hardware harness. The next release is a
**minor** — v0.9.0, not v0.8.1.

## Things that will bite

Everything under this heading in the previous handoffs still applies. Added:

- **Grep before you build.** `plate_placement`, two API routes, a CLI command and
  a React card already existed for the feature this sprint was asked to add.
- **`grep -rln` through the session's shell has returned 0 matches for text that
  is demonstrably there.** Two searches for "placement" under `desktop/src` came
  back empty while `PlacementCard.tsx` sat in that directory. Use the Grep tool,
  or `ls` the directory, before concluding something does not exist.
- **PrusaSlicer is still not installed on this machine.** The portable 2.9.6 build
  fetched last instalment lives only in a session scratchpad.
