# Handoff — unreleased work on `main` after v0.8.0, seventh instalment

Written 2026-08-26. **Nothing here is released.** Supersedes
`HANDOFF_main_overrides.md`; read `HANDOFF_v0.8.0.md` for the released product.

## Exact state

| | |
|---|---|
| Current stable release | **v0.8.0**, published, latest, untouched |
| Release tag | `v0.8.0` → commit `e12bc59` |
| Working tree | clean, and `main` matches `origin/main` |
| Release evidence | `docs/internal/evidence/0.8.0.json` unchanged; no snapshot edited |

The previous instalment's work had never been pushed. It was fast-forwarded to
`origin/main` at the start of this one, after checking `origin/main` was an
ancestor of local `HEAD`. No force, no reset, no rebase.

## Current verification on `main`

Backend **1718 passed / 4 skipped** · desktop **335** · `u1convert selfcheck`
**27/27** · `tsc --noEmit` clean · `cargo check` clean · production build clean.

**Not run against `main`:** installed-app acceptance and the real-U1 hardware
harness. `main` is **not hardware verified**, and there is **no release**.

## Start here

```
cd "D:/STL Files/snapmaker-studio"
git status --short                       # expect clean
git rev-parse HEAD origin/main           # expect the two to match
cd backend && py -m pytest -q            # expect 1718 passed, 4 skipped
```

Python is `py` on this machine. Backend tests run from `backend/`; the desktop
gates are `npm run test`, `npx tsc --noEmit` and `npm run build` from `desktop/`,
and `cargo check` from `desktop/src-tauri`. The selfcheck is
`py -c "from u1convert.cli import cli; cli(['selfcheck'])"`.

## What this instalment was for

The previous one found that a prepared copy can state a fact correctly and the
slicer never read it. This one asked that question of every load-bearing fact.
The full measurement record is in `docs/internal/PRUSA_SEMANTICS.md` under
*What Snapmaker Orca reads, and what it only stores*.

### The finding that matters most

**Every Snapmaker Orca compatibility fix Studio applies, and every optimization,
was being discarded by the slicer.**

A project names a process preset and then lists that preset's values inline.
Studio assumed the inline values were the ones used. They are not: Orca resets
any value the project does not **declare** in `different_settings_to_system`.
Read back from a copy Studio itself produced in optimize mode:

| Studio wrote | before | after |
|---|---|---|
| `prime_tower_width` 60 | **30** | 60 |
| `prime_tower_brim_width` 2 | **5** | 2 |
| `brim_type` `no_brim` | **`auto_brim`** | `no_brim` |
| `exclude_object` 1 | **0** | 1 |

`brim_type` and `exclude_object` are the shipping compatibility fixes, applied on
every Prepare in every mode and reported to the user as applied. They had never
worked.

`u1_identity.normalize_presets` blanked the declaration to clear Orca's
"Customized Preset" notice, with a comment saying the customized values
themselves stayed in the project. The notice and the values are the same switch.

### The previous instalment's Application rule was too broad

It said a foreign `Application` makes Orca load geometry only. Measured properly
it needs **two** things at once: a **flat** root model (meshes inline rather than
components into `3D/Objects/`) **and** the case-sensitive substring `PrusaSlicer`
in the value. An invented name, `SuperSlicer`, `Slic3r`, lower-case
`prusaslicer`, an empty value and no value at all are all fine — and the same
`PrusaSlicer-2.9.6` on a component-based root model opens as a full project.

The fix that shipped is unchanged and still correct. Only the explanation was
wrong, and the doc now says so in place.

**The lesson:** a fix that works is not the same as an explanation that holds. A
one-variable test that flips the outcome tells you the variable matters in *that*
file, not that it is the rule.

### A per-object layer height and a prime tower

The last instalment proved `layer_height` reaches the slicer and behaves — on a
single-filament plate. On a multi-filament plate the plate does not slice at all:
*"A prime tower requires that all objects have the same layer height."* So it now
crosses only onto a plate that prints with one filament. Infill and support are
unaffected.

## Where the code is

- `backend/snapstudio_core/preset_deviation.py` — new. The declaration, its
  shape, and why each part of the shape is what it is.
- `backend/snapstudio_core/target_reachability.py` — new. What each fact was
  measured to be in the slicer, with the measurement beside it.
- `backend/snapstudio_core/repair.py` — declares the deviations after every write.
- `backend/snapstudio_core/u1_identity.py` — the corrected comment, and the
  cleanliness gate no longer failing a copy for declaring a real deviation.
- `backend/snapstudio_core/stl_wrap.py` — `filaments_in_use`.
- `backend/snapstudio_core/fidelity.py` — every row carries both answers.
- `desktop/src/lib/fidelity.ts` — `targetNote`, `looksBetterThanItIs`.
- `backend/tests/test_target_reachability.py` — 19 tests.
- Template: `gap_fill_target` was `nowhere` where the preset says `topbottom`.
  Undeclared, so it had never reached a print; it now states what has always been
  used.

## Tooling

The harness lives in a session scratchpad and is gone when that session is. It is
rebuilt from the description in the previous handoff in about twenty minutes.
What this instalment added:

* **`Discard` on Orca's own preset prompt.** Changing a global setting and closing
  brings up *"Closing application: unsaved changes"* with Discard and Save
  buttons. It answers to neither Alt+N nor Escape; the harness finds the Discard
  button by class and title and posts BM_CLICK. Getting this wrong writes a
  preset into the user's Orca, which the harness must never do.
* **Reading the notice before dismissing it.** Orca's load warning is evidence and
  is recorded, but it is never the verdict — the verdict comes from the project
  Orca saved back.

Every run reported a clean audit: no pre-existing slicer, own temporary
directory, own process id, ownership of the foreground proved before every
keystroke and every click, closed cleanly, nothing outside its directory written.

## Things that will bite

Everything under this heading in the previous handoffs still applies. Added:

- **A missing file can look preserved.** Removing `project_settings.config`
  entirely left the printer, the process preset and every value apparently
  intact — because Orca fell back to the presets it already had selected in the
  app. Any test of "was this read from the file" needs a value that is **not** a
  preset default, or it measures the app's state instead of the file's.
- **Orca reorders objects on save.** A comparison keyed on list position reports
  a reshuffle as a total loss. Compare per object, by the object's own name.
- **A fixture that cannot slice proves nothing about slicing.** The
  `prusa-multi-object` cubes are open shells: *"No layers were detected."* The
  prime-tower measurement needed solid geometry before it meant anything.
- **A declaration in the wrong category is silently ignored.** A filament key
  named in the process entry did nothing for it; the same key in the filament
  entries worked. Over-declaring is harmless — Orca drops a name it does not
  know — but mis-categorising is not the same as over-declaring.

## Backlog, reranked

1. **Which values Studio should be stating at all.** The mechanism is settled —
   declared or reset — so the open question is no longer whether a process value
   arrives but whether Studio should be writing 549 of them. Most match the
   preset; the ones that do not are now the interesting list.
2. **`[Content_Types].xml` and the package-level `_rels/.rels`** were not varied
   one at a time. Two more gate cases, an hour.
3. **Second material provider** — Spoolman is still the only implementation.
4. **Individual per-object placement**, if the product ever wants it.
5. **OBJ/GLB input** — unchanged, still last.

## Release policy from here

Unchanged. No release until a convergence sprint that re-runs, against the
**final** built installer: backend, desktop, selfcheck, installed acceptance, the
v0.8.0 → next in-place upgrade, and the real-U1 hardware harness. The next
release is a **minor** — v0.9.0, not v0.8.1.
