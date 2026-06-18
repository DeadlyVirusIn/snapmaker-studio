# Releasing Snapmaker Studio

Consolidated release process: the pre-release checklist, the Windows installer
smoke-test runbook, and the beta release plan/notes. (Merged from the former
RELEASE_CHECKLIST.md, INSTALLER_SMOKE_TEST.md, and BETA_RELEASE_PLAN.md.)

---

# Part 1 — Release Checklist

# Snapmaker Studio — Release Checklist (v0.3.0-beta.1)

Run after the PR `public-b3-conversion → main` merges. Nothing here is automated by
the PR — each is a deliberate manual gate. **No release/tag is created until every
box above the "Publish" line is ticked.**

## 1. Social preview upload
- [ ] Confirm `docs/brand/social-preview.png` (1200×630, Pack-aligned) renders correctly.
- [ ] GitHub → repo **Settings → General → Social preview** → upload the PNG.
- [ ] Verify the card by sharing the repo URL (or via a link debugger).

## 2. Windows installer smoke test
- [ ] On a clean Windows host: `cd desktop && npm ci && npm run tauri build`.
- [ ] NSIS `.exe` produced under `desktop/src-tauri/target/release/bundle/nsis/`.
- [ ] Installer icon shows the Pack app-icon (rebuilt `icon.ico`).
- [ ] Install → app launches → window title "Snapmaker Studio".
- [ ] Open an STL → Doctor → Convert → output `*_SnapmakerU1.3mf` saved; original intact.
- [ ] Open a Bambu/Orca 3MF → Compare shows diff; Library lists both; Batch converts 2 files.
- [ ] Close app → no orphan `snapstudio-api` process remains (Task Manager).
- [ ] Uninstall → clean removal.

## 3. Release tag
- [ ] Tag `v0.3.0-beta.1` on the merged `main` head.
- [ ] (Do **not** tag before the installer smoke test passes.)

## 4. Release notes
- [ ] Use the draft in Part 3 (below) ("Release notes").
- [ ] Create the GitHub release against the tag; mark **pre-release**.
- [ ] Attach the smoke-tested installer `.exe`.
- [ ] Confirm the README release badge resolves once the release exists.

## 5. Demo recording
- [ ] Record a 30–60s clip following `docs/DEMO_SCRIPT.md` (Input → Diagnose →
      Transform → Validate → Output on a real file).
- [ ] Export GIF/MP4; add to the release page and landing.

## 6. Innovation Fund submission
- [ ] Assemble assets per Part 3 (below) → "Innovation Fund submission assets":
      INNOVATION_FUND, PRODUCT_VISION/MISSION, ARCHITECTURE, ROADMAP, brand Pack,
      BETA_READINESS_REPORT + qa-beta screenshots, live repo + installer release, demo clip.
- [ ] Verify all links point to `main` (post-merge), not the feature branch.
- [ ] Submit.

---
**Publish line** — only proceed past here when 1–4 are complete and verified.
Steps 5–6 can follow the release.

---

# Part 2 — Windows Installer Smoke-Test Runbook

# Windows Installer Smoke-Test Execution Plan (v0.3.0-beta.1)

Detailed runbook for Part 1 (above). Run on a **clean Windows host**
(or a fresh VM / new user profile) with **no Python** and no prior Snapmaker Studio
install — that is the real test (bundled sidecar, no dev tooling).

## Prerequisites (build host)
- Windows 10/11 x64.
- Node LTS + npm; Rust toolchain (`rustup`, MSVC target); Tauri prereqs (WebView2).
- Python 3 **only on the build host** (to freeze the sidecar) — NOT on the test host.

## Build
```
cd backend && ./build-sidecar.ps1            # PyInstaller -> snapstudio-api.exe
cd ../desktop && npm ci && npm run tauri build
```
Expected artifact:
`desktop/src-tauri/target/release/bundle/nsis/Snapmaker Studio_0.3.0-beta.1_x64-setup.exe`

## Clean-room test matrix
Run on the **test host** (no Python). Tick each:

| # | Step | Expected | Pass |
|---|------|----------|------|
| 1 | Double-click the `.exe` | NSIS installer opens; icon = Studio Hub tile | ☐ |
| 2 | Complete install (current-user) | Installs without admin prompt | ☐ |
| 3 | Launch app | Window opens, title "Snapmaker Studio", dark UI | ☐ |
| 4 | Status bar | "Engine ready · v0.3.0-beta.1 · Local-only" | ☐ |
| 5 | Open `examples/sample_cube.stl` | Doctor → CONVERTIBLE, no crash | ☐ |
| 6 | Make U1-ready | Saves `sample_cube_SnapmakerU1.3mf`; original intact | ☐ |
| 7 | Open a Bambu/Orca `.3mf` | Doctor verdict + Compare shows diff | ☐ |
| 8 | Projects | Both files indexed; search/filter work | ☐ |
| 9 | Batch convert 2 files | Progress → "Done 2/2", both U1-ready | ☐ |
| 10 | Settings | Theme toggle (light/dark) works | ☐ |
| 11 | Close app | No orphan `snapstudio-api.exe` in Task Manager | ☐ |
| 12 | Re-open + close 3× | No orphan accumulation; no port conflict | ☐ |
| 13 | Uninstall | Clean removal; app dir gone | ☐ |

## Negative / edge checks
- ☐ Open a non-3MF/STL file via dialog → rejected by filter (only .stl/.3mf selectable).
- ☐ Convert with output dir on a different drive → still writes; original untouched.
- ☐ Kill the app process forcibly (Task Manager) → sidecar dies too (no orphan).

## Pass criteria
- Steps 1–13 all pass; no orphan sidecar; originals never overwritten; no crash.
- If any of 5–9 fail → **release blocker** (correctness/reliability).
- 10/12/edge failures → triage; cosmetic ones may ship as known issues.

## On pass
Proceed to Part 1 (above) (release + attach this exact
`.exe`). Record host OS build + a one-line result in the release notes.

## Status
⏳ **Not yet executed** — requires a Windows build host. No `.exe` artifact exists in
the repo (installers are not committed). This is the gating manual step for an
installer-backed public release.

---

# Part 3 — Beta Release Plan & Notes

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
| Product vision + mission | `docs/PRODUCT_VISION.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| Roadmap | `docs/ROADMAP.md` |
| Brand system | `docs/brand/` (Asset Pack + guidelines) |
| Proof / QA evidence | `docs/archive/BETA_READINESS_REPORT.md` + `docs/qa-beta/*` |
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
