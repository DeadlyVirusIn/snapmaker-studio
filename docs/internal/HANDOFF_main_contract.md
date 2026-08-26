# Handoff — unreleased work on `main` after v0.8.0, eighth instalment

Written 2026-08-26. **Nothing here is released.** Supersedes
`HANDOFF_main_reachability.md`; read `HANDOFF_v0.8.0.md` for the released product.

## Exact state

| | |
|---|---|
| Current stable release | **v0.8.0**, published, latest, untouched |
| Release tag | `v0.8.0` → commit `e12bc59` |
| Working tree | clean |
| Release evidence | `docs/internal/evidence/0.8.0.json` unchanged; no snapshot edited |

## Current verification on `main`

Backend **1731 passed / 4 skipped** · desktop **335** · `u1convert selfcheck`
**27/27** · `tsc --noEmit` clean · `cargo check` clean · production build clean.

**Not run against `main`:** installed-app acceptance and the real-U1 hardware
harness. `main` is **not hardware verified**, and there is **no release**.

## Start here

```
cd "D:/STL Files/snapmaker-studio"
git status --short                       # expect clean
git rev-parse HEAD origin/main           # expect the two to match
cd backend && py -m pytest -q            # expect 1731 passed, 4 skipped
```

Python is `py`. Backend tests run from `backend/`; desktop gates are
`npm run test`, `npx tsc --noEmit` and `npm run build` from `desktop/`, and
`cargo check` from `desktop/src-tauri`.

## What this instalment settled

The measurement record is in `docs/internal/PRUSA_SEMANTICS.md` under *The two
package gates* and *What a prepared U1 project should state at all*. The rule for
the template is in `backend/snapstudio_core/data/templates/PROVENANCE.md`.

### The two package gates

`[Content_Types].xml` is **ignored** — removed, stripped, mistyped and malformed
all opened as full projects. `_rels/.rels` is **required**, down to the
relationship `Type` URI: removed, mis-targeted, mis-typed and malformed were all
refused outright with *"Snapmaker Orca error"* and nothing loaded, not even the
geometry.

### The printer gets its own declaration entry

`different_settings_to_system`'s **last** entry is the printer's. `nozzle_type`
undeclared came back reset to the preset's value; declared in that entry it was
kept — and sentinels injected into `machine_start_gcode` and `machine_end_gcode`
survived into the exported G-code. So the printer entry decides what the machine
runs.

### Eight template values that had never reached a print

Of 549 keys, measured against both supported builds' effective presets: 274 equal
the preset, 264 have no preset that defines them, 11 genuinely differ. Two of the
eleven are the project naming its presets and one was fixed last instalment. The
other eight had no owning feature and, being undeclared, Orca replaced every one
on load — including the machine's own start and end G-code, of which Studio was
shipping a five-week-old snapshot. Removed. Template 549 → 541.

### The Prusa carry was never reaching the slicer either

`prusa.CARRIED` translates five process values from the source so a project
sliced at 0.15 mm with four walls does not arrive at 0.2 mm with two. The
starter-profile path wrote all five and declared none. Same defect as the
compatibility fixes, in the one path last instalment did not look at. Declared
now.

## Four fixtures prepared and not yet run

The desktop was in continuous use for the second half of this instalment. The
harness refuses to take the foreground from a window this session does not own,
so it declined rather than typing into the user's browser — which is the correct
behaviour and is why these are outstanding:

| fixture | what it would confirm |
|---|---|
| `N0_prusa_carry_undeclared` / `N1_prusa_carry_declared` | the source-carry fix, end to end |
| `M01_machine_gcode_undeclared` | an undeclared machine G-code sentinel is replaced |
| `F1_everything_minimal` | full-feature round-trip and the full-vs-minimal slice comparison |

**Nothing above depends on them.** Each mechanism they would confirm was measured
in both directions on other files — the declared/undeclared pair, and the
printer-entry pair. They are named so the next session runs them rather than
assuming, and they live in the session scratchpad, so rebuilding is the first
step. `classify_template.py` and `presets.py` in that scratchpad rebuild the
whole audit in a minute.

**Run them when the desktop is idle.** Check `Get-ForegroundOwner` first; if
anything but Orca owns the foreground, wait.

## Where the code is

- `backend/snapstudio_core/preset_deviation.py` — `PRINTER`, `PRINTER_KEYS`, and
  the three-way split.
- `backend/snapstudio_core/convert.py` — the starter-profile path declares what
  it carries.
- `backend/snapstudio_core/data/templates/PROVENANCE.md` — which group every
  template key belongs to, and each group's rule.
- `backend/snapstudio_core/data/templates/u1_base_project_settings.json` — 541.
- `backend/tests/test_template_provenance.py` — 7 tests, including one that fails
  if any module starts reading Orca's shipped preset files.
- `backend/snapstudio_core/target_reachability.py` — the two package gates.

## Things that will bite

Everything under this heading in the previous handoffs still applies. Added:

- **The template is not the output.** `set_filament_block` rewrites every
  per-filament array at prepare time, so the template appeared to differ from the
  presets in 99 places and the shipping output differs in 11. Classify the
  prepared project, never the template.
- **Resolve preset inheritance before comparing.** A child preset JSON holds a
  handful of keys; the effective value comes from a four-deep chain. Comparing
  against the child alone says almost everything "has no preset equivalent".
- **A leaf preset can carry junk.** The resolver picked up
  `printer_settings_id: "MyToolChanger 0.4 nozzle - Copy"` from a shipped file.
  Presets are evidence, not truth — read the value, then ask whether it makes
  sense.
- **The user's desktop is not yours.** GUI automation competes with whoever is
  using the machine, and losing that competition is the correct outcome. Build
  the fixtures, check the foreground, and say plainly what you did not run.

## Backlog, reranked

1. **Run the four prepared fixtures** when the desktop is idle. Half an hour.
2. **The 274 restated preset defaults.** They are inherited in practice already,
   so removing them changes nothing measurable — but that is an argument for
   leaving them alone as much as for cutting them, and each removal group needs
   its own round-trip and slice comparison. Worth doing only if the template's
   size is causing a real problem.
3. **Second material provider** — Spoolman is still the only implementation.
4. **Individual per-object placement**, if the product ever wants it.
5. **OBJ/GLB input** — unchanged, still last.

## Release policy from here

Unchanged. No release until a convergence sprint that re-runs, against the
**final** built installer: backend, desktop, selfcheck, installed acceptance, the
v0.8.0 → next in-place upgrade, and the real-U1 hardware harness. The next
release is a **minor** — v0.9.0, not v0.8.1.
