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
- [ ] Use the draft in `docs/BETA_RELEASE_PLAN.md` ("Release notes").
- [ ] Create the GitHub release against the tag; mark **pre-release**.
- [ ] Attach the smoke-tested installer `.exe`.
- [ ] Confirm the README release badge resolves once the release exists.

## 5. Demo recording
- [ ] Record a 30–60s clip following `docs/DEMO_SCRIPT.md` (Input → Diagnose →
      Transform → Validate → Output on a real file).
- [ ] Export GIF/MP4; add to the release page and landing.

## 6. Innovation Fund submission
- [ ] Assemble assets per `docs/BETA_RELEASE_PLAN.md` → "Innovation Fund submission assets":
      INNOVATION_FUND, PRODUCT_VISION/MISSION, ARCHITECTURE, ROADMAP, brand Pack,
      BETA_READINESS_REPORT + qa-beta screenshots, live repo + installer release, demo clip.
- [ ] Verify all links point to `main` (post-merge), not the feature branch.
- [ ] Submit.

---
**Publish line** — only proceed past here when 1–4 are complete and verified.
Steps 5–6 can follow the release.
