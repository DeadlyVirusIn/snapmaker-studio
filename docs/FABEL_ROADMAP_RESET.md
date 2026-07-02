# Fabel Roadmap Reset — Snapmaker Studio

**Date:** 2026-07-01 · Companion to `docs/FABEL_DEVIL_ADVOCATE_REVIEW.md` and `docs/FABEL_REVIEW_FINDINGS_TABLE.md`.
**Status:** proposal only — does not replace `docs/ROADMAP.md` until Kunal approves.

Principle for every release below: *one theme, shipped and accepted, beats three themes pending.* Nothing enters beta.21 until beta.20.4 is ACCEPTED in TRUST_STATUS.md.

---

## beta.20.4 — "Land the release" (immediate patch)

P0/P1 acceptance blockers and truth repairs only. No features.

| Feature | Why | Evidence | Effort | Risk | Acceptance test |
|---|---|---|---|---|---|
| Run + record the 12-item installed-GUI acceptance checklist | 3 releases stuck at this gate | TRUST_STATUS.md all-unchecked checklist | Human session (~1-2h) | Findings may force fixes | All 12 items checked in TRUST_STATUS.md, status flips to ACCEPTED (or failures logged as new P0s) |
| Docs coherence sweep: fix TRUST_STATUS 20.2/20.3 mix-up; fill README SHA256; reconcile SHA256/size values; one version string everywhere | Contradictions kill the honesty pitch with judges | Findings table R2 | S | none | grep for old versions/hashes returns only CHANGELOG/history; README SHA256 matches released installer |
| Historical banners on stale docs (JUDGE_OVERVIEW, WHAT_TO_TEST_FIRST, docs/fund/*) or regenerate them | Fund docs claim "read-only, no printer control" — now false | R2 evidence | S (banner) / M (regenerate) | none | Every doc either describes the current build or carries "HISTORICAL — describes vX" banner in first 3 lines |
| Resolve bed-volume contradiction (270³ vs verified 271×335×275) | Two "hardware facts" disagree | CHANGELOG vs PRINTER_HUB_VERIFICATION | S | Needs the correct sourced number | One number, one source comment, used consistently in docs + constants |
| "Printer Hub" naming pass (kill "Printer Doctor" in copy) | In-app naming drift | FirstLayer.tsx, BeginnerWorkflow.tsx copy | S | none | grep "Printer Doctor" in desktop/src returns 0 |
| Rephrase "112/112" claim everywhere it appears | Reads as success guarantee | README, PROOF.md, INNOVATION_FUND | S | none | Every instance includes "structural gate, not print success" qualifier in same sentence |
| Container zip path-traversal audit | Orca had this exact bug class (PR #12860) | container.py in-memory today | S | Low | Written note in SECURITY.md: no extract-to-disk path exists / any path is sanitized; test added if applicable |
| Orca CLI spike (timeboxed 1 day, no shipping code) | Prices beta.22 | Upstream result.json writer; fork base 2.3.0 pre-CLI-fix | S | Spike may show fork CLI broken (that's still an answer) | Written spike note: fork CLI works? upstream CLI produces result.json for a prepared U1 copy? |

---

## beta.21 — "One clear path for a novice"

Highest-value simplification. Theme: a first-time U1 owner opens a model and knows what to do in 60 seconds.

| Feature | Why | Evidence | Effort | Risk | Acceptance test |
|---|---|---|---|---|---|
| IA collapse: Simple nav = Home / Check my model / My designs / Printer / Help; everything else under More tools | 12 nav items + 13 Doctor nouns = maze | Frontend inventory; NOVICE_UX_RED_TEAM | M | Power users grumble (Advanced mode unchanged) | New user test: open STL → reach verdict + next steps in ≤3 clicks; nav shows ≤5 primary items in Simple |
| Fix Plan page: one prioritized plain-language list per model, synthesized from intelligence_report | Answers "what do I do?" once, in one place | intelligence_report already aggregates | M | Prioritization logic needs care (severity ordering exists) | For 5 corpus files, Fix Plan shows ≤5 actions, each with a "do this in Studio/Orca" step; no banned false-ready words (test_public_claims extended) |
| Kill alias routes /doctor/pricing + /doctor/profit; remove Multi-Material explainer tab; merge first-layer surfaces to one entry point | Duplicate surfaces | Frontend inventory | S | Broken deep links (add redirects) | Routes redirect; only one first-layer entry in nav/report |
| Dead-end cleanup: one "Not supported yet — do this in Orca" component replaces disabled buttons + future-tense promises | Reads as broken | ScaleDoctor disabled button; FirstLayer future-tense copy | S | none | No disabled primary buttons; grep "coming"/"will live" in user-facing copy returns 0 |
| Narrowed AABB collision check (component-transform files only; instanced/source_object_id stays "unknown" with plain-language reason) | Shrink the biggest "unknown"; keep honesty | build_item_dims already computes world AABBs; prior failure was on instanced files | M | False positives → keep strictly to clear-overlap reporting with margin; fixture-gated | Known collision file flagged; known-good corpus files not flagged; instanced fixture still returns "unknown — verify in Orca"; tests added |
| Print-by-object collision advisory promotion + mixing-aware color caveat | U1 users report hardware-damage risk (fork issue #136); fork 2.3.3 mixing changes color advice | validation_report at_risk signal exists | S | none | By-object multi-object file shows explicit toolhead-collision warning; >4-color advice mentions mixing caveat |
| Simple mode default for new installs (one-time chooser) | Novice red-team P0 | NOVICE_UX_RED_TEAM #1 | S | Pending Kunal decision (review Q5) | Fresh install lands in Simple (or chooser); setting persists |
| Automated installed-app smoke (install → launch → open file → prepare copy → uninstall, scripted) | Removes the single-human release gate | Findings table R1 | M-L | Windows UI automation flakiness; scope to smoke, not full acceptance | Script runs on release candidate and produces pass/fail log; wired into RELEASE_CHECKLIST.md |
| Judge docs regenerated from accepted build + demo script pinned | Judge-facing accuracy | R2, R14 | S | none | JUDGE_OVERVIEW/WHAT_TO_TEST_FIRST match shipped build; demo script has zero live-site dependencies |
| Constants module for hardware/heuristic facts (U1_BUILD, toolheads, density, thresholds) with provenance | Single home for facts; enables freshness watcher | Backend inventory (scattered hardcodes) | S | none | One module; all consumers import it; provenance comment per constant |

---

## beta.22 — "Verified by Orca" (deeper Orca integration)

Theme: Studio's advisories get an authoritative second opinion without Studio ever slicing.

| Feature | Why | Evidence | Effort | Risk | Acceptance test |
|---|---|---|---|---|---|
| Opt-in "Verify with Orca" step: run Orca CLI --slice on the prepared copy, parse result.json (exit codes + per-plate warning_message), surface as plain language | Converts collision/layout "unknown" → verified; fixes the real P0 miss class | Upstream result.json (src/OrcaSlicer.cpp); collision exit codes; CLI fixed ≥2.3.2 | M-L | Fork CLI may be broken (spike from 20.4 decides engine: fork vs upstream vs unavailable); CLI runtime cost; version drift | Collision fixture: Studio reports Orca-confirmed collision with plate + message; clean file reports "verified by Orca vX"; Orca absent → honest "verification unavailable"; never blocks handoff |
| Cost/time from sliced output: parse .gcode.3mf / gcode metadata (user-sliced or CLI-produced) | Slicer-accurate cost replaces density heuristic | Orca PR #14238 format | M | Format variance across Orca versions — corpus-gate it | For a sliced file, Cost page shows Orca-sourced time/filament labeled with source + version; heuristic clearly labeled as fallback |
| .gcode.3mf awareness in Printer Hub (metadata, history, plateindex) | Orca 2.4+ primary job format | PRs #14238/#14404 | S-M | none | .gcode.3mf job shows correct name/plate/estimates in Printer Hub |
| Deep-link handoff via snapmaker-orca:// with path-spawn fallback | Robustness; kills path-guessing | Fork nsis/CFBundleURLSchemes protocol registration | S | Protocol behavior differences — keep fallback | Handoff works with Orca installed in non-default path; fallback still works |
| Profile freshness watcher (compare constants + prepared keys vs installed Snapmaker Orca vendor bundle) | Staleness insurance | Findings R5; PRs #14305/#14391/#14432 | M | Vendor bundle location/format changes | When bundle differs from Studio constants, Compatibility shows a "Studio's U1 facts may be behind Orca" advisory with details |
| Backend control arming (short-lived confirmation token required by _post control endpoints) | Safety gating below UI | moonraker.py comment; Findings R8 | M | API contract change — version both sides | Control call without token → refused + logged; UI flow unchanged for user; test added |
| CORS allowlist + CSP enable (start pre-GA hardening) | Documented pre-GA blockers | server.py:70; tauri.conf.json:16 | M | Regression risk in webview — smoke-test | CSP on, app functional in installed smoke; CORS restricted to app origin |

---

## Research track (no release promises, timeboxed investigations)

| Item | Goal | Exit criterion |
|---|---|---|
| Bambu/Orca instancing parser (source_object_id, model_instance transforms, assemble-vs-build) | Real layout math for instanced files | Fixture corpus (incl. the known collision-miss file) where computed placements match Orca CLI --export-3mf output; only then schedule as a feature |
| bbs_3mf.cpp watch process | Early warning on Bambu format changes | Documented ritual: on each BambuStudio release, diff bbs_3mf.cpp + run Studio corpus; log results in a FORMAT_WATCH.md |
| Snapmaker Orca TCP 13619 helper service | Understand Upload-and-Print channel; possible future integration | Protocol notes; no integration until documented/stable |
| Orca PartPlate semantics study (read-only, for parity checks — not reimplementation) | Know what "verified by Orca" covers vs doesn't | Written coverage map of Orca checks vs Studio advisories |
| Multi-plate per-plate verification | Upgrade multi-plate from blanket "warn" | Design note; depends on instancing research + CLI per-plate results |

---

## Stop / defer

| Item | Verdict | Why |
|---|---|---|
| In-app API-key metadata model search (Thingiverse/MMF/Cults3D keys) | **Stop (remove UI)** | Dead for most users ("key configured outside the app"); link-out browsing already covers discovery; maintenance + demo-failure surface |
| Native 3MF scaled export | **Defer indefinitely** | Blocked for good reasons; Orca --scale/--scale-to-fit + verify is safer and cheaper; keep preview |
| New Doctor pages (any) | **Stop** | New checks land as report sections, not nav nouns |
| Cura / Creality / Anycubic adapters | **Defer** | Detect-only is fine; no user pull evidenced; Bambu+Prusa cover the roadmap need |
| Color-mixing simulation | **Stop** | Fork feature is new + proprietary; a copy caveat suffices |
| Business/Profit expansion beyond current calculator | **Defer** | Cost accuracy (from sliced output) matters more than more pricing features |
| Full Orca PartPlate reimplementation | **Stop** | AGPL wall + moving target + CLI gives the verdict |
| Embedded slicing | **Stop (already out of scope)** | Hard rule; stays |
| Multi-printer support / Plugin SDK | **Defer to post-GA** | Phase-4 roadmap; irrelevant before acceptance + trust land |
| lib3mf adoption | **Defer** | Custom lxml reader works and is hardened; lib3mf adds nothing for the Bambu dialect (spec_production dormant since 2024) |

---

## Sequencing logic (why this order)

1. beta.20.4 exists because **nothing else matters while trust status is PENDING and docs contradict themselves** — it is the cheapest release with the highest judge impact.
2. beta.21 before beta.22 because the Fix Plan/IA work makes the Orca verification result *legible* — "verified by Orca" only lands if there is one obvious place to see it.
3. beta.22's CLI work is gated on a 1-day spike in 20.4 so the effort estimate is priced by evidence, not hope.
4. Instancing stays research because Bambu's format moved twice in 6 months (1-based IDs, assembly payloads) — building on it now means rework.
