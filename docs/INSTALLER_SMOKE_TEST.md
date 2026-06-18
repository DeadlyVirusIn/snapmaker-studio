# Windows Installer Smoke-Test Execution Plan (v0.3.0-beta.1)

Detailed runbook for `docs/RELEASE_CHECKLIST.md` §2. Run on a **clean Windows host**
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
Proceed to `docs/RELEASE_CHECKLIST.md` §3 (tag) → §4 (release + attach this exact
`.exe`). Record host OS build + a one-line result in the release notes.

## Status
⏳ **Not yet executed** — requires a Windows build host. No `.exe` artifact exists in
the repo (installers are not committed). This is the gating manual step for an
installer-backed public release.
