# Handoff — unreleased work on `main` after v0.8.0, sixth instalment

Written 2026-08-26. **Nothing here is released.** Supersedes
`HANDOFF_main_ff1aef2.md`; read `HANDOFF_v0.8.0.md` for the released product.

## Exact state

| | |
|---|---|
| Current stable release | **v0.8.0**, published, latest, untouched |
| Release tag | `v0.8.0` → commit `e12bc59` |
| Working tree | clean |
| Release evidence | `docs/internal/evidence/0.8.0.json` unchanged; no snapshot edited |

The previous handoff said runtime work ended at `ff1aef2`. It does not any more —
this instalment changed the engine, the writers, the audit and the desktop card.

## Current verification on `main`

Backend **1695 passed / 4 skipped** · desktop **327** · `u1convert selfcheck`
**27/27** · `tsc --noEmit` clean · `cargo check` clean · production build clean.

**Not run against `main`:** installed-app acceptance and the real-U1 hardware
harness. `main` is **not hardware verified**, and there is **no release** from
this instalment.

## Start here

```
cd "D:/STL Files/snapmaker-studio"
git status --short                       # expect clean
git rev-parse HEAD origin/main           # expect the two to match
cd backend && py -m pytest -q            # expect 1695 passed, 4 skipped
```

Python is `py` on this machine — there is no `python` on PATH and no virtualenv.
Backend tests run from `backend/`; the desktop gates are `npm run test`,
`npx tsc --noEmit` and `npm run build` from `desktop/`, and `cargo check` from
`desktop/src-tauri`. The selfcheck is
`py -c "from u1convert.cli import cli; cli(['selfcheck'])"`.

## What this instalment settled

**Per-object setting overrides — the last category-D question — are settled.**
Three of them cross; everything else is reported by name and not carried. The full
measurement record is in `docs/internal/PRUSA_SEMANTICS.md` under *Per-object
setting overrides*. In short:

| Source key | Orca's key, on `<object>` | Classification |
|---|---|---|
| `layer_height` | `layer_height` | **exact** |
| `fill_density` | `sparse_infill_density` | **preserved semantic** |
| `support_material` | `enable_support` | **preserved semantic** |

The one thing to carry forward if nothing else is read: **PrusaSlicer's own
`fill_density` and `support_material`, written into an Orca project, are dropped
exactly as an invented key is dropped.** The project Orca saves from any of the
three is byte-identical to the project it saves from a file carrying no setting at
all. A generic "copy every override" path would have produced files that look right
and say nothing to the slicer, and every test would have passed.

**A malformed value costs the object, not the setting.** A non-numeric layer
height, Unicode digits, `enable_support="true"` and `enable_support="2"` each made
Orca open the project **with an empty plate**. `layer_height="0"` and a negative
one **hung Orca on load** — unresponsive, burning CPU, no clean close. So values
are validated before they are written and Prepare fails rather than writing one it
cannot stand behind.

## The bug found on the way, which matters more than the feature

Studio's prepared copy of a project it does not split kept the source's
`<metadata name="Application">PrusaSlicer-2.9.6</metadata>`. Snapmaker Orca 2.3.6
answers that with **"The 3mf is not supported by Snapmaker Orca, loading geometry
data only"** and then ignores `model_settings.config` entirely.

Read back from the project Orca saved: object names replaced by the file's name,
and **an object Studio had written as filament 3 came back as filament 0,
unassigned.** The per-object assignment `assignments.py` exists to protect was
correct in the file and never reached the slicer — and the fidelity audit reported
it preserved, because the audit compares two files and the file *was* right.

Fixed by stating `SnapmakerStudio-u1convert`, which is true of the copy. One value
in the root model changes and nothing else.

**The lesson for the next session:** a fidelity audit comparing two files cannot
see a file the target refuses to read. Anything Studio claims to carry is worth
checking through the slicer at least once, not only through the audit.

## Where the code is

- `backend/snapstudio_core/overrides.py` — new. The evidence-backed allowlist:
  source key, target key, level, value gate, and why each gate exists. Read its
  docstring before changing any of it.
- `backend/snapstudio_core/stl_wrap.py` — `_override_lines`, `_nozzle_mm`,
  `_own_the_root_model`; both settings writers emit the carried values.
- `backend/snapstudio_core/assignments.py` — `_override_rows` compares across the
  rename; `_own_body` stops an object's chunk at `</object>`.
- `backend/snapstudio_core/multipart.py` — the structural validator re-checks every
  object-level setting in the finished archive.
- `backend/snapstudio_core/prusa.py` — the "not carried" panel names the settings
  that stay behind instead of counting them.
- `desktop/src/lib/fidelity.ts` — `objectSettingsLine`, rendered by `FidelityCard`.
- `backend/tests/test_object_overrides.py` — 78 tests.
- `backend/tests/fixtures/orca-object-overrides/` — four files Orca wrote itself,
  with a manifest the suite re-hashes.

## Tooling, and what happened to it

The Orca automation harness and the portable PrusaSlicer live in a session
scratchpad and are gone when that session is. **Neither is in the repository and
neither should be.** Rebuilding both is about an hour, and the methods are
described here and in `PRUSA_SEMANTICS.md`. Their absence is not evidence that
something cannot be measured — the previous handoff said the same thing and it was
right.

What this instalment's harness did that the previous one's did not:

* **Drove Orca's own per-object panel.** Process ▸ Objects, the object in the
  tree, then the Frequent tab. Custom-drawn and invisible to UI Automation, so it
  is clicked at coordinates read off a screenshot. That is how the target's own
  vocabulary was obtained rather than guessed.
* **Exported G-code.** `Ctrl+G` in Orca opens *Save Sliced file as:* and writes a
  `.gcode.3mf` with the G-code inside at `Metadata/plate_1.gcode`. Both slicers
  bracket each object with `; printing object <name> id:N copy K`, so extrusion,
  layer participation and feature type are attributable per object. That is what
  turned slicing from a yes-or-no into a measurement.
* **Watched for a hang.** A value Orca cannot cope with leaves it spinning inside
  the load with a window that never answers. The harness now detects that, reports
  the case as a hang, and terminates only the pid it started itself.

**PrusaSlicer 2.9.6 portable** — `PrusaSlicer-2.9.6.zip` from the project's GitHub
release, sha256 `5AAF22E42F95ACCECFA122D23A835911F289ECC2FF606DB3E83D637DDCC0A209`,
unzipped and run from the scratchpad, never installed. Its CLI slices headlessly:
`prusa-slicer-console.exe --export-gcode --gcode-label-objects=octoprint
--layer-height 0.2 --first-layer-height 0.25 --fill-density 15% --output x.gcode in.3mf`.
Note the CLI defaults are Slic3r's, not a Prusa profile's — 0.3 mm layers and 20%
infill — so a control that does not set them explicitly can accidentally equal the
test.

Every Orca run reported a clean audit: no pre-existing slicer process, own
temporary directory, own process id, ownership of the foreground proved before
every keystroke, closed cleanly, nothing outside its directory written.

## Things that will bite

Everything under this heading in the previous handoffs still applies. Added:

- **A matching key name is not a matching setting, and a surviving key is not a
  recognised one.** Both need a control. The invented key is the whole method.
- **`\d` in a Python regex matches Unicode digits.** A layer-height gate written
  with `\d` accepted `٠.٣` and `float()` turned it into 0.3 — a value no slicer
  wrote. Orca deletes the object rather than reading it. Spell out `[0-9]`. This
  is the second time this exact trap has been hit in this codebase.
- **PrusaSlicer emits `G92 E0` at every layer.** A G-code extrusion parser that
  ignores it silently loses a layer's worth of extrusion per reset and the totals
  stop meaning anything. Orca uses relative E and is unaffected, which is exactly
  why the bug only showed on one side.
- **A `;TYPE:` comment carries across an object bracket.** Without resetting the
  feature at `; printing object`, 40 mm of one object's support was attributed to
  the object that came next.

## Backlog, reranked

1. **Check what else the audit reports preserved but the slicer never sees.** The
   Application-metadata bug is unlikely to be the only fact that is right in the
   file and invisible to Orca. Painting is proved through the slicer; filament
   assignment now is; the rest of `model_settings.config` is not.
2. **Second material provider** — Spoolman is still the only implementation.
3. **Individual per-object placement**, if the product ever wants it.
4. **OBJ/GLB input** — unchanged, still last.

Per-object overrides are off this list.

## Release policy from here

Unchanged. No release until a convergence sprint that re-runs, against the **final**
built installer: backend, desktop, selfcheck, installed acceptance, the
v0.8.0 → next in-place upgrade, and the real-U1 hardware harness. The next release
is a **minor** — v0.9.0, not v0.8.1.
