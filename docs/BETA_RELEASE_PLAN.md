# Snapmaker Studio — Beta Release Plan

**Date:** 2026-06-18 · **Branch:** `public-b3-conversion`

## Version
**`v0.3.0-beta.1`** — matches `desktop/src-tauri/tauri.conf.json` and the README
status badge. SemVer pre-release; next would be `v0.3.0-beta.2` (fixes) or
`v0.3.0` (GA).

## Release notes (draft — for the GitHub release body)

> ### Snapmaker Studio v0.3.0-beta.1
> **The workflow platform for modern 3D printing.** Drop in a Bambu / OrcaSlicer /
> PrusaSlicer / STL file and get a clean, validated Snapmaker U1 project — local-first,
> no cloud, no account.
>
> **Highlights**
> - **Doctor** — read-only U1 compatibility diagnosis with a verdict + score.
> - **Convert** — Bambu/Orca/Prusa/STL → clean U1 3MF; originals never overwritten.
> - **Compare** — diff original ↔ U1-ready (geometry, counts, normalized settings).
> - **Project Library** — every diagnosed/converted file auto-indexed, searchable.
> - **Batch convert** — many files at once with live per-file progress.
> - **Desktop app** — Tauri + React, dark-first; bundled engine sidecar (no Python).
> - One-click **Windows installer** (NSIS).
>
> **Proven:** real-world corpus of 112 files → 100% Doctor READY; former Bambu
> project opens in Snapmaker Orca with zero warnings.
>
> **Workflow:** Input → Diagnose → Transform → Validate → Output (validation always on).
>
> Local-first · open source (MIT). Full architecture in `docs/ARCHITECTURE.md`.

## Release checklist
- [ ] Tag `v0.3.0-beta.1` on `public-b3-conversion` head (`36b80be`).
- [ ] Build the Windows installer (`npm run tauri build`) → NSIS `.exe`.
- [ ] Smoke-test the installer on a clean Windows box (install → open → convert → uninstall).
- [ ] Create GitHub release, paste notes above, attach the installer `.exe`.
- [ ] Upload social preview (`docs/brand/social-preview.png`) in repo Settings.
- [ ] (Optional) open PR `public-b3-conversion` → `main`.

## Screenshots (ship with the release / store page)
From `docs/qa-beta/` (captured live against the engine):
`01_dashboard_dark`, `04_doctor_3mf`, `05_convert_done`, `06_compare_diff`,
`07_projects_populated`, `08d_batch_done`, `09_settings_dark`. Empty/responsive/
loading variants also available (`01d`, `01c`, `03L`).

## Demo assets
- **Landing page:** `docs/landing/index.html` (Pack-aligned; `landing_preview.png`).
- **Hero / social:** `docs/brand/hero.svg`, `docs/brand/social-preview.{svg,png}`.
- **Demo script:** `docs/DEMO_SCRIPT.md` (walkthrough for a recorded demo/GIF).
- **TODO (non-blocking):** record a 30–60s screen-capture demo GIF/MP4 from the
  script for the release page and Fund submission.

## Innovation Fund submission assets
| Asset | Source |
|---|---|
| One-pager / pitch | `docs/INNOVATION_FUND.md` |
| Product vision + mission | `docs/PRODUCT_VISION.md`, `docs/PRODUCT_MISSION.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Roadmap | `docs/ROADMAP.md` |
| Brand system | `docs/brand/` (Asset Pack + guidelines) |
| Proof / QA evidence | `docs/BETA_READINESS_REPORT.md` + `docs/qa-beta/*` |
| Live product | GitHub repo + installer release |

**Submission readiness:** all written/visual assets exist and are Pack-aligned. The
only producible-now gap is a recorded demo clip (scripted, not yet captured).

## Remaining blockers
**None for the code push** (already pushed + verified). For the *release/Fund*:
- Build + smoke-test the installer, then publish the tagged release (manual, needs a
  Windows build host).
- Upload social preview (web UI).
- Record the demo clip.

All are packaging/marketing steps — no code or functional blockers.
