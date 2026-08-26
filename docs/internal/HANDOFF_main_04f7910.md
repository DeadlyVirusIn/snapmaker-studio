# Handoff — unreleased work on `main` after v0.8.0, third instalment

Written 2026-08-25. **Nothing here is released.** Supersedes
`HANDOFF_main_e418dc0.md`; read `HANDOFF_v0.8.0.md` for the released product.

## Exact state

| | |
|---|---|
| Current stable release | **v0.8.0**, published, latest, untouched |
| Release tag | `v0.8.0` → commit `e12bc59` |
| `main` HEAD | **`04f7910`** |
| `origin/main` | in step with `main` — the previous instalment's five commits were pushed at the start of this one |
| Working tree | clean |
| Release evidence | `docs/internal/evidence/0.8.0.json` unchanged; no snapshot edited |

Commits since the previous handoff:

```
04f7910 docs(truth): the capacity rule, and what Orca needs to read painting
078104c feat(prepare): painting crosses in the dialect Snapmaker Orca reads
7f3729e feat(prepare): a copy declares as many filaments as it refers to
cd71526 docs(internal): handoff after the Orca measurements
```

## Current verification on `main`

Backend **1531 passed / 4 skipped** · desktop **321** · `u1convert selfcheck`
**27/27** · `tsc --noEmit` clean · `cargo check` clean · production build clean.

**Not run against `main`:** installed-app acceptance and the real-U1 hardware
harness. Those were last run against the v0.8.0 final installer (34/34 and 39/39).
`main` has changed runtime code since, so **`main` is not hardware verified**.

## Orca automation is now blocked while anyone else's Orca is open

The instalment before this one began with an Orca the maintainer had opened, and
ended with that process gone and one of their files carrying an mtime from inside
the automation window. Nothing proved the automation did it — every keystroke was
already gated on our own process owning the foreground — and nothing proved it did
not. An automation that cannot be exonerated is not safe enough to run beside
someone's work.

The rule is no longer "do not touch theirs". It is **do not run at all while
theirs exists**: the session surveys every Snapmaker Orca process first and
refuses to start if any is running, works in its own temporary directory on a copy
of the project, sends input only while its own process id owns the foreground,
captures only its own window, closes only its own process id — never force-kills —
and afterwards checks that no Orca it did not start exists and that no watched file
outside its directory was written. Every run this sprint reported a clean audit.

## What was measured

Both answers came from files Snapmaker Orca 2.3.5 wrote, using the round-trip
harness described in the previous handoff.

### Logical filaments are not toolheads

| declared | slot 1 | slot 4 | slot 5 | slot 6 |
|---|---|---|---|---|
| 4 | kept | kept | **→ 0** | **→ 0** |
| 5 | — | kept | kept | **→ 0** |
| 6 | — | kept | kept | kept |

**Orca keeps a slot whenever the project declares that many filaments.** The four
nozzles and the bed were unchanged in all ten cells. The previous sprint's
explanation — the U1's four toolheads — was wrong.

So the prepared copy declares as many filaments as the source refers to, across
object assignments, volume assignments and painted colour. Which structures grow
was measured by handing Orca a six-filament project and reading what it held at
six: the flush table (square in the count), the flush vector (twice it),
`filament_maps`, and `slice_info.config`'s rows. What stays at four is every
per-extruder option and `printable_area`, which is the bed polygon and four
entries long by coincidence — a naive "grow every four-element array" corrupts the
bed. Studio's existing per-filament key list was checked against Orca's own
behaviour and has no false positives.

### Painting needs two things, and neither alone is enough

| the mesh is | the attribute is | painting after Orca |
|---|---|---|
| in the root model | `paint_color` | **none** |
| in its own object file, behind a component | `paint_color` | all 8 facets, same slots, same areas |
| in its own object file, behind a component | `slic3rpe:mmu_segmentation` | **none** |

The previous handoff's backlog item — "translate the paint dialect on the way
out" — would have fixed nothing on its own. A painted object now crosses in both
respects, using the component/object-file layout the multi-part writer already
produced.

The encoded value is unchanged; the OrcaSlicer and PrusaSlicer painted-cube
fixtures carry byte-identical strings for the same eight facets. No painting
version is written: no project in the Orca family declares one, and a copy without
one opens correctly.

**The control.** Handed a paint tree that cannot be decoded, Orca wrote back
`00000000` — an unpainted facet. A slicer merely carrying the string across would
have returned the broken one unchanged, so that is what makes the rows above
evidence rather than pass-through.

## What else changed

**The structural validator runs inside Prepare.** It had caught every corruption
the tests threw at it and had never run outside them, so a writer bug would have
reached the user as a project Orca opens wrongly. An unsound copy is refused, not
saved. Running it in the pipeline immediately found a false positive of its own:
it read every part id and component id in a file as if they belonged to one
object, and called a genuine eight-object Orca project broken. Both checks are
scoped per object now, and a test damages the writer's output to prove Prepare
refuses it.

**The audit gained two rows and lost a wrong one.** Each part's painting is
compared facet by facet in order, so colour on the wrong part is a finding rather
than a matching set of values. The per-slot painting comparison counts painted
area only — a project's totals also include the area nobody painted, attributed to
whatever slot that mesh is assigned, so a copy that faithfully carried a part's
filament moved that remainder and looked repainted.

## Open findings worth a sprint of their own

1. **The Prusa reader gives one default slot to a whole object.** In
   `painted_color._default_slot`, the Prusa branch returns the first volume with
   an extruder for every facet of the object, so a two-volume object's unpainted
   remainder is attributed to the first volume's filament. Measured on the
   two-volume fixture: 50 mm² sits under slot 2 in the source reading and under
   slot 5 in the copy's, and the copy's is the correct one. The fidelity
   comparison no longer depends on it, so nothing currently reports wrongly — but
   the source-side reading is wrong and any feature that uses per-slot area from a
   Prusa project inherits it. The fix is per-volume attribution, which means the
   Prusa reader has to describe volumes rather than objects.
2. **The prepared copy lands at the plate corner.** Established as **pre-existing,
   not caused by the multi-part or paint work**: the source fixture's own build
   item is `10 10 10` and the copy carries it unchanged, which is the correct
   "placement carried" behaviour. It sits at the corner because PrusaSlicer's bed
   origin is not the U1's. Orca files it under *Outside*. A first impression worth
   fixing, in its own sprint, by deciding what Studio should do about a placement
   that is legal on the source bed and off the target one.
3. **Multi-object sources keep the old layout.** `_try_multipart` handles one
   source object; a project with several keeps the geometry in the root, so its
   painting does not reach Orca. The audit says so, per copy, rather than the
   crossing failing silently — but the honest fix is to emit the target layout for
   every object.
4. **No slice-level proof for painting.** The save round-trip shows Orca reads and
   rewrites the painting; the plate's own record of which filaments a sliced plate
   uses was not obtained for a painted project (the painted fixtures sit off the
   plate, which is finding 2). The claim is "Orca reads it", not "Orca prints it".

## Backlog after those

5. **Second material provider** — Spoolman is still the only implementation.
6. **Per-object overrides** — still category D, not established. The round-trip
   harness is how to settle it: write a candidate `layer_height` on a part, read
   what comes back, and use an invented key as the control.
7. **OBJ/GLB input** — unchanged, still last.

## Release policy from here

No release until a convergence sprint that re-runs, against the **final** built
installer: backend, desktop, selfcheck, installed acceptance, the v0.8.0 → next
in-place upgrade, and the real-U1 hardware harness. `main` carries user-facing
capability, so the next release is a **minor** — v0.9.0, not v0.8.1.

## Things that will bite

Everything under this heading in the two previous handoffs still applies. Added:

- **A prepared U1 project has 125 four-element lists and they are not all about
  filament.** `printable_area` is the bed. The per-extruder options are the
  machine. Growing either is claiming a fifth toolhead exists.
- **Orca's filament panel will not add a fifth filament to a U1 project**, so the
  capacity question cannot be answered through its interface. It is answered by
  writing the file and reading what comes back.
- **A paste into the save dialog can lose its last character** to autocomplete;
  the harness checks the field through UIA and repeats the paste.
- **Another application will steal the foreground mid-run.** The harness retries
  the raise and still refuses to send input without proving ownership; a run that
  fails that way is a retry, not a finding.
