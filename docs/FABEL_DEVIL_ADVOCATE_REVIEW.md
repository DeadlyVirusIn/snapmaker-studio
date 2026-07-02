# Fabel Devil's-Advocate Review — Snapmaker Studio

**Date:** 2026-07-01
**Reviewer:** Claude Fable 5, acting as a hostile-but-fair external review panel (personas: CTO, Product Strategist, Principal Architect, Senior UX Researcher, Novice U1 User Advocate, Skeptical Innovation Fund Judge, Snapmaker Orca Power User, 3MF/Bambu Metadata Reverse Engineer, Slicer Integration Engineer, Security Engineer, QA Lead, Release Engineer, Open Source Ecosystem Analyst, Devil's Advocate).
**Inputs:** full repo + docs audit (4 read-only research passes over docs/, desktop/src, backend/), live GitHub research (3 research passes, 2026-07-01) over OrcaSlicer/OrcaSlicer, Snapmaker/OrcaSlicer, bambulab/BambuStudio, prusa3d/PrusaSlicer, 3MFConsortium (lib3mf + specs), Ultimaker/Cura, plus an open-source printability-tool landscape scan.
**Scope:** review and recommendations only. No code changed. No release published.

Companion documents:
- `docs/FABEL_REVIEW_FINDINGS_TABLE.md` — risk register, opportunity map, upstream tables, capability comparison.
- `docs/FABEL_ROADMAP_RESET.md` — beta.20.4 / beta.21 / beta.22 / research / stop-defer plan with acceptance tests.

---

## 1. Executive summary

Snapmaker Studio is an honest product wrapped in an unfinished release process and an over-branded information architecture. The engine's discipline is real and rare: `collision.py` is a deliberate, tested refusal to guess; readiness verdicts are blocked by "unknown" instead of faked; originals are never modified. That honesty is the product's core asset — and it is currently being spent on the wrong things.

Three structural problems dominate everything else:

**First, the release never lands.** beta.20.1, .20.2, and .20.3 all stalled at the same gate: a 12-item interactive installed-app acceptance checklist that only Kunal can run, and that is currently entirely unchecked. Trust status is "PARTIAL / PENDING — not accepted" for the third consecutive point release. Until installed-app acceptance is either passed or partially automated, every feature conversation is premature.

**Second, the documentation contradicts itself in ways a judge will find in minutes.** README carries a blank SHA256. JUDGE_OVERVIEW and WHAT_TO_TEST_FIRST describe beta.15 — five point releases stale. Fund docs (AUDIT, RELEASE_READINESS, SCORECARD) describe a beta.1-era product and explicitly say "Do NOT claim printer control — Studio is deliberately read-only," while the shipping product sends g-code and starts prints. Test counts disagree (166 vs 321+138). One doc says CSP shipped; another says CSP is disabled and a pre-GA blocker. CHANGELOG says the U1 bed is 270×270×270; the hardware verification record says 271×335×275. For a product whose entire pitch is *trustworthy honesty*, internal contradiction is the single fastest way to lose a judge.

**Third, the honesty is drifting toward uselessness at exactly the highest-stakes check.** Object-to-object spacing — the check that produced a real P0 miss (Orca flagged a collision Studio called fine) — returns "unknown" for every multi-object 3MF. That is honest. It is also the one question a multi-object user most needs answered. Meanwhile, upstream OrcaSlicer's CLI already computes the real answer (collision exit codes and per-plate `warning_message` in a machine-readable `result.json`). Studio does not need to reimplement Orca's PartPlate math; it needs to *borrow Orca's verdict*. This is the single biggest opportunity found in this review, and it converts Studio's most embarrassing "unknown" into a verified answer without violating the "Studio does not slice" rule (Orca still does the slicing; Studio reads the referee's scorecard).

The upstream picture is favorable but time-sensitive. No open-source pre-print advisory competitor exists (landscape scan found nothing above 3 stars). Neither upstream Orca, Snapmaker Orca, BambuStudio, PrusaSlicer, nor Cura has a plain-language pre-slice geometry advisor — the niche is open. But slicers are absorbing adjacent guardrails release by release (Orca 2.4.x collision-aware skirts and slice-time rejection of unsafe configs; Cura disabled-extruder warnings; Bambu import-time mesh repair), Snapmaker's own fork is adding cloud model-library one-click printing and firmware-level defect detection, and Bambu's 3MF dialect keeps mutating (1-based variant ID change; new assembly-guide payloads in 2.8.0) with zero standardization coming from the 3MF Consortium (production/slice specs dormant since 2024). Studio's window to define "the intelligence layer" is open now and will not stay open.

**The recommended reset in one line:** land beta.20.4 as an acceptance-and-truth release (checklist + docs coherence, nothing else); make beta.21 the novice-simplification release (collapse the Doctor sprawl into one Fix Plan); make beta.22 the Orca-verification release (CLI round-trip that turns "unknown" into "verified by Orca"); move Bambu instancing to a research track; stop building Doctor variants and in-app API-key model search.

---

## 2. Top 10 risks

Full register with severity/evidence/mitigation in `FABEL_REVIEW_FINDINGS_TABLE.md` §1.

1. **Acceptance deadlock (P0).** Three point releases in a row died at the same manual 12-item installed-GUI checklist. There is no automated installed-app smoke. Human single-point-of-failure on every release.
2. **Docs contradiction epidemic (P0 for judges).** Stale judge docs (beta.15), beta.1-era fund docs contradicting shipped printer control, blank README SHA256, three different SHA256/size values in the beta.20 family, 166-vs-459 test counts, CSP shipped-vs-disabled, 270³-vs-271×335×275 bed volume. Any one of these, found by a skeptical judge, undermines the "honesty" pitch categorically.
3. **Unsigned installer + SmartScreen.** First user experience is a Windows warning screen. Documented as deferred, but it interacts badly with risk #2: an "Unknown publisher" warning plus a blank SHA256 in the README is a trust hole a novice cannot cross.
4. **Collision "unknown" at the highest-stakes check.** Real P0 miss already happened (Orca collision warning missed by Doctor). `collision.assess_spacing` is a branch on object count, not a check. Honesty without help; multi-object users get no value where they most need it.
5. **Upstream profile staleness treadmill.** Orca upstream 2.4.1 corrected U1 bed to 270×270, added 0.2/0.6/0.8 nozzle profiles, and mass-rewrote profile setting IDs (PR #14432). Snapmaker Orca is based on upstream 2.3.0 and lags. Studio hardcodes `U1_BUILD = (270,270,270)`, 4 toolheads, and profile facts. No mechanism watches upstream profile changes — Studio's prepared copies can silently drift out of date.
6. **Bambu 3MF format mutation.** `bbs_3mf.cpp` changed repeatedly in 6 months: variant IDs switched to 1-based (silent semantic break), AMS arrangement metadata, filament-switcher keys, assembly-guide steps tree (2.8.0). Studio's regex/byte-count fast paths (`intelligence._bbox_and_triangles`, `fingerprint`, `plate_remap`) are the most brittle consumers. Plate count is already derived two inconsistent ways.
7. **Doctor sprawl.** ~13 distinct "Doctor" nouns; three overlapping first-layer surfaces; Cost/Pricing/Profit are three registry IDs for one page; "Printer Hub" vs "Printer Doctor" naming drift inside the app; heavy cross-linking reads as a maze. The brand device has become the complexity.
8. **Printer control safety enforced only in the UI layer.** Backend `_post` control functions have no server-side confirmation token or arming state; the stated safety gate is frontend confirmation dialogs. E-stop path (M112 via gcode/script) has never been fired on hardware. One frontend bug away from an unconfirmed command path.
9. **Model discovery fragility.** Six external sites; in-app metadata search requires API keys "configured outside the app" (dead for most users); link-out browser windows depend on third-party sites not blocking embedded/webview traffic; MakerWorld gates format versions server-side. Low control, real demo-failure surface.
10. **Orca handoff is Windows-only, path-guessed, fire-and-forget.** Hardcoded install paths; silent unavailability on macOS/Linux; no confirmation Orca loaded the file; no version negotiation — while Snapmaker Orca registers a `snapmaker-orca://` URL protocol Studio doesn't use.

Honorable mentions: "112/112 corpus" phrasing reads like a success guarantee to a fast-reading judge (it is an internal structural gate); hidden dead-end states in the UI ("3MF export not ready" disabled button, "will live in the Printer Doctor" future-tense promises, `—` cost pillars); CORS `*` on the loopback sidecar and CSP disabled remain open pre-GA security items.

---

## 3. Top 10 missed opportunities

Full map with effort/dependency/demo value in `FABEL_REVIEW_FINDINGS_TABLE.md` §2.

1. **Orca CLI verification round-trip (the headline).** Upstream Orca CLI (≥2.3.2; segfault before that) slices headless and writes `result.json` with typed exit codes — including `CLI_OBJECT_COLLISION_IN_LAYER_PRINT`, `CLI_OBJECTS_PARTLY_INSIDE`, `CLI_GCODE_PATH_CONFLICTS` — plus per-plate `warning_message`. Studio can offer an opt-in "Verify with Orca" step on the prepared copy and convert its collision/layout "unknown" into "verified by Orca 2.4.1" or a concrete named failure. This preserves every hard rule (Orca slices; Studio reads output; advisory language survives) and directly fixes the worst real-world miss. Caveat to verify: whether the *Snapmaker* fork's CLI works (fork is based on 2.3.0, pre-segfault-fix) — if not, upstream Orca can serve as verification engine while Snapmaker Orca remains the handoff target, or verification waits for a fork rebase.
2. **`snapmaker-orca://` deep-link handoff.** The fork's installer registers URL protocols on Windows and macOS. Replacing path-guessing `spawn()` with protocol launch (with path fallback) makes handoff more robust and potentially cross-platform.
3. **Cost/time from Orca's own output.** Orca 2.4.0 packages sliced jobs as `.gcode.3mf` with slice metadata. Parsing a user's sliced output (or CLI-produced gcode.3mf) gives real print time, filament usage per toolhead, and purge — replacing the hardcoded 1.24 g/cm³ PLA heuristic and making the Cost page slicer-accurate.
4. **`.gcode.3mf` awareness in Printer Hub.** Orca now uploads packaged 3MFs with a `plateindex` field (PR #14404). Printer Hub file metadata/history should recognize these, or it will misread the primary job format of Orca 2.4+ users.
5. **Narrowed collision honesty.** `geometry.build_item_dims` already computes world-space per-item AABBs correctly for component-based files. A conservative AABB *separation* check (report only clear overlaps, keep "unknown" for instanced/`source_object_id` files) shrinks the unknown from "all multi-object files" to "instanced files only" — honest and materially more useful. The prior failed attempt failed on instanced placement; scoping it out is the fix.
6. **Beginner "Fix Plan" page.** One prioritized, plain-language list per model ("3 things to do before you print") synthesized from all doctors — replaces the doctor maze for Simple mode. Most of the data already exists in `intelligence_report`.
7. **U1 pain-point checks the fork community is asking for.** Snapmaker Orca issue #136: print-by-object toolhead collisions risking hardware damage — precisely a pre-print advisory. Also color-count guidance is changing under Studio's feet: fork 2.3.3 shipped Full Spectrum color *mixing* (2-3 filaments blended), so "colors > 4 toolheads" advice needs a mixing-aware caveat.
8. **Profile freshness watcher.** A small check comparing Studio's hardcoded U1 facts and prepared-profile keys against the installed Snapmaker Orca vendor bundle (`resources/profiles/Snapmaker/`), warning when Studio is behind. Cheap insurance against risk #5.
9. **Judge demo hardening as a feature.** The 10-second demo report exists (good). Missing: one guaranteed-safe golden-path demo script pinned to the shipping build + docs regenerated from one version source. Judges get the "wow" only if nothing stale is discoverable.
10. **Batch readiness report for small print farms.** Batch prepare + pricing already exist; a one-page printable "batch readiness" summary is a cheap differentiator no slicer offers, aimed at the U1's multi-unit buyer.

---

## 4. Upstream repo review

### 4.1 Repos checked (live GitHub, 2026-07-01)

| Repo | Why it matters to Studio | Referenced in | Last checked | Priority |
|---|---|---|---|---|
| Snapmaker/OrcaSlicer | Downstream slicer; handoff target; U1 profile truth | docs/snapmaker-orca-integration.md, ROADMAP.md, README, desktop/src/lib/orca.ts | 2026-07-01 | P0 |
| OrcaSlicer/OrcaSlicer (canonical upstream; SoftFever redirects here) | Upstream of the fork; CLI; profile source; check overlap | docs/research/U1_PRINT_PROFILE_RESEARCH.md, DESIGN_INTELLIGENCE_V0_5_PLAN.md | 2026-07-01 | P0 |
| bambulab/BambuStudio | Bambu-family 3MF is Studio's best-supported input | backend detect.py/canonical.py, ARCHITECTURE.md, PROOF.md | 2026-07-01 | P0 |
| prusa3d/PrusaSlicer | Second ecosystem (detect + partial read) | canonical.py, ROADMAP.md, PRUSA_XL_AUDIT.md | 2026-07-01 | P2 |
| 3MFConsortium (lib3mf, spec_*) | Standards baseline for 3MF parsing | (not a dependency; custom lxml reader) | 2026-07-01 | P2 |
| Ultimaker/Cura | Third ecosystem (detect-only) | detect.py, ROADMAP.md | 2026-07-01 | P3 |
| Moonraker/Klipper (via fork inspection) | U1 API surface; Printer Hub | moonraker.py, PRINTER_HUB.md | 2026-07-01 | P1 |
| Model sites (Printables, Thingiverse, MyMiniFactory, Cults3D, Thangs, MakerWorld) | Find Models providers | model_search.py, MODEL_DISCOVERY_HUB.md | 2026-07-01 (not deep-audited) | P3 |

### 4.2 Key recent upstream enhancements and their impact

Full table in `FABEL_REVIEW_FINDINGS_TABLE.md` §3. Highlights:

- **Orca upstream v2.4.1 (2026-06-28):** U1 bed corrected to 270×270, new 0.2/0.8mm U1 nozzle profiles (PRs #14305, #14391); profile setting IDs mass-rewritten with CI guard (PR #14432). *Impact: Studio's hardcoded U1 facts and prepared profiles need a freshness mechanism.*
- **Orca upstream v2.4.0 (2026-06-20):** `.gcode.3mf` packaged job uploads (PR #14238) + `plateindex` on Moonraker uploads (PR #14404, 2.4.1); collision-aware skirts (PR #14130); unsafe by-object configs now rejected at slice time (PR #14333); Troubleshoot Center (PR #12416 — diagnostics, not printability). *Impact: overlap on collision-class checks is growing at slice time; pre-slice plain-language advisory remains unclaimed.*
- **Orca CLI (source-verified):** headless `--slice/--export-3mf/--arrange/--orient/--scale-to-fit/--downward-check` etc.; `result.json` with typed exit codes and per-plate `warning_message`; CLI unusable before 2.3.2 (segfault fix PR #12719); `--logfile` added in 2.4.0 (PR #13931). *Impact: opportunity #1.*
- **Orca 3MF security fix (PR #12860, v2.3.2):** path traversal in 3MF import → arbitrary file write. *Impact: audit `snapstudio_core.container` zip handling for the same class of bug.*
- **Snapmaker Orca v2.3.3 (2026-06-01):** Full Spectrum color mixing; ~15 new U1 filament profiles; local helper service on TCP 13619 for Upload-and-Print. **v2.3.0/2.3.1:** built-in Model Library with one-click cloud print; MQTT device channel; Flutter-webview device UI; firmware `DEFECT_DETECTION_*` macros (bed foreign-object detection at print start). Fork is based on upstream 2.3.0 (version.inc evidence); users request rebase (issue #291). Installer registers `snapmaker-orca://` URL protocol. *Impact: Snapmaker is moving up-stack (cloud, library, on-printer detection) — Studio's differentiation must stay at pre-print geometry intelligence and honesty; deep-link and 13619 are integration surfaces; color-mixing changes the "colors vs toolheads" advisory.*
- **BambuStudio 2.5.0→2.8.0-beta:** `bbs_3mf.cpp` churn — 1-based variant IDs (silent break), AMS arrangement metadata, `has_filament_switcher` key, assembly-guide steps tree serialized into project 3MFs (2026-06-24 commits). *Impact: tolerant read-only parsing is correct; add per-release corpus checks; watch `bbs_3mf.cpp` as the early-warning file.*
- **3MF Consortium:** lib3mf 2.5.0 (2026-02-24, WASM/Python bindings) but `spec_production`/`spec_slice` dormant since 2024 — no standardization of Bambu/Orca project metadata is coming. *Impact: vendor-tracking burden is permanent; plan for it.*
- **PrusaSlicer 2.9.6 / Cura 5.13:** no format or preflight moves of consequence (Cura's disabled-extruder warnings are the closest small guardrail). *Impact: low.*
- **Competitive scan:** no open-source pre-print checker with any traction (all ≤3 stars). *Impact: whitespace confirmed; the real competitor is slicers absorbing guardrails.*

---

## 5. Page / navigation simplification

Persona: Senior UX Researcher + Novice U1 User Advocate. Evidence from the route/nav inventory.

**Problems found**
- 12 primary nav items in Advanced mode; 7 carry doctor/tool branding. Novice cannot predict which page answers "will this print?"
- "Doctor" appears as ~13 distinct nouns (incl. code-level "Business Doctors", "Bed-Fit Doctor"). The metaphor stopped being a guide and became a taxonomy the user must learn.
- Three first-layer surfaces (standalone `/first-layer`, DesignInsights card, Printer history insights) with no explanation of difference.
- Multi-Material appears three ways; the `/colors` "Multi-Material" tab is an explainer that tells you to go somewhere else — a dead-end page.
- Cost/Pricing/Profit: three registry IDs, one page; `/doctor/pricing` and `/doctor/profit` silently resolve to Cost. Delete the aliases.
- Naming drift inside the app: registry/sidebar say "Printer Hub"; FirstLayer and BeginnerWorkflow copy say "Printer Doctor."
- Developer-shaped leakage: raw `setting_path` keys and "Evidence:" strings in Compatibility findings; monospace old→new settings dumps in LiveWorkspace diff; brand jargon ("The Intelligence Layer" as the sidebar subtitle) that only makes sense to the team.
- Dead-end/future-tense states visible to users: disabled "3MF export not ready" button; "Bed mesh / telemetry checks will live in the Printer Doctor."

**Recommended target IA (beta.21)**
- Simple mode nav = 5 items: **Home · Check my model (Fix Plan) · My designs · Printer · Help.** Everything else under one "More tools" group (already half-built).
- One umbrella check surface: Project Doctor becomes the only "Doctor" a novice sees; Compatibility, Scale, First Layer, Colors, Print Quality become *sections/tabs of the model report*, not sibling nav destinations. Keep deep routes for power users, remove them from primary nav.
- Rename for humans: "Cost & Pricing Doctor" → "Cost"; "Batch Prepare" stays Advanced-only; "Why Studio?" content folds into Help/About.
- Kill alias routes (`/doctor/pricing`, `/doctor/profit`), kill the Multi-Material explainer tab (link straight into workspace check), pick one name for Printer Hub and enforce it with a grep test.
- Replace visible dead-ends: disabled buttons and future-tense promises become a single quiet "Not supported yet — do this in Orca" line pattern (one component, consistent).
- Move raw `setting_path`/evidence dumps behind a "Details" disclosure in Simple mode.

---

## 6. Technical feasibility warnings

Persona: Principal Architect + 3MF Reverse Engineer + Slicer Integration Engineer.

- **Bambu instancing (`source_object_id`, per-instance transforms in `model_settings.config`, assemble-vs-build semantics) is genuinely hard** and Bambu keeps changing the surrounding format. Do not promise it in a beta. Research track only, driven by a fixture corpus of real files (the known collision-miss file is fixture #1). Success criterion: reproduce Orca's on-plate placement for the corpus, verified against Orca CLI `--export-3mf` output.
- **A full Orca PartPlate-equivalent boundary/collision engine is the wrong build.** Orca's own checks include wipe-tower interactions, sequential-print kinematics, and exclusion zones — a moving target reimplemented from AGPL code you cannot copy (MIT license wall). Borrow the verdict via CLI instead (opportunity #1); reserve native checks for the conservative AABB-separation case.
- **The Orca CLI integration has version hazards.** CLI segfaulted before upstream 2.3.2; Snapmaker fork is based on 2.3.0. Design the verify step to (a) detect Orca variant+version, (b) prefer upstream Orca if present, (c) degrade to "verification unavailable" honestly. Never make it mandatory.
- **Regex/byte-count 3MF fast paths are the brittleness hot-spot.** `fingerprint` counts `plate_*.json` files while `plate_remap` parses `plater_id` — already two sources of truth for plate count. Consolidate on one parsed representation before adding more consumers.
- **Support enforcers are string-counted, not parsed.** `compatibility.py` counts occurrences of `support_enforcer` in `model_settings.config`. Fine as a heuristic; do not let UI copy imply structural understanding of enforcer volumes.
- **Printer control gating should move down a layer.** Add a backend arming requirement (e.g., control endpoints refuse unless a short-lived confirmation token issued by an explicit user action accompanies the request). UI-only gating fails the Security Engineer's bar for a machine that can heat and move.
- **3MF zip handling:** replicate Orca's path-traversal fix class (PR #12860) — verify `container.py` never writes extracted names to disk unsanitized (it holds parts in memory today; keep it that way, and guard any future extract-to-disk path).
- **Hardcoded facts need one home.** `U1_BUILD`, toolhead count, PLA density, default $20/kg, 5% overhang threshold, aspect>4 tip rule — collect into one constants module with provenance comments, so the profile-freshness watcher has a single thing to check.

---

## 7. Roadmap reset (summary)

Full plan with per-item evidence/effort/acceptance tests in `docs/FABEL_ROADMAP_RESET.md`.

- **beta.20.4 — "Land the release."** Only acceptance blockers and truth repairs: pass the 12-item installed-GUI checklist; fix docs drift (single version/SHA256 source, refresh or clearly date-stamp judge and fund docs); README SHA256; one naming pass (Printer Hub); no new features.
- **beta.21 — "One clear path for a novice."** IA collapse (§5); Fix Plan page; dead-end cleanup; judge demo script pinned to the accepted build; narrowed AABB collision check (component-based files only).
- **beta.22 — "Verified by Orca."** Opt-in Orca CLI verification of the prepared copy with `result.json` import; `.gcode.3mf` awareness in Printer Hub; deep-link handoff; cost/time from sliced output when available.
- **Research track (no release promises):** Bambu instancing parser + fixture corpus; `bbs_3mf.cpp` watch process; profile-freshness watcher design; backend control arming.
- **Stop / defer:** in-app API-key model search (keep link-out); 3MF scaled export (route through Orca `--scale`/verify instead); new Doctor pages of any kind; Cura/Creality adapters; color-mixing simulation; further Business/Profit expansion.

---

## 8. Immediate action list (this week)

1. Run the beta.20.3 12-item installed-app acceptance checklist; record results in TRUST_STATUS.md whatever the outcome.
2. Fix TRUST_STATUS.md internal 20.2/20.3 mix-up; fill README SHA256 or remove the field until release; reconcile the three SHA256/size values.
3. Add a "HISTORICAL — describes beta.N" banner to JUDGE_OVERVIEW.md, WHAT_TO_TEST_FIRST.md, docs/fund/* or regenerate them; the read-only-vs-control contradiction in fund docs is the most dangerous single line in the repo.
4. Resolve the bed-volume contradiction (270³ vs verified 271×335×275) with one sourced number and a comment.
5. Grep-and-fix "Printer Doctor" vs "Printer Hub"; add a naming test.
6. Spike (timeboxed, 1 day): does Snapmaker Orca 2.3.4's CLI run `--slice` on a prepared U1 copy without crashing, and does upstream Orca 2.4.1 produce `result.json` for the same file? This one experiment prices beta.22.
7. Audit `container.py`/any extract path against the Orca 3MF path-traversal class (PR #12860).

---

## 9. What not to build

- **Orca PartPlate reimplementation.** AGPL-walled, moving target, and the CLI gives you the verdict for free.
- **Full Bambu instancing support on a beta timeline.** Research track; corpus first.
- **In-app metadata model search requiring user-provisioned API keys.** Dead feature for most users; keep sanctioned link-out browsing.
- **3MF scaled export (native).** Blocked today for good reasons; Orca CLI `--scale`/`--scale-to-fit` + verification is the cheaper, safer path.
- **More Doctors.** Any new check lands as a section of the model report, not a nav destination or a new noun.
- **Color-mixing simulation.** Fork's Full Spectrum feature is new and proprietary; a mixing-aware *caveat* in toolhead-fit copy is enough.
- **Embedded slicing.** Already out of scope; stays out.
- **Multi-printer / plugin SDK before GA.** Phase-4 roadmap items; irrelevant until acceptance and trust land.

---

## 10. Questions for Kunal

1. **Judge deadline:** is there a fixed Innovation Fund submission date? beta.20.4's scope (acceptance + truth) is sized for "soon"; a hard date could shrink it further.
2. **Code signing budget:** deferral is documented, but is a certificate (or Azure Trusted Signing) actually out of budget for the fund submission window? SmartScreen is a first-impression tax on every judge.
3. **Orca dual-install tolerance:** acceptable to recommend users/judges install *upstream* Orca alongside Snapmaker Orca if the fork's CLI proves broken, to power verification? Or must verification wait for a fork rebase?
4. **Hardware access cadence:** when can the M112 e-stop path be fired once on the real U1 (accepting the klipper restart) so "hardware-verified" covers the safety control too?
5. **Simple mode as default:** the novice red-team asked for it in beta.15 — is Simple-by-default (with a one-time chooser) acceptable for beta.21?
6. **Model search keys:** OK to remove the in-app API-key search UI entirely (keep link-out), or is a partner/API-key story planned?
7. **Fund docs:** regenerate to current build, or freeze-and-banner as historical records of the submitted beta.16.2? Both are honest; mixing eras is not.
8. **What does "win" look like for beta.22's demo:** the "unknown → verified by Orca" collision story, or the cost-from-sliced-output story? Both fit; the first is stronger for judges, the second stronger for daily users.

---

*Review complete. No code was modified. Recommendations only — claims cite repo files or live upstream references gathered 2026-07-01; upstream citations (PR/issue/commit IDs) are listed in FABEL_REVIEW_FINDINGS_TABLE.md.*
