# Overnight Differentiation Mission — Report

**Mission:** Increase Innovation Fund competitiveness through *product differentiation*,
implemented autonomously and shipped incrementally. Priorities P1–P5.

**Outcome:** P1–P4 implemented, tested, committed, and pushed to `main`. P5 (demo
readiness) wired end-to-end in the app; one screenshot capture remains. No data-loss,
release, credential, or irreversible-architecture blocker was hit. The engine and
converter were **not** rewritten — every feature is a read-only layer on top.

---

## What shipped

| # | Feature | Commit | Surface |
|---|---------|--------|---------|
| P1 | **Project Intelligence** — real geometry (dims, triangles, complexity), materials, counts, ecosystem, verdict/score | `7074e97` | `/insights` + Design Insights cards |
| P2 | **Validation Center** — pass/warn/fail checks (incl. bed-fit vs 270³), Preserved / Changes / At-risk | `06f6ccd` | `/report` + readiness card |
| P3 | **U1 Printer Hub** (read-only spike) — discover + live status (state, progress, bed + 4 toolhead temps) | `be312ab` | `/printer/discover`, `/printer/status` + new **Printers** tab |
| P4 | **Canonical project representation** — smallest source-neutral view; Prusa INI reader | `24ad4d0` | `/canonical` + `CanonicalProject` |

All four are **read-only**. The Printer Hub issues GET requests exclusively (proven by
test). The canonical layer reuses Project Intelligence and never mutates a file.

## Tests

`backend`: **40 passed**. New coverage:
- `test_api.py`: insights (STL + 3MF materials), report.
- `test_moonraker.py`: probe/status parsing against a mock Moonraker **and an assertion
  that only GET requests are ever issued** (the read-only guarantee).
- `test_canonical.py`: Prusa 3MF and STL both read into the canonical shape; INI
  multi-material splitting; honesty note present.

Desktop: `tsc --noEmit` clean after the Printers route + API client additions.

## Demo loop (P5)

The app now supports the full novice journey in one place:

**Open** a file → **Understand** it (Project Intelligence) → **Validate** it (Validation
Center: what's preserved / changed / at risk) → **Prepare** it (convert to a clean U1
3MF) → **View printer status** (Printers tab, live, read-only).

Existing screenshots cover Insights, Convert-done, My Designs, Batch
(`docs/qa-beta/rel_*.png`, `simple_*.png`). **Remaining capture:** the new Printers tab
(needs a live app + sidecar run; deferrable to a Haiku-model QA pass per project
testing policy).

## Honest limitations (no overclaiming)

- **Printer Hub is monitoring only.** No upload, no print start, no printer modification.
  It is a spike proving discovery + status reads, not a print-sending feature.
- **Prusa is detected, not preserved.** The canonical layer reads Prusa materials and
  printer model, and the converter still geometry-wraps Prusa input — the canonical
  view records this caveat explicitly rather than implying full Prusa support.
- The canonical representation is the *foundation* for multi-ecosystem work, not the
  finished abstraction.

## Blockers encountered

None that halt progress. Deferred items requiring a human / external step:
- **beta.2 release tag + installer** — awaits the user's Orca verification of
  `KidsCrocsWithSupport_SnapmakerU1_beta2.3mf` (release publication is an explicit STOP).
- **Printers-tab screenshot** — needs a live web-service/app start (project policy routes
  testing/service starts to the Haiku model).

## Next highest-value sprint

1. **Wire the canonical view + Validation Center into the desktop Printer Hub flow** so a
   user can validate, then see "this design fits your connected U1" — closing the loop
   between file readiness and the actual printer.
2. **Prusa preservation (beyond detection):** map Prusa multi-material objects through the
   converter so per-object color survives, using the canonical layer as the contract.
3. **Capture the Printers-tab screenshot** (Haiku QA run) and add it to `SCREENSHOTS.md`.
