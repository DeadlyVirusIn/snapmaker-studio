# Snapmaker Studio — Beta Readiness Report

**Date:** 2026-06-18 · **Build:** v0.3.0-beta.1 · **Mode:** runtime end-to-end QA

End-to-end verification of all nine surfaces against the **real** Python sidecar
(`snapstudio_api` on loopback) driving the production React build (`vite preview`)
through a Tauri-IPC shim, so every data-backed state below is live engine output —
not mocked. Screenshots in [`qa-beta/`](../qa-beta/).

## Method
- Sidecar started on an **empty** library dir (`SNAPSTUDIO_DATA_DIR`) to prove the
  genuine empty state, then populated by real conversions during the run.
- Headless Chromium (Playwright) drove navigation, file open (Doctor → Convert →
  Compare), Library, and Batch; transient states (loading/progress) forced via a
  request-delay route; error states forced with a bad auth token.
- Backend unit/integration suite: **25 passed** (`pytest -q`). Frontend build green.

## Feature status

| # | Area | Status | Evidence |
|---|------|--------|----------|
| 1 | Dashboard | ✅ Pass | **100% real data** — recents, activity, library counts, sidebar Recent all from the live library; `01_dashboard_dark`, `01b_dashboard_light`, `01c_dashboard_narrow`, `01d_dashboard_empty`, `01e_dashboard_activity` |
| 2 | Projects | ✅ Pass | empty + populated + search + filter; `02_projects_empty_dark`, `07_projects_populated`, `07b_projects_search`, `07c_projects_narrow` |
| 3 | Workspace | ✅ Pass | file load, source panel, nav; `03_workspace_stl_doctor`, `04_doctor_3mf` |
| 4 | Doctor | ✅ Pass | READY (3MF, score 100) + CONVERTIBLE (STL), real verdicts; `04_doctor_3mf`, `03_workspace_stl_doctor`, loading `03L_doctor_loading` |
| 5 | Convert | ✅ Pass | saved U1 project + validated_ok, originals preserved; `05_convert_done` |
| 6 | Compare / Diff | ✅ Pass | geometry-preserved, side-by-side counts, 13 settings normalized; STL correctly skips diff; `06_compare_diff`, `06b_compare_stl_note` |
| 7 | Project Library | ✅ Pass | auto-records doctor/convert; 2 real entries, search/filter; `07_projects_populated`, `07b_projects_search` |
| 8 | Batch Conversion | ✅ Pass | stage → progress → done 2/2 (2 ok), per-file U1-ready; `08_batch_empty`, `08b_batch_staged`, `08c_batch_progress`, `08d_batch_done`, `08e_batch_narrow` |
| 9 | Settings | ✅ Pass | theme (Light/Dark), output folder, keep-originals (always on), about; `09_settings_dark`, `09b_settings_light` |

### State coverage (per requirement)
| State | Result |
|---|---|
| Navigation | ✅ sidebar links Dashboard/Projects/Batch + in-app routing verified (asserted) |
| Empty | ✅ Projects "Your library is empty"; Batch "No files queued" |
| Loading | ✅ Doctor "Analyzing compatibility…" spinner+skeleton (`03L`); Projects "Loading your library…"; Batch "Converting…" (`08c`) |
| Error | ✅ Doctor "Couldn't analyze this file · doctor failed (401) · Retry" (`E1`); Projects "Couldn't load your library · Retry" (`E2`) |
| Dark mode | ✅ default; all surfaces |
| Light mode | ✅ Settings toggle; `01b`, `09b` |
| Responsive | ✅ 820px-wide captures, grids reflow; `01c`, `07c`, `08e` |

## Screenshots (`docs/qa-beta/`)
`01_dashboard_dark` · `01b_dashboard_light` · `01c_dashboard_narrow` ·
`01d_dashboard_empty` · `01e_dashboard_activity` · `02_projects_empty_dark` · `03_workspace_stl_doctor` · `03L_doctor_loading` ·
`04_doctor_3mf` · `05_convert_done` · `06_compare_diff` · `06b_compare_stl_note` ·
`07_projects_populated` · `07b_projects_search` · `07c_projects_narrow` ·
`08_batch_empty` · `08b_batch_staged` · `08c_batch_progress` · `08d_batch_done` ·
`08e_batch_narrow` · `09_settings_dark` · `09b_settings_light` ·
`E1_doctor_error` · `E2_projects_error`

## Dashboard Reality Sprint (resolved)
The previously-flagged mock content is **eliminated**. Dashboard now pulls
everything from the live library (`/library`):
- **Continue working** recents, **Activity** feed (derived from each project's real
  `last_action` + `updated_at`), and **Library** insight counts (total / U1-ready /
  needs-work) are all genuine.
- **Sidebar** "PINNED" mock list → **"Recent"** from the live library; "New project"
  stub → "Open a model".
- Verified live: empty state ("No projects yet" / "0 projects"); after two real
  conversions → "2 projects · 1 U1-ready · 1 need work", activity "Converted
  sample_cube.stl to U1". No fabricated names/numbers.
- The mock detail route (`/projects/:id`) and its fake checks/compare/history page
  were removed. **`mock.ts`, `ProjectCard.tsx`, `Workspace.tsx` deleted; zero
  `MOCK_*` strings remain in `desktop/src` (verified by grep).**

## Known issues
1. **Library error is slow to surface (~5–8 s).** Projects uses TanStack Query with
   default 3× retry + backoff, so a failing `/library` call shows "Loading…" for
   several seconds before the error card. Doctor errors surface immediately (no
   retry). Functionally correct, just slow to fail.
2. **Status bar shows "Engine ready" under auth failure.** `/health` is
   unauthenticated, so the footer reads ready even when token-gated calls 401.
   Cosmetic only.

## Release blockers
**None functional.** All nine areas work end-to-end against the live engine with
correct empty/loading/error handling and originals never overwritten. No crashes,
no broken routes, no data-loss paths, and no mock/demo data in production.

## Polish items (post-beta, non-blocking)
- Lower the library query retry (or show a "retrying…" hint) so errors surface fast.
- Footer should reflect auth/connectivity, not just `/health`.
- Persist a real per-project history (the `library.history` table exists) to enrich
  the Activity feed beyond last-action.

## Recommendation
**BETA READY — READY TO PUSH.** The core promise — drop any STL/Bambu/Orca file in
and get a clean, validated Snapmaker U1 project, with Doctor / Convert / Compare /
Library / Batch all working locally — is verified live, and the Dashboard now shows
only genuine data (zero `MOCK_*`). The two remaining known issues are cosmetic and
non-blocking. No credibility gaps remain for a beta release.
