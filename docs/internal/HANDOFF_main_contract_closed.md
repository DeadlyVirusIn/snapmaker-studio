# The U1 project contract audit is closed

Written 2026-08-28. Supersedes `HANDOFF_main_contract_addendum.md`; read
`HANDOFF_main_contract.md` for what the contract is and
`HANDOFF_main_reachability.md` for the mechanism underneath it.

**No runtime code changed in this run.** It was evidence only: the four
outstanding fixtures were built, run through Snapmaker Orca 2.3.6 and answered.

## State

| | |
|---|---|
| Current stable release | **v0.8.0**, published, untouched |
| Contract audit | **CLOSED** |
| Software gates | backend **1731 passed / 4 skipped**, desktop **335**, selfcheck **27/27**, `tsc` clean, `cargo check` clean, production build clean |
| v0.8.0 evidence | unchanged |

**Not run:** installed acceptance and the real-U1 hardware harness. `main` is
still not hardware verified and there is **no release**.

## The desktop was exclusive

Sampled before starting: 30 readings over 60 s, one foreground pid throughout,
human-idle rising 50 s → 108 s. Every fixture then re-checked six seconds of
foreground stability before its Orca started, and `Assert-StillOwned` re-checked
ownership after each save. No run reported a stolen foreground.

## What the four fixtures answered

### The settings carried from a PrusaSlicer project

Five process values, deliberately not the U1 preset's, in two projects differing
only in `different_settings_to_system`. Read from the project Orca saved back:

| | Studio wrote | undeclared | declared |
|---|---|---|---|
| `layer_height` | 0.15 | **0.2** | **0.15** |
| `initial_layer_print_height` | 0.3 | **0.25** | **0.3** |
| `sparse_infill_density` | 37% | **15%** | **37%** |
| `wall_loops` | 4 | **2** | **4** |
| `brim_width` | 8 | **5** | **8** |

**0 of 5 survived undeclared; 5 of 5 declared.** And it is behaviour, not just
storage: the declared project sliced to **199 layers at a 0.15 mm step**, which
is the carried layer height doing its job.

### The machine's own start G-code

A comment — nothing that moves, heats or homes — at the top of
`machine_start_gcode`, with the printer's real block underneath, in two projects
differing only in the printer entry of the declaration:

| | in the project Orca saved | in the exported G-code |
|---|---|---|
| undeclared | **absent** | **absent** |
| declared | **present** | **present** |

Undeclared, Orca replaced the whole block with the printer preset's own, dated
`20260128`. That is the behaviour the eight removed template keys were removed
for, confirmed at the level that matters: what the machine would actually run.

### The same project, prepared both ways

Three objects, one of them multi-part, painted, five logical filaments, a
per-object override and carried source settings — prepared once with the
pre-minimisation 549-key template and once with the current 541-key one, and both
handed to Orca. The two prepared inputs are identical on all 542 shared keys, the
full one carrying exactly the eight extras.

Compared **per object by name**, because Orca reorders objects on save and
position is the wrong key:

| object | full 549 | minimal 541 |
|---|---|---|
| `A_two_volumes` | extruder 0, parts on filaments 2 and 5 | identical |
| `B_painted` | extruder 3, `enable_support=1`, `sparse_infill_density=60%` | identical |
| `C_plain` | extruder 0 | identical |

Also identical: part subtypes, part matrices, 16 painted facets, 40 triangles,
plate count, all three build transforms, object-file digests, model instances,
relationship targets and every preset identity. The only differences anywhere
were the order objects appear in the file, which is not a fact the project
states.

`layer_height` is correctly **absent** from the carried override: this is a
five-filament plate, and Orca refuses to slice a prime-tower plate whose objects
have different layer heights.

### Sliced, full against minimal

The multi-object fixture cannot slice — its cubes are open shells, so Orca says
"No layers were detected" — so the behavioural comparison used a solid
two-filament project put through both templates and sliced on the same Orca:

| | full 549 | minimal 541 |
|---|---|---|
| plate layers | 199 | 199 |
| per object | 199 layers, 0.15 mm step, 6366.98 mm | identical |
| wipe tower | yes | yes |
| start block | `20260128` | `20260128` |
| filament used | 35.18 g | 35.18 g |
| **G-code** | **1,427,703 bytes** | **1,427,703 bytes** |

**Byte-identical.** Removing the eight keys changed nothing about the print,
which is what "they had never reached a print" predicted.

## Verdict

**U1 PROJECT CONTRACT AUDIT — CLOSED.**

The remaining 274 preset-equal values are **REDUNDANT_BUT_HARMLESS / DEFERRED**.
They are already inherited in practice, they produce no measured defect, and
removing them is churn. Do not reopen the 541-key audit without a measured
defect.

## Two things found on the way

**A fixture off the plate is Studio working, not failing.** The
`prusa-semantics` sources land 1.0 mm off the left and 1.5 mm off the front of
the U1 bed, so Orca greys out Slice. `plate_placement.assess` names the object,
the edges and the millimetres and offers the one-piece move; applying it made the
plates sliceable. Worth knowing before mistaking it for a bug.

**A long path defeats the file dialog.** Several runs failed with
"SAVE FAILED: not written within 120s", which reads like Orca refusing the file.
It was not: a 160-character path typed into the dialog lost its leading
characters — the box held `a\Local\Temp\claude\...` instead of the whole path —
so Enter had nothing valid to commit. `WM_SETTEXT` and a clipboard paste were
both tried and neither could be verified (`GetWindowTextLengthW` reads 0 for that
control even when it visibly holds text; `Get-Clipboard` hangs in a
non-interactive host). **Driving Orca to a short destination fixed it on the
first attempt.** Keep evidence runs under a short path.

## Next

The next engineering item is the **second material provider**. Spoolman is still
the only implementation of the material-provider seam, and proving the seam is
genuinely provider-generic needs a second real one. Nothing about it was
researched, chosen or written in this run.

## Release

**NO RELEASE.** A convergence sprint must still run against the exact final
installer: version bump, full software gates, installed acceptance, the
v0.8.0 → v0.9.0 upgrade, the real-U1 hardware harness, immutable v0.9.0 evidence,
and publish / re-download / re-hash.
