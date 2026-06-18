# Snapmaker Studio — Release Readiness (v0.3.0-beta.1)

Status as of the pre-release hardening pass. Target: RC-beta on top of `main`
(Phase A + B1 already merged; conversion engine on `public-b3-conversion`).

## Gate matrix — ALL GREEN
| Gate | Result |
|---|---|
| `npm run build` | ✅ exit 0 (tsc + vite) |
| `cargo check` | ✅ exit 0 (1 cosmetic `mem::forget` warning) |
| backend tests | ✅ **10 passed, deterministic** (ran 3× clean) |
| validation corpus | ✅ **112 files, 100% clean, 0 failures** |
| `npm run tauri build` | ✅ NSIS installer produced |

## Versioning — consistent
`0.3.0-beta.1` across `desktop/package.json`, `desktop/src-tauri/Cargo.toml`,
`desktop/src-tauri/tauri.conf.json`, and the in-app StatusBar/Settings labels.
(Backend engine lib `pyproject` stays `0.2.0` — versioned independently by design.)

## Installer
- Artifact: `Snapmaker Studio_0.3.0-beta.1_x64-setup.exe` (~14.2 MB).
- NSIS, **per-user** install (no admin), WebView2 **downloadBootstrapper**.
- MSI intentionally disabled (`targets: ["nsis"]`) to avoid prerelease-version
  issues; NSIS is the primary, per spec.
- Metadata: productName "Snapmaker Studio", publisher "DeadlyVirusIn / Snapmaker
  Studio", copyright set.

## Sidecar packaging
- PyInstaller-frozen `snapstudio-api-...-msvc.exe` (~12.4 MB) with the **current
  engine** (B3B identity normalization, B3E geometry wrap, CORS).
- Bundled via Tauri `externalBin`; sits beside the app exe in the installer.
- **No system Python required.**
- Lifecycle: **zero orphans** on graceful close and force-kill (Windows Job
  Object `KILL_ON_JOB_CLOSE` + Python parent-watchdog). Verified on the installed
  app; `/health` -> `{"status":"ok","api_version":"api/1"}`.

## Issues found & fixed this pass
- **Flaky `test_server_doctor_requires_token` (WinError 10053).** Root cause: the
  sidecar replied `401` without draining the POST body -> Windows connection
  reset. Fixed by reading the request body before the auth check. Now
  deterministic (3x clean). This also hardens the real sidecar, not just the test.
- **`build-sidecar.ps1` `pyinstaller` not on PATH.** Switched to
  `python -m PyInstaller` (CI-robust).
- **Validator crashed on non-ASCII filenames** (cp1252 console). Made progress
  output ASCII-safe.

## Known blockers (pre-GA, not pre-beta)
- **Icon/branding:** placeholder icon in the build; replaced by the new brand
  system (this sprint, Phase 3) — needs rasterizing to `.ico`/`.png` and wiring
  into `tauri.conf.json` before GA.
- **Code signing:** unsigned -> Windows SmartScreen "Unknown Publisher". Acceptable
  for beta; **required for public GA**.
- **Manual GUI/Orca pass:** the in-app drag->convert and multi-file Orca
  zero-warning check are human steps (engine + lifecycle verified headlessly;
  Fox Sake confirmed zero-warning by the user).

## Recommendation
**Ready for an internal/beta RC and for PR to `main`.** Not yet public-GA:
ship the new icon and code signing first.
