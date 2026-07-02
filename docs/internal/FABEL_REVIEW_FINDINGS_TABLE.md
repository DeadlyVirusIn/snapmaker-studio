> **INTERNAL ENGINEERING REVIEW — not user documentation.**

# Fabel Review — Findings Tables

**Date:** 2026-07-01 · Companion to `docs/FABEL_DEVIL_ADVOCATE_REVIEW.md`. Live upstream data gathered 2026-07-01 via the GitHub API.

---

## 1. Risk register

| # | Risk | Severity | Evidence | Why it matters | Mitigation | Release target |
|---|---|---|---|---|---|---|
| R1 | Installed-app acceptance never passes (manual 12-item checklist, single human gate) | **P0** | TRUST_STATUS.md: beta.20.1/.20.2/.20.3 all "PARTIAL / PENDING — not accepted"; checklist all unchecked | No release is trustworthy or demoable; blocks everything | Run checklist for 20.4; then automate an installed-app smoke (install → launch → open STL/3MF → prepare copy → uninstall) in CI or a scripted local harness | beta.20.4 (run), beta.21 (automate) |
| R2 | Docs contradiction epidemic | **P0 (judge-facing)** | README SHA256 blank; JUDGE_OVERVIEW/WHAT_TO_TEST_FIRST at beta.15; fund docs at beta.1 claiming "read-only, no printer control" vs shipped control; test counts 166 vs 321+138; CSP "shipped" (JUDGE_OVERVIEW) vs "disabled, pre-GA blocker" (PRODUCTION_READINESS_TRIAGE); bed 270³ (CHANGELOG) vs 271×335×275 (PRINTER_HUB_VERIFICATION); 3 different SHA256/size values in beta.20 family; TRUST_STATUS header says 20.3 but body says 20.2 | Product's core pitch is honesty; one discovered contradiction collapses it | Single version/SHA source (generated); historical banners on stale docs; docs-consistency check in CI | beta.20.4 |
| R3 | Unsigned installer / SmartScreen "Unknown publisher" | **P1** | windows-code-signing.md (deferred); PRODUCTION_READINESS_TRIAGE (external blocker) | First impression for every judge/novice is a security warning | Budget decision (cert or Azure Trusted Signing); until then: README SHA256 always filled + verify instructions | Decision by beta.21 |
| R4 | Collision/spacing = "unknown" for all multi-object 3MF | **P1** | collision.py (branch on object count only); prior real P0 miss (Orca collision warning missed); TRUST_STATUS deferral note self-references beta.20.3 | Highest-stakes check gives zero help exactly where users need it | Two-step: narrowed AABB-separation check for component-based files (beta.21); Orca CLI verification import (beta.22) | beta.21 + beta.22 |
| R5 | Upstream U1 profile staleness | **P1** | Orca upstream 2.4.1 PRs #14305/#14391 (U1 bed corrected to 270×270; new 0.2/0.6/0.8 nozzles); PR #14432 (setting-ID mass rewrite); Studio hardcodes U1_BUILD 270³, 4 toolheads; Snapmaker fork based on upstream 2.3.0 | Prepared copies / advice drift out of date silently; "profile compatible" claim erodes | Constants module with provenance; profile-freshness watcher vs installed Snapmaker Orca vendor bundle | beta.22 (watcher), constants beta.21 |
| R6 | Bambu 3MF format mutation | **P1** | bbs_3mf.cpp commits: 1-based variant_ids (2026-04-15), AMS arrangement metadata, has_filament_switcher, assembly-guide steps tree (2026-06-24, v2.8.0-beta) | Regex/byte-count fast paths break silently; plate count already computed 2 inconsistent ways (fingerprint vs plate_remap) | Tolerant read-only parsing (keep); consolidate plate-count source; per-BambuStudio-release corpus check; watch bbs_3mf.cpp | beta.22 + research |
| R7 | Doctor sprawl / IA complexity | **P1 (novice)** | ~13 "Doctor" nouns; 3 first-layer surfaces; Cost/Pricing/Profit aliases; 12 Advanced nav items; NOVICE_UX_RED_TEAM P0s partially open | Novices can't find "will this print?"; judges see clutter, not intelligence | IA collapse to 5 Simple-mode items + Fix Plan umbrella (see review §5) | beta.21 |
| R8 | Printer-control safety gating UI-only; e-stop never hardware-fired | **P1 (safety)** | moonraker.py `_post` comment block ("UI is the safety gate"); TRUST_STATUS: M112 path contract-verified only | One frontend regression away from an unconfirmed motion/heat command | Backend arming/confirmation token for control endpoints; fire e-stop once on hardware and record it | arming beta.22; hardware test ASAP |
| R9 | Model-discovery dependency fragility | **P2** | model_search.py: in-app search needs external API keys; link-out windows to 6 third-party sites; MakerWorld gates format versions server-side | Demo-failure surface; features that look dead ("needs a key configured outside the app") | Remove in-app key-search UI (keep link-out); demo script avoids live sites | beta.21 |
| R10 | Orca handoff fragility | **P2** | main.rs: Windows-only hardcoded paths, fire-and-forget spawn, no version negotiation; fork registers `snapmaker-orca://` protocol (unused by Studio) | Handoff is the product's climax step; silent failure = broken promise | Deep-link launch with path fallback; post-launch hint; detect version | beta.22 |
| R11 | Hidden placeholder/dead-end states | **P2** | Disabled "3MF export not ready" button (ScaleDoctor); "will live in the Printer Doctor" (FirstLayer); `—` cost pillars; Multi-Material explainer tab that redirects | Reads as broken to novices (documented in NOVICE_UX_RED_TEAM) | One consistent "Not supported yet — do this in Orca" pattern; remove future-tense promises | beta.21 |
| R12 | Loopback sidecar hardening (CORS `*`, CSP disabled, token exposure) | **P2 (pre-GA)** | PRODUCTION_READINESS_TRIAGE.md; server.py:70; tauri.conf.json:16 | Documented pre-GA blockers; also contradicts JUDGE_OVERVIEW claim | Fix CORS allowlist; enable CSP; re-verify | pre-GA, start beta.22 |
| R13 | "112/112 corpus" phrasing reads as success guarantee | **P2** | README/PROOF.md/INNOVATION_FUND headline | Fast-reading judge hears "100% success," then finds the disclaimers — trust whiplash | Rephrase: "112/112 files produced structurally valid U1 copies (internal gate; not print success)" everywhere the number appears | beta.20.4 |
| R14 | Docs drifting from app (systemic) | **P2** | Judge docs beta.15; SUBMISSION_STATUS beta.20; ROADMAP "as of beta.17/15" | Recurs every release; manual docs don't scale | Generated version stamps; release checklist item "docs sweep" with grep list | beta.20.4 + process |
| R15 | Upstream Orca changes making Studio stale (general) | **P2** | Orca 2.4.x cadence (~monthly); fork lags upstream by a minor line; fork users demand rebase (issue #291) | Studio sits between two moving targets (fork + upstream) | Quarterly upstream review ritual (this doc's tables as template); pin "validated against" versions in docs | process |

---

## 2. Opportunity map

| Opportunity | User value | Technical difficulty | Upstream dependency | Demo value | Recommended release |
|---|---|---|---|---|---|
| Orca CLI verification import ("Verify with Orca" on prepared copy; parse result.json exit codes + per-plate warning_message) | **Very high** — converts collision/layout "unknown" into verified answer; fixes the real P0 miss class | Medium (process orchestration, version detection, JSON parse; no geometry math) | Orca CLI ≥2.3.2 (upstream; fork CLI viability unverified — spike needed) | **Very high** ("Studio caught it before you even opened Orca — and Orca confirms") | beta.22 |
| Beginner Fix Plan page (one prioritized plain-language list per model) | High — answers "what do I do?" in one place | Low-medium (synthesis over existing intelligence_report) | none | High (judge-facing clarity) | beta.21 |
| Narrowed AABB collision check (component-based files only; instanced stays "unknown") | High — shrinks the unknown to the truly-hard case | Medium (reuse build_item_dims; strict scoping + fixtures) | none | Medium | beta.21 |
| Cost/time from Orca sliced output (.gcode.3mf / gcode metadata) | High — replaces heuristic grams with slicer-accurate numbers | Medium (parse gcode.3mf slice metadata) | Orca 2.4.0 .gcode.3mf format (PR #14238) | Medium-high | beta.22 |
| `snapmaker-orca://` deep-link handoff (fallback to path) | Medium — robustness + future cross-platform | Low | Fork installer protocol registration (nsis + macOS schemes) | Low | beta.22 |
| .gcode.3mf awareness in Printer Hub (job metadata, plateindex) | Medium — correctness for Orca 2.4+ users | Low-medium | Orca PRs #14238/#14404 | Low | beta.22 |
| Profile freshness watcher (compare Studio constants vs installed Snapmaker Orca vendor bundle) | Medium — trust insurance | Low | Snapmaker Orca profile JSON layout (resources/profiles/Snapmaker/) | Low | beta.22 |
| Print-by-object toolhead-collision advisory (U1-specific; by-object sequence already surfaced as at_risk) | Medium-high — fork issue #136 calls it hardware-damage risk | Low (copy + severity promotion of existing at_risk signal) | none | Medium | beta.21 |
| Mixing-aware color advice (caveat when fork's Full Spectrum mixing could apply) | Medium — keeps toolhead-fit advice honest post-2.3.3 | Low (copy change) | Fork 2.3.3 feature awareness only | Low | beta.21 |
| Batch readiness report (printable one-pager over existing batch + pricing) | Medium (print-farm niche) | Low-medium | none | Medium | beta.22+ |
| Judge demo hardening (golden-path script pinned to accepted build; no live-site dependencies) | High (submission risk ↓) | Low | none | Very high (indirect) | beta.20.4 |
| Model Browser → Doctor pipeline polish (open downloaded file straight into Fix Plan) | Medium | Low | none | Medium | beta.21 |
| U1 profile validator (validate prepared copy keys against installed vendor bundle) | Medium | Medium | Snapmaker Orca profile format | Low | beta.22+ |
| True Bambu instancing parser (source_object_id, model_instance transforms, assemble semantics) | High (unlocks real layout math for instanced files) | **Very high**; format actively mutating | BambuStudio bbs_3mf.cpp (moving) | Low direct | Research track |

---

## 3. Upstream enhancements table

| Repo | Recent enhancement | Impact on Studio | Threat/Opportunity | Action |
|---|---|---|---|---|
| OrcaSlicer/OrcaSlicer v2.4.1 (2026-06-28) | U1 profiles: bed corrected 270×270, 0.2/0.8 nozzles added, 0.6 process lineup (PRs #14305, #14391) | Studio's hardcoded U1 facts / prepared profiles can drift | Threat | Constants module + freshness watcher |
| OrcaSlicer v2.4.1 | Profile setting IDs de-duplicated/rewritten w/ CI guard (PR #14432) | Prepared-copy key matching may hit renamed IDs | Threat | Track `renamed_from`; validate against vendor bundle |
| OrcaSlicer v2.4.0 (2026-06-20) | `.gcode.3mf` packaged sliced jobs (PR #14238); `plateindex` on Moonraker uploads (PR #14404, in 2.4.1) | Printer Hub will see .gcode.3mf jobs; cost/time metadata available | Opportunity | beta.22 items |
| OrcaSlicer v2.4.0 | Collision-aware per-object skirts (PR #14130); unsafe by-object configs rejected at slice time (PR #14333) | Orca absorbing collision-class guardrails at slice time | Threat (overlap) | Reposition Studio checks as "before you open Orca"; don't reimplement |
| OrcaSlicer v2.4.0 | Troubleshoot Center (PR #12416) | Diagnostics only, not printability | Neutral | none |
| OrcaSlicer CLI (main) | `--slice/--arrange/--orient/--scale-to-fit/--downward-check/--logfile`; result.json with typed exit codes (incl. CLI_OBJECT_COLLISION_*, CLI_OBJECTS_PARTLY_INSIDE) + per-plate warning_message; segfault fixed in 2.3.2 (PRs #12719, #13001, #13931) | Machine-readable verification channel for prepared copies | **Major opportunity** | beta.22 headline; spike fork-CLI viability first |
| OrcaSlicer v2.3.2 (2026-03-23) | 3MF import path-traversal security fix (PR #12860) | Same bug class could exist in any 3MF zip handling | Threat | Audit container.py / any extract path |
| OrcaSlicer issues | 3D/height-aware exclusion zones still open (#10579; #12774 closed-FR) | Gap upstream hasn't filled | Opportunity | Candidate future advisory (low priority) |
| Snapmaker/OrcaSlicer v2.3.3 (2026-06-01) | Full Spectrum color mixing (2-3 filament blend); ~15 new U1 filament profiles | "Colors > 4 toolheads" advice needs mixing caveat; filament list stale | Threat (advice staleness) | Mixing-aware copy (beta.21) |
| Snapmaker/OrcaSlicer v2.3.0–2.3.1 | Built-in Model Library w/ one-click cloud print; MQTT device channel; Flutter device UI; camera/Cloud Mode | Snapmaker moving up-stack into discovery + monitoring | Threat (positioning) | Studio differentiates on pre-print geometry intelligence + local-first honesty |
| Snapmaker/OrcaSlicer (installer) | Registers `snapmaker-orca://` URL protocol (nsis + macOS CFBundleURLSchemes) | Robust handoff mechanism available | Opportunity | beta.22 deep-link |
| Snapmaker/OrcaSlicer (firmware profiles) | `DEFECT_DETECTION_*` macros — on-printer bed foreign-object detection at print start | First-layer/bed checking moving into firmware | Threat (overlap, long-term) | Keep Studio's first-layer advice pre-print + model-side |
| Snapmaker/OrcaSlicer (fork state) | Based on upstream 2.3.0; rebase demanded (issue #291); local helper service on TCP 13619 for Upload-and-Print | Fork lag = CLI/feature uncertainty; 13619 undocumented integration surface | Both | Spike fork CLI; note 13619 as research |
| Snapmaker/OrcaSlicer issue #136 | Print-by-object toolhead collision (hardware damage risk) | Users want exactly a pre-print collision advisory | Opportunity | Promote by-object at_risk signal (beta.21) |
| bambulab/BambuStudio 2.5→2.8-beta | bbs_3mf.cpp churn: 1-based variant_ids; AMS arrangement metadata; has_filament_switcher; assembly-guide steps tree (commits 291dcbaa/10ccec8c, 2b2bbe12, f4a5398f, 7d67dd45/f3904f3a) | Parser landmines for Bambu-family inputs; format keeps growing | Threat | Corpus check per Bambu release; watch bbs_3mf.cpp; stay read-only/tolerant |
| 3MFConsortium | lib3mf 2.5.0 (2026-02-24; WASM/Python bindings); spec_production/spec_slice dormant since 2024 | No standardization of Bambu/Orca project metadata coming | Neutral-threat | Accept vendor-tracking burden; lib3mf optional for standards-core only |
| prusa3d/PrusaSlicer 2.9.4–2.9.6 | ColorMix; SLA pipeline; junction deviation | No format/preflight moves | Neutral | Keep detect-only adapter |
| Ultimaker/Cura 5.12–5.13 | Disabled-extruder warnings; 3MF load fix; Bambu-printer experiment (5.11-alpha) | Small advisory guardrails appearing in mainstream slicers | Mild threat | none now |
| OSS landscape scan | No pre-print checker >3 stars (printability-ai, STL-Checker-App, parse3MF etc. all tiny) | Whitespace confirmed | Opportunity | Move fast on the beta.21/22 story |

---

## 4. Capability comparison — Studio vs slicers (2026-07-01)

| Capability | Studio today | Snapmaker Orca today (2.3.4) | Orca upstream today (2.4.1) | Bambu/Prusa/Cura | Gap | Recommendation |
|---|---|---|---|---|---|---|
| Layout/bed-boundary check | Advisory world-AABB vs 270³ window; multi-plate = warn; failures → unknown | At slice time (plate checks) | At slice time + CLI exit codes (CLI_OBJECTS_PARTLY_INSIDE) | Similar slice-time | Studio is pre-slice but advisory; slicers are authoritative later | Keep pre-slice advisory; add Orca CLI confirmation (beta.22) |
| Object-object collision/spacing | **Unknown (honest stub)** | Slice-time errors | Slice-time errors + collision-aware skirts + CLI collision exit codes | Slice-time | Studio's biggest capability gap | Narrowed AABB (beta.21) + CLI import (beta.22); never reimplement PartPlate |
| Supports / enforcers | Overhang % heuristic → "supports likely"; enforcer string-count | Full support gen + painting | Full + tree-support clearance improvements | Full | Studio advisory-only by design | Keep advisory; copy must not imply structural parsing |
| Color/toolhead mapping | Colors vs 4 toolheads compare; no mixing awareness | Filament sync w/ device; **Full Spectrum mixing**; pre-send mapping page | Per-feature filament assignment; AMS matching | Bambu AMS mature | Mixing makes Studio's >4-colors advice partially stale | Mixing-aware caveat (beta.21) |
| Scale/fit guidance | Real STL scaled copies; 3MF preview-only (export blocked) | Full scale in GUI | Full + CLI --scale/--scale-to-fit | Full | 3MF scaling gap | Route via Orca (CLI or manual); drop native 3MF scaled export |
| Cost estimation | Geometry-volume × density heuristic; honest "estimate" | Slicer-accurate post-slice | Slicer-accurate + .gcode.3mf metadata | Slicer-accurate | Heuristic vs real | Parse sliced output (beta.22) |
| Model repair/conversion | STL→U1 wrap; Bambu/Orca 3MF→U1 repair w/ preservation validation; U1-identity gate | none (slices what you give it) | Basic mesh fixes | Bambu import-time mesh repair | **Studio's unique strength** | Keep; headline it |
| Novice plain-language explanation | Doctors + insights (but sprawling) | none | none (Troubleshoot Center = logs) | none | **Studio's unique strength, undermined by IA** | Fix Plan consolidation (beta.21) |
| Pre-slice risk narrative (design score, overhang/stability story) | Yes (mesh_diagnostics real math) | none | none | none | Whitespace held by Studio | Protect + demo it |
| Batch workflows | Batch prepare + pricing rollup | none | Multi-plate slicing | Bambu multi-plate | Differentiator for farms | Batch readiness report later |
| Printer monitoring/control | Moonraker read + user-confirmed control; health score; failure insights | Device tab (MQTT/cloud, camera) | Moonraker host support | Bambu cloud | Overlap growing; Studio = local-first + plain-language | Keep read-first posture; backend arming |
| Model discovery | Link-out browser + keyed metadata search (mostly dead) | Built-in Model Library + one-click print (cloud) | none | MakerWorld/Printables ecosystems | Snapmaker owns convenience; Studio can't win here | Keep link-out only; drop keyed search |

---

## 5. Current-state snapshot (for future diffing)

- Studio: v0.4.0-beta.20.3, trust PARTIAL/PENDING (not accepted); backend 321 tests + frontend 138 (per TRUST_STATUS).
- Snapmaker Orca: v2.3.4 (2026-06-11), base upstream 2.3.0, 2.3.5 in prep.
- Orca upstream: v2.4.1 (2026-06-28).
- BambuStudio: 2.8.0 public beta (2026-06-25); 2.7.1.62 stable.
- PrusaSlicer 2.9.6 (2026-06-25); Cura 5.13.0 (2026-05-28); lib3mf 2.5.0 (2026-02-24).
