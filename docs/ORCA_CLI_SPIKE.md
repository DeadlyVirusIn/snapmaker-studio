# Orca CLI Spike — can "Verified by Orca" work? (beta.22 pricing spike)

**Date:** 2026-07-01 · Timeboxed 1-day spike per `docs/internal/FABEL_ROADMAP_RESET.md` (beta.20.4 item).
**Question:** can Studio run an Orca CLI slice on a prepared U1 copy and read back a machine-readable verdict (typed exit codes / `result.json` warnings) to upgrade its collision/layout "unknown"?
**Answer (short):** Snapmaker Orca's CLI is **not viable** (segfaults). Upstream Orca 2.4.1 CLI **runs headless reliably**, but in the 2.4.1 release build **no `result.json` was produced and no typed failure exit codes fired** for naive out-of-bounds / overlapping fixtures. **Recommendation: viable-with-caveats — do not commit beta.22 scope until the machine-readable verdict channel is confirmed** (flag matrix + newer build follow-up below).

## Versions tested

| Slicer | Version | Source |
|---|---|---|
| Snapmaker Orca (installed) | v2.3.4 (fork base = upstream 2.3.0) | `C:\Program Files\Snapmaker_Orca\snapmaker-orca.exe` |
| OrcaSlicer upstream | v2.4.1 (2026-06-28) | `OrcaSlicer_Windows_V2.4.1_x64_portable.zip` from the official release |

## Commands run

All headless (`Start-Process -WindowStyle Hidden`, output to a scratch `--outputdir`, 2–4 min timeout):

```text
<exe> --slice 0 --debug 1 --outputdir <dir> <file.3mf>
<exe> --info --outputdir <dir> <file.3mf>          (fork only)
```

## Fixtures and results

Fixtures built from `examples/sample_cube_U1_SnapmakerU1.3mf` (a Studio-prepared U1 copy; ~20 mm cube at plate center) by duplicating the build `<item>` with a shifted transform. Source files verified unmodified after all runs (`git status examples/` clean).

| Fixture | Geometry | Snapmaker Orca 2.3.4 CLI | Upstream Orca 2.4.1 CLI |
|---|---|---|---|
| clean (1 cube) | on plate | **CRASH** exit `0xC0000005` (access violation), no output | exit 0, `plate_1.gcode` (243 KB) |
| collision (2 cubes, +5 mm offset = heavy overlap) | overlapping instances | **CRASH** `0xC0000005` | exit 0, gcode (425 KB) — overlapping meshes fuse; by-layer slicing treats this as legal union, **not** a collision error |
| spaced (2 cubes, +60 mm) | clear of each other | not run (CLI already proven dead) | exit 0, gcode (424 KB) |
| out-of-bounds (2nd cube at x≈325) | partly/fully outside 270 bed | — | exit 0, gcode — **no boundary error** |
| far out-of-bounds (2nd cube at x=525.5, verified in model XML) | far outside bed | — | exit 0, gcode (423 KB) — **still no boundary error** |
| `--info` | — | **CRASH** `0xC0000005` | not tested (timebox) |

## Findings

1. **Snapmaker Orca fork CLI is dead.** Both `--slice` and `--info` segfault immediately. Consistent with the fork being based on upstream 2.3.0 — the CLI segfault that made `--info/--slice/--export-3mf` unusable was only fixed upstream in v2.3.2 (PR #12719). Conclusion: **no fork rebase → no fork CLI.**
2. **Upstream 2.4.1 CLI is solid as a headless slicer.** Exit 0, deterministic `plate_1.gcode` output, no GUI window, no writes outside `--outputdir`, source files untouched. Running it against a Studio-prepared U1 copy "just works."
3. **The machine-readable verdict channel is unproven in the 2.4.1 release build.** No `result.json` appeared in `--outputdir` (or anywhere) for success or failure-shaped inputs. The `record_exit_reson()` writer and typed exit codes (`CLI_OBJECTS_PARTLY_INSIDE`, `CLI_OBJECT_COLLISION_IN_LAYER_PRINT`, …) exist in upstream `src/OrcaSlicer.cpp` on `main` — either newer than the 2.4.1 tag, gated behind flags not tried here (`--pipe`, `--export-slicedata`, `--metadata-*`), or written only on paths these fixtures didn't reach.
4. **Naive failure fixtures don't fail.** A cube 255 mm outside the plate sliced with exit 0. The CLI appears to auto-place/absorb out-of-bounds objects by default (candidate causes: default `--ensure-on-bed`-like behavior, plate-membership semantics assigning far objects to another plate, or checks only firing with `--normative-check`). Overlapping instances are legitimately fused by by-layer slicing — the GUI "objects too close" warning class relates to sequential print / extruder clearance, not mesh overlap.
5. **Dual-install is technically clean.** The upstream portable zip runs beside the installed Snapmaker Orca with zero interaction (separate exe, separate config). Using upstream as a verification engine while Snapmaker Orca remains the handoff target is feasible — at the cost of asking users to obtain a second slicer (~170 MB), and of verifying against non-Snapmaker profile semantics.

## Recommendation

**Viable-with-caveats.** For beta.22's "Verify with Orca":

- **Engine:** upstream Orca ≥2.4.1 only. The Snapmaker fork's CLI is unusable until it rebases to ≥2.3.2 (fork issue #291 asks for exactly this) — track that as the trigger to revisit.
- **Blockers before committing scope:** a short follow-up spike must (a) test the flag matrix `--normative-check` / `--no-check` / `--ensure-on-bed 0` / `--arrange 0` / `--pipe` / `--export-slicedata` against the same fixtures, and (b) test an upstream nightly/next tag for `result.json`. If neither yields a machine-readable boundary/collision verdict, the beta.22 feature reduces to "Orca slices it without crashing + gcode produced" — still useful (slice-success + time/filament from output) but **not** the collision-unknown killer — reprice accordingly.
- **What is already safe to build on:** headless slice-success verification + parsing the produced gcode/`.gcode.3mf` for time/filament (the beta.22 cost item), since that only needs exit 0 + output files, which 2.4.1 delivers today.
- **Do not** integrate the CLI in beta.20.4 (out of scope) and do not claim any "verified by Orca" capability in docs until the follow-up spike lands.

## result.json example structure

Not observed in this spike (see finding 3). The upstream `main`-branch writer emits, per source: exit code/error message, `prepare_time`, `export_time`, `layer_height`, `wall_loops`, `sparse_infill_density`, and per-plate objects with `id`, `sliced_time`, `triangle_count`, `warning_message`. Treat as unverified until reproduced on a real build.

---

## Addendum (2026-07-02) — root cause found, spike question closed

Follow-up source inspection of the **v2.4.1 tag** (not `main`) resolved finding 3:
`record_exit_reson()` **is present in v2.4.1** and is called on every exit path —
but its entire body is wrapped in **`#if defined(__linux__) || defined(__LINUX__)`**.
It is a compile-time gate, not a flag: **official Windows and macOS builds never
write `result.json`.** That is exactly why this spike's Windows runs produced none.

Consequences for beta.22 "Verify with Orca":

- **Rescope on Windows** to what the CLI reliably provides: exit code + produced
  artifacts (slice-success verification) and time/filament parsed from the output
  gcode/`.gcode.3mf` — the cost item stands; the machine-readable warning channel
  does not, on Windows.
- Options if the warning channel is still wanted: run the Linux CLI in WSL/container
  (heavy, not novice-friendly) or propose an upstream change lifting the platform
  gate (small patch, reasonable ask).
- **Snapmaker fork watch list:** fork `version.inc` already reads 2.3.5 (unreleased),
  and three community PRs opened 2026-07-01 fix fork CLI crashes — **#560**
  (`--load-assemble-list` plate-loading crash), **#561** (profile normalization
  without `nozzle_diameter`), **#562** (GUI filament state during extruder
  expansion). If these land in 2.3.5, re-run this spike against the fork build —
  a working fork CLI would remove the dual-install requirement entirely.
