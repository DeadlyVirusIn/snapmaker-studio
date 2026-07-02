# Upstream Utilization Audit — Snapmaker Studio (internal engineering review)

> **Internal review document** — not user documentation.
> Date: 2026-07-02 · Live GitHub data. Delta against the 2026-07-01 upstream review
> (`FABEL_REVIEW_FINDINGS_TABLE.md` §3) plus utilization verdicts.
> Companions: `FABLE_PUBLIC_RELEASE_AUDIT.md`, `FABLE_RELEASE_COPY_REVIEW.md`.

## 1. Headline findings

1. **The Orca CLI `result.json` question is closed — and it changes beta.22.**
   `record_exit_reson()` *is* present in upstream v2.4.1 (`src/OrcaSlicer.cpp` ~line
   416, writing `<outputdir>/result.json` on every exit path) **but the whole body is
   wrapped in `#if defined(__linux__) || defined(__LINUX__)`** — a compile-time gate,
   not a flag. On Windows and macOS official builds it is a no-op. This exactly
   explains the `ORCA_CLI_SPIKE.md` result (no result.json on Windows 2.4.1).
   **Consequence:** on Windows, "Verify with Orca" cannot rely on result.json from
   official builds. Realistic options: (a) exit-code + produced-artifacts signal only
   (slice-success verification + cost/time from output — still worthwhile), (b) run
   the Linux CLI in WSL/container (heavy; not novice-friendly), (c) upstream PR to
   lift the gate (worth filing — small change, clear rationale). Update
   `ORCA_CLI_SPIKE.md` accordingly.
2. **The Snapmaker fork CLI may fix itself.** Fork `version.inc` already says 2.3.5
   (unreleased), and three community PRs opened 2026-07-01 target exactly the fork's
   CLI crashes: #560 (`--load-assemble-list` plate-loading crash), #561 (process-only
   profile normalization without `nozzle_diameter`), #562 (GUI filament state during
   extruder expansion). None merged yet. **Watch these + the 2.3.5 release; re-run
   the CLI spike against 2.3.5.** If they land, the handoff slicer itself becomes the
   verification engine — no dual-install story needed.
3. **Moonraker: no risk.** v0.10.0 deprecations are update-manager endpoints only;
   Studio's GET telemetry, gcode upload, pause/resume/cancel and M112 paths are
   untouched.

## 2. Upstream table (state 2026-07-02)

| Repo | Latest relevant change | Studio currently uses? | Gap | Recommendation | Release target |
|---|---|---|---|---|---|
| OrcaSlicer/OrcaSlicer v2.4.1 | result.json writer exists but Linux-only compile gate; recent merges: preset validator update (#14507), renamed-preset aliases (#14504) | Reference only (profile facts; spike ran the CLI) | Windows CLI gives exit code + artifacts, no machine-readable warnings | Re-scope beta.22 "Verify with Orca" to slice-success + cost/time from output; consider upstream PR to lift the Linux gate | beta.22 (rescoped) |
| Snapmaker/OrcaSlicer v2.3.4 (2.3.5 in prep) | CLI-crash-fix PRs #560/#561/#562 (2026-07-01, open); flutter device UI + filament sync fixes merged | Handoff target (spawn + path detection) | Fork CLI broken in 2.3.4; deep link `snapmaker-orca://` still unused by Studio | Watch #560–562 + 2.3.5; re-spike CLI on 2.3.5; adopt deep-link launch with path fallback | beta.22 |
| bambulab/BambuStudio 2.8.0-beta | No bbs_3mf.cpp changes since 2026-06-24 (assembly steps tree) | Bambu-family 3MF read (tolerant, in-memory) | Assembly-guide payloads will appear in 2.8-saved files | Corpus check when 2.8.0 goes stable; keep read-only tolerant posture | beta.22 corpus ritual |
| prusa3d/PrusaSlicer 2.9.6 | Nothing new | Detect + partial INI read | none new | No action | — |
| Ultimaker/Cura 5.13.0 (5.14-alpha exists) | Nothing relevant | Detect-only | none | No action (adapter stays deferred) | — |
| 3MFConsortium lib3mf 2.5.0 | Nothing new; production/slice specs still dormant | Not used (custom lxml reader — correct choice) | none | No action | — |
| Arksine/moonraker v0.10.0 | Update-manager endpoint deprecations only; upcoming: standard reboot/shutdown, PrusaSlicer-fork metadata detection | Full Printer Hub client (GET + confirmed POST) | none affecting Studio | No action; note reboot/shutdown endpoints as possible future confirmed-controls | — |

## 3. What Studio uses correctly today

Snapmaker Orca as the one-way handoff target (spawn, no automation) ✓ · U1 profile
facts sourced from the installed vendor bundle semantics (270×270×270 with travel-limit
clarification) ✓ · Moonraker read-first client with confirmed controls and extension-
gated uploads ✓ · Bambu-family 3MF read kept tolerant and in-memory (right posture
against format churn; pinned by the path-traversal test) ✓ · lib3mf correctly *not*
adopted (adds nothing for the vendor dialect) ✓ · Model discovery kept to link-out
(no scraping, no API-key dead ends in the primary flow) ✓.

## 4. Missed opportunities (carried + new)

1. `snapmaker-orca://` deep-link handoff (registered by the fork installer; Studio
   still path-guesses). beta.22.
2. `.gcode.3mf` awareness in Printer Hub (Orca 2.4 job format, `plateindex`). beta.22.
3. Cost/time from sliced output (works today — needs only exit-0 + artifacts, which
   Windows CLI delivers). beta.22 — now the *strongest* beta.22 item given the
   result.json gate.
4. Profile freshness watcher vs installed vendor bundle. beta.22.
5. Roadmap items dropped from beta.21 that remain cheap: print-by-object collision
   advisory promotion; mixing-aware colour caveat (fork 2.3.3 Full Spectrum). beta.21.x
   or beta.22 — copy-level, low risk.
6. New: upstream PR to un-gate result.json on Windows (small, high leverage for the
   whole ecosystem, positions Studio as a good citizen). Research track.

## 5. Stop / defer (reconfirmed)

Native PartPlate reimplementation — stop (unchanged). Full Bambu instancing — research
only; 2.8 assembly payloads reinforce this. lib3mf adoption — defer. Cura/Creality
adapters — defer. In-app API-key model search — stop (unchanged).

## 6. Public claims needing updates because upstream changed

None today — no public Studio claim depends on result.json or fork-CLI behavior.
Internal only: `ORCA_CLI_SPIKE.md` should gain a dated addendum with the Linux-gate
finding and the #560–562 watch list so beta.22 planning reads the corrected picture.
