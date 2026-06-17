# Snapmaker Studio — desktop (Phase 1 scaffold)

Native desktop shell: **Tauri (Rust) → React/TypeScript UI → local Python sidecar → `snapstudio_core` engine.**

Phase 1 proves the architecture end-to-end: launch the app, pick or drop a file, run **Doctor**
through the sidecar, and show a plain-language verdict. No conversion button yet.

## Prerequisites
- Python 3.13 with the engine installed: `pip install -e ../backend`
- Node.js + npm
- Rust toolchain (`cargo`, `rustc`) and the Tauri v2 system prerequisites for your OS

## Run (dev)
```bash
cd desktop
npm install
npm run tauri dev
```
On launch the Rust shell spawns `python -m snapstudio_api` from `../backend`, reads its
`{"port","token"}` handshake, and the UI calls the sidecar over `127.0.0.1`.

## How it works
- `src-tauri/src/main.rs` — spawns the sidecar, captures the handshake, exposes `get_api_info`.
- `src/api.ts` — fetches port/token via `get_api_info`, then calls `/health` and `/doctor`.
- `src/App.tsx` — drag-drop / browse, "Run Doctor", verdict card (READY / REPAIRABLE / CONVERTIBLE / HIGH_RISK).
- Sidecar: `../backend/snapstudio_api` (loopback-only, token-gated `/doctor`, open `/health`).

## Security (Phase 1)
- Sidecar binds `127.0.0.1` only; `/doctor` requires the per-launch `X-Auth-Token`.
- No network egress; no account; engine stays offline and read-only for Doctor.

## Packaging notes (future — not done in Phase 1)
- **Sidecar:** freeze `snapstudio_api` (+ `snapstudio_core` + bundled `data/`) with **PyInstaller**;
  ship the binary as a **Tauri `externalBin` sidecar**; verify `importlib.resources` data resolves when frozen.
- **App:** `npm run tauri build` -> Windows NSIS/MSI first; macOS `.dmg`/notarized; Linux AppImage.
- **Auto-update:** wire Tauri's built-in signed updater against GitHub Releases.
- In `main.rs`, replace the dev `python -m snapstudio_api` spawn with the bundled sidecar path.

## Status
Build-unverified in this scaffold (no `npm install` / `cargo build` run here). The Python sidecar
is verified independently (`backend/tests/test_api.py`). Run the dev command above to launch.
