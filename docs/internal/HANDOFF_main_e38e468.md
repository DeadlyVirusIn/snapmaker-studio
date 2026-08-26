# Handoff — unreleased work on `main` after v0.8.0, fourth instalment

Written 2026-08-25. **Nothing here is released.** Supersedes
`HANDOFF_main_04f7910.md`; read `HANDOFF_v0.8.0.md` for the released product.

## Exact state

| | |
|---|---|
| Current stable release | **v0.8.0**, published, latest, untouched |
| Release tag | `v0.8.0` → commit `e12bc59` |
| `main` HEAD | **`e38e468`** |
| Working tree | clean |
| Release evidence | `docs/internal/evidence/0.8.0.json` unchanged; no snapshot edited |

Commits since the previous handoff:

```
e38e468 docs(truth): the volume rule, the multi-object shape, and the wipe tower
4396350 feat(prepare): every object crosses in the target's own layout
6ffa280 fix(painted): an unpainted patch prints in its own volume's filament
a684da2 docs(internal): handoff after the capacity and painting measurements
```

## Current verification on `main`

Backend **1577 passed / 4 skipped** · desktop **321** · `u1convert selfcheck`
**27/27** · `tsc --noEmit` clean · `cargo check` clean · production build clean.

**Not run against `main`:** installed-app acceptance and the real-U1 hardware
harness. Those were last run against the v0.8.0 final installer (34/34 and 39/39).
`main` has changed runtime code since, so **`main` is not hardware verified**.

## PrusaSlicer is a tool this work needs, and it was not installed

The `prusa-semantics` fixtures were authored with a portable PrusaSlicer 2.9.6
that is no longer on the machine, and this instalment needed the slicer again to
author new ones. The portable build is downloaded and extracted under the
session's scratchpad — `PrusaSlicer-2.9.6.zip` from the project's GitHub release,
sha256 `5aaf22e4…a209`, unzipped, `prusa-slicer-console.exe --version` verified as
2.9.6. Nothing was installed into the system and no admin was needed. A future
session that needs to author a fixture will have to do the same; the method is
`--export-3mf`, and the scripts that drive it are throwaway.

## What was measured, and what it changed

### A volume's triangle range

| Question | Answer, from PrusaSlicer 2.9.6 |
|---|---|
| Are `firstid`/`lastid` inclusive? | **Yes** — 0 to 5 is six facets |
| Can ranges leave a gap? | **Not from the slicer**: 0–3 and 8–11 came back as 0–3 and 4–7 over an eight-facet mesh |
| Can they overlap? | **Not from the slicer**: 0–7 and 5–11 came back as 0–7 and 8–14 over a fifteen-facet mesh, the shared facets duplicated |
| Reversed, or past the end? | **Refused** — "Found invalid triangle id", no file written |

So a genuine file says which volume owns a facet exactly once. Anything else is
*unknown*, never a sibling's filament.

**The defect that fixed.** An unpainted patch prints in whatever its own volume is
assigned, and Studio answered that once per object — the first volume that stated
a slot answered for every facet. 50 mm² of the two-volume fixture sat under
filament 2 that belongs to filament 5, and the wrong side was the **source**
reading: the prepared copy had been right. Attribution is per volume now, in the
order volume → object → unknown. Eight slicer-authored fixtures pin it down, the
two sharpest putting the silence exactly where the partly-painted facet is.

Because both sides now agree, the audit compares the whole per-slot attribution
again rather than painted area alone — the narrowing done a sprint ago was a
workaround for this defect and is gone.

### A project of several objects

Orca's own badge project holds three: each with its own object file, its own
relationship, its own composite with its own components and build item, and part
ids unique across the project. That is the shape a prepared copy now takes for
**every** logical object, not only the first. Before this, a project with more
than one object kept its geometry in the root model — where Orca does not read
painting from — so a multi-object painted project lost its colour while every
per-file check passed.

Filament capacity is computed across every object. The audit answers per object:
the shape of its parts, the painting on them, where it sits, its assignment. The
object count counts objects rather than `<object>` elements, which had made three
objects look like seven.

Two objects referencing one mesh is **legitimate** — `orca-pa-line-dual` does it
eight times. A validator check that called it broken was written and removed
again, with the counter-example recorded where the check was.

### Orca prints the painting

The previous handoff's claim was "Orca reads and round-trips it". A painted cube
alone on the plate slices to two objects — the cube and a **wipe tower**. The same
cube with its paint attributes stripped slices to the cube alone. A wipe tower
exists only for a print that changes filament, and the control is what makes that
a measurement. The claim is now "Orca prints it".

## The Orca round-trip, per object

Three-object project, prepared, validator PASS, opened by Orca 2.3.5, saved back:

| | Studio wrote | Orca wrote |
|---|---|---|
| A (two volumes) | slot 0, parts on filaments 2 and 5, 6+6 facets, 6+2 painted, at 40 40 10 | identical |
| B (painted) | object slot 3, one part, 12 facets, 8 painted, at 90 40 10 | identical |
| C (plain) | slot 0, one part, 12 facets, 0 painted, at 140 90 10 | identical |
| project | 5 declared filaments, 4 nozzles | 5 declared filaments, 4 nozzles |

Orca renumbers ids and reorders the objects — its own choice — and every semantic
fact survives. Geometry digests match on both sides, per part.

## The plate "Outside" finding — scoped, not fixed

Evidence collected this instalment:

* the U1 printable area is `0.5x1 … 270.5x271`;
* the single-cube fixtures cross at build transform `10 10 10` with a mesh from
  −10 to +10, so they occupy 0–20 in x and y — touching x = 0, outside a polygon
  that starts at 0.5. Orca files them under **Outside**;
* the three-object fixture sits at 40/90/140, occupies 30–150, and slices without
  complaint. Placement is carried exactly in both cases.

So this is not a Studio bug in the sense of moving anything: the copy is where the
source put it, and the source's bed origin is not the U1's. The likely right
answer is **A plus B** — preserve the source placement and *say* the object is off
the target bed, and offer an explicit "move onto the U1 plate" the person chooses.
Automatic repositioning (C) would silently change where a print lands. Not
implemented; this is the scoping the next sprint asked for.

## Backlog, reranked

1. **Tell the person when a prepared object is off the U1 bed**, and offer an
   explicit reposition. Scoped above; nothing implemented.
2. **Per-object overrides** — still category D, not established. The round-trip
   harness is how to settle it: write a candidate `layer_height` on a part, read
   what comes back, and use an invented key as the control.
3. **Second material provider** — Spoolman is still the only implementation.
4. **OBJ/GLB input** — unchanged, still last.

Nothing else from the previous handoff's list is open: the Prusa reader defect is
fixed, multi-object sources carry, and the slice-level paint proof is obtained.

## Release policy from here

No release until a convergence sprint that re-runs, against the **final** built
installer: backend, desktop, selfcheck, installed acceptance, the v0.8.0 → next
in-place upgrade, and the real-U1 hardware harness. `main` carries user-facing
capability, so the next release is a **minor** — v0.9.0, not v0.8.1.

## Things that will bite

Everything under this heading in the previous handoffs still applies, especially
the Orca automation rule: **no automation runs while an Orca someone else opened
is running.** Added:

- **`\b` in a regex written through a shell heredoc arrives as a backspace byte.**
  It happened again here, in `stl_wrap.py`, and the pattern parsed fine while
  matching nothing. The patterns it affected are now written with no backslash
  escape at all — `[0-9]` rather than `\d`, a literal space rather than `\s` — so
  there is nothing left to mangle. Prefer that to remembering to escape.
- **`re.findall(compiled_pattern, text, re.S)` raises.** Flags belong to the
  compile; call `pattern.findall(text)`.
- **Preparing writes a `.orig.3mf` beside its source.** A test that prepares a
  fixture in place leaves a file in the repository; copy it to `tmp_path` first.
