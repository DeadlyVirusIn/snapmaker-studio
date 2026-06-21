# Windows release checklist (Snapmaker Studio)

> Why this exists: `tauri build` does **not** re-freeze the PyInstaller sidecar.
> If you forget to rebuild it, the installer ships a **stale sidecar** and new
> backend endpoints (e.g. Compatibility / Scale / Model Discovery / Print Quality
> / First Layer Doctors) return 404 at runtime even though the UI renders. v0.4.0-
> beta.4 shipped with this bug; always follow the steps below.

## 1. Version bump
- `desktop/package.json`, `desktop/src-tauri/Cargo.toml`,
  `desktop/src-tauri/tauri.conf.json` → the public version (no `-local`).
- `backend/pyproject.toml` → PEP 440 form (e.g. `0.4.0b5`).
- Commit the `Cargo.lock` change too.

## 2. Tests (must be green)
```
cd backend  && python -m pytest -q
cd desktop  && npm run test && npx tsc --noEmit && npx vite build
```

## 3. Build — ALWAYS refreeze the sidecar first
```
cd desktop
npm run release:windows      # = build:sidecar (pwsh scripts/build-sidecar.ps1) then tauri build
```
(equivalently: `cd desktop/scripts && pwsh build-sidecar.ps1`, then `cd desktop && npx tauri build`.)

Dev/local builds may skip the refreeze; **public releases must not.**

## 4. Mandatory bundled-sidecar endpoint smoke (do NOT publish if this fails)
Start the staged sidecar (`desktop/src-tauri/bin/snapstudio-api-*.exe`), read its
stdout handshake `{port, token}`, and confirm every route resolves (POST routes
need the `X-Auth-Token` header). None of these may 404:

- `GET  /health`             → 200
- `POST /plate_inspect`      → present (existing)
- `POST /compatibility_check`→ present
- `POST /scale_preview`     → present
- `POST /model_search`      → present (ok if providers disabled — no API keys)
- `POST /quality_check`     → 200 with a valid symptom
- `POST /first_layer_check` → 200 with a valid symptom

A missing route returns **404**; an executed route on bad input returns 400/500 —
that still proves the route exists. Also confirm **0 orphan sidecar processes**
after the app/sidecar closes.

## 5. Checksum + notes
- Compute final size + SHA256 of `Snapmaker Studio_<version>_x64-setup.exe`.
- Fill `docs/RELEASE_NOTES.md` and `docs/windows-install.md` (file name, size, SHA256).
- Grep release notes for paid/commercial model names — expect 0 hits.

## 6. Tag + publish
```
git commit -am "release: v<version>"
git tag -a v<version> -m "Snapmaker Studio v<version>"
git push origin main && git push origin v<version>
gh release create v<version> --title "Snapmaker Studio v<version>" \
  --notes-file docs/RELEASE_NOTES.md --prerelease --verify-tag \
  "desktop/src-tauri/target/release/bundle/nsis/Snapmaker Studio_<version>_x64-setup.exe"
```

## 7. Reminder
The installer is **unsigned** (SmartScreen "Unknown publisher"); ship the SHA256
so users can verify. Signing readiness: `docs/windows-code-signing.md`.
