# Handoff — unreleased work on `main` after v0.8.0

> **Superseded by `HANDOFF_main_e418dc0.md`.** `main` has moved on: the Orca
> evidence gap this document calls the next task is closed, and modifier
> volumes are carried. Read this for how the multi-part work was arrived at,
> not for the current state.

Written 2026-08-25 at a context limit, mid-stream. This is the state a fresh
session should start from. **Nothing here is released.**

Read `docs/internal/HANDOFF_v0.8.0.md` first for the released product, then this
for what has happened on `main` since.

## Exact state

| | |
|---|---|
| Current stable release | **v0.8.0**, published, latest, untouched |
| Release tag | `v0.8.0` → commit `e12bc59` |
| `main` HEAD | **`2b06ed6`** — local and `origin/main` identical |
| Working tree | clean, no stashes, one worktree |
| Release evidence | `docs/internal/evidence/0.8.0.json` unchanged; no snapshot edited |

Commits on `main` since the release:

```
2b06ed6 feat(prepare): a source object's parts cross as real parts
4dbdf17 test(prusa): feed the reader what no slicer would write
3e07fdc fix(prusa): unassigned crosses as unassigned, and the parts underneath are audited
33ab818 docs(truth): Studio uploads one thing, and now says so
f41048b docs(internal): the state after v0.8.0
```

## Current verification on `main`

Backend **1480 passed / 4 skipped** · desktop **321** · `u1convert selfcheck`
**27/27** · `tsc` clean · `cargo check` clean · production build clean.

**Not run against `main`:** installed-app acceptance and the real-U1 hardware
harness. Those were last run against the v0.8.0 final installer (34/34 and 39/39).
`main` has changed runtime code since, so **`main` is not hardware verified** and
those numbers must not be cited for it.

## What was done since v0.8.0

### 1. The upload claim was false, and is fixed

Printer Hub genuinely uploads a sliced job to the user's printer. The docs said
"nothing uploaded", "no upload", "never uploads anything anywhere" — false, in the
documents people read *because* they care about privacy.

Corrected across README, CLAUDE.md, SECURITY, PRODUCT_VISION, the judge and fund
documents, the install guide, the release notes and the v0.8.0 handoff. Four app
strings about dragging in a model were scoped to the model ("your file stays on
your computer"). `moonraker.py`'s docstring still opened "read-only Moonraker
client — HARD CONSTRAINT: GET requests only. No uploads" several releases after
the control functions were added below it; it now describes the split it has.

`backend/tests/test_upload_claim_truth.py` guards the absolute form in current
surfaces, leaves historical text alone, and reads a **window** rather than a line
because a wrapped sentence puts the qualifier on the next line.

### 2. PrusaSlicer semantics, measured not assumed

Method: put a candidate model config in a genuine PrusaSlicer project, hand it back
to `prusa-slicer-console.exe --export-3mf`, and read what the slicer wrote. One
variable per run. Ten resulting files live in
`backend/tests/fixtures/prusa-semantics/` with a manifest the suite re-hashes.

Full findings: **`docs/internal/PRUSA_SEMANTICS.md`** — read it before touching
this area. Headlines:

- "no assignment" and "explicit slot 1" are **different facts**; PrusaSlicer
  round-trips each faithfully. Snapmaker Orca writes `extruder="0"` for the first.
  Studio wrote slot 1 and the audit called it preserved. Fixed both ends.
- a slot beyond the filament count is **not clamped** by the slicer, so Studio
  must not clamp it either;
- one object with volumes on different filaments is **ordinary and fully
  representable** on both sides;
- volume roles are `ModelPart` / `ParameterModifier` / `NegativeVolume` /
  `SupportEnforcer` / `SupportBlocker`; an unrecognised word is silently promoted
  to `ModelPart` **by PrusaSlicer itself**, turning a modifier into solid plastic.
  Studio does not repeat that.

### 3. Multi-part output is implemented

A source object whose volumes carry facts of their own now crosses as **real
parts**. PrusaSlicer stores volumes as triangle ranges inside one mesh; the
prepared copy splits along those ranges and emits the structure two genuine
Orca-family projects proved:

```
3D/3dmodel.model           one <object> with one <component> per part, zero meshes
3D/Objects/object_1.model  one mesh object per part, ids from 1
3D/_rels/…rels             the object file declared as a relationship
model_settings.config      <part id="N"> per component, each with its extruder
```

`part id` == component `objectid` == object id in the Objects file. That identity
is what makes the metadata describe the geometry rather than decorate it.

Proved on the fixture with filaments 2 and 5: 12 triangles in and out, 6 per part,
none duplicated; the parts **recombine to a digest identical** to the source solid,
facet by facet in winding order; the two part digests differ; slot 5 not clamped;
object slot stays `0`; all 8 painted facets survive with identical values, 6 and 2
across the parts. Fidelity's `volume_filament` row flips to `preserved_exact`.

New code: `backend/snapstudio_core/multipart.py` (splitter, digests, emitters,
structural validator) and `_try_multipart` in `stl_wrap.py`.

The split is **narrow on purpose**: one source object, one mesh, volumes as ranges.
Anything else declines and the object crosses whole — always safe, because the
audit still reports what could not be carried.

## The one open gap, and it is the next task

**Snapmaker Orca 2.3.5 opened the prepared multi-part project** with no corruption
warning, recognised the Snapmaker U1 printer, four nozzles and the U1 process
profile, and titled the window with the project name.

**Its per-object part list was never read.** A synthetic mouse click would not land
on the Process → "Objects" chip. So the honest evidence level is:

> loads cleanly and is recognised as a U1 project

and **not**

> Orca shows two parts on filaments 2 and 5

Do not blur those. A GUI-automation limitation is not a claim about file semantics.

## Next sprint — ready-to-paste prompt

```
SNAPMAKER STUDIO — ORCA PART-LIST VERIFICATION + MODIFIER CARRY

Read: docs/internal/HANDOFF_main_2b06ed6.md, docs/internal/PRUSA_SEMANTICS.md,
backend/snapstudio_core/multipart.py, backend/tests/test_multipart_output.py

State: main = 2b06ed6. v0.8.0 published, untouched. NO RELEASE this sprint.

Objective 1 — close the evidence gap. Orca opens the multi-part file and
recognises it as a U1 project, but its per-object part list was never read.
In order of preference:
 (a) drive the object list via UI Automation (UIA), not synthetic mouse events —
     the synthetic click is why it failed;
 (b) get Orca to save or export the project and read the saved file;
 (c) if both are blocked, document the exact limitation and stop. Do not turn a
     GUI limitation into a claim about file semantics.

Objective 2 (only if 1 succeeds) — carry modifier volumes. The target
representation is proven: subtype="modifier_part" in model_settings plus
type="other" on the object in the Objects file, both in orca-pa-line-dual.3mf.
Emit it, prove Orca reads it as a modifier and not as solid geometry, and only
then flip the audit row. Never write an unproven role as normal_part.

Constraints: never force-kill Orca, a slicer, a printer or any user GUI process —
only PIDs this session starts, tracked. Capture a window only while it genuinely
owns the foreground. No private paths, usernames or model names in tracked files.

Phase 0: reconcile state; confirm nothing moved beyond 2b06ed6.
```

## Things that will bite

- **Regex literals keep arriving as literal backspace bytes.** Writing `\b`
  through a heredoc into a Python string collapses it to `\x08`, and the pattern
  then silently matches nothing. It happened four times this session and every
  time a test caught it, not review. Prefer patterns that need no `\b`, and if a
  regex "matches nothing" for no reason, print `repr(pattern)` first.
- **`str.isdigit()` is true for Unicode digits.** `extruder="٣"` became slot 3.
  Slot parsing is ASCII-only and bounded by `assignments.MAX_SLOT` now.
- **Snapmaker Orca's CLI crashes on every project.** Do not retry it. GUI only.
- **Orca renders partially on the secondary mixed-DPI monitor.** Move its window
  to the primary display before capturing, and check it owns the foreground —
  one capture this session caught unrelated windows and had to be deleted.
- **The real U1** answers Moonraker on port 7125 at a LAN address the maintainer
  supplies; `U1.local` does not resolve on this network. The address is a runtime
  argument and must never reach a tracked file.
- A local Spoolman for provider testing:
  `docker run -d --name <own-name> -p 7913:8000 ghcr.io/donkie/spoolman:latest`.
  Stop only containers this session started.

## Backlog after the Orca gap, reranked

1. **Orca part-list verification** — the open gap above.
2. **Modifier carrying** — representation proven, emission not attempted.
3. **Second material provider** — Spoolman is still the only implementation, so
   "generic seam" is one example. Blocked behind the multi-part work by choice.
4. **Per-object overrides** — `layer_height`, `fill_density`, `support_material`
   are all **category D, not established**: the real Orca projects in the fixtures
   carry only `name` and `extruder` at object level, so nothing proves a target
   equivalent. A matching name is not evidence of matching semantics.
5. **OBJ/GLB input** — unchanged, still last.

## Release policy from here

No release until a convergence sprint that re-runs, against the **final** built
installer: backend, desktop, selfcheck, installed acceptance, the
v0.8.0 → next in-place upgrade, and the real-U1 hardware harness. `main` carries
user-facing capability, so the next release is a **minor** — v0.9.0, not v0.8.1.

## Standing rules that bite most often

- Studio never slices, never takes autonomous control of a printer, never sends
  anything off the user's local network, and never modifies an original file.
  Printer Hub *does* transfer a sliced job to the user's own printer on the LAN,
  after they confirm it — say that, do not claim otherwise.
- Never force-kill a slicer, printer or user GUI process. Only PIDs this session
  started.
- No local paths, usernames, hostnames, printer addresses or private model names
  in tracked files or screenshots.
- Unknown stays unknown. Withdraw an unprovable claim rather than patching it.
- Publishing adds an evidence snapshot; it never edits one.
- A development build carrying the previous version string is **not** that
  release. Record the commit, size and hash, and say which it is.
