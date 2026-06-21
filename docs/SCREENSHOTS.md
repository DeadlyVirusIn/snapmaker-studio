# Snapmaker Studio — Screenshot Package

Live screen capture must be done on the running app (the engine/sidecar can't be
driven headlessly, and a browser-only render lacks the sidecar for real Doctor
data). This doc gives **exact, reproducible** capture steps + per-shot specs so
anyone can produce the marketing set consistently.

## Setup (once)
1. Build + install: `cd desktop && npm run tauri build`, then run the installer
   (`..._0.3.0-beta.1_x64-setup.exe`).
2. Launch from Start Menu (or `npm run tauri dev` for iteration).
3. **Display:** 1440x900 logical, 100% scale, **light theme** (Settings -> Light)
   for high-contrast marketing; capture a dark-theme variant of each too.
4. Use a real file: `example.3mf` (Bambu, 5-color) and its converted output
   `example_SnapmakerU1.3mf`.
5. Window: maximize or 1280x800 client area; hide personal paths if needed.
6. Capture PNG at native res; export 2x for retina/marketing.

## Shots

### 1 — Dashboard (hero/workspace)
- **Route:** `/` (Dashboard).
- **Compose:** greeting + hero drop zone + 4 quick-action cards + "Continue
  working" project cards with status badges. Cursor off-frame.
- **Message:** "a real workspace, not a CLI."
- **File:** `dashboard.png` (+ `dashboard-dark.png`).

### 2 — Doctor analysis
- **Steps:** Open -> pick `example.3mf` -> land on LiveWorkspace; Doctor auto-runs.
- **Compose:** file name `example.3mf`, **READY** badge, **score 100** ring,
  recommended action, compatibility checklist, Source inspector (5 colours).
- **Message:** "instant, trustworthy diagnosis."
- **File:** `doctor.png` (+ dark).

### 3 — Conversion success
- **Steps:** click **Make U1-ready** -> wait for completion.
- **Compose:** green **"Saved U1-ready project"** card, output name
  `example_SnapmakerU1.3mf`, full path, **"Validated — ready to slice in
  Snapmaker Orca."**
- **Message:** "one click, done, verified."
- **File:** `conversion-success.png` (+ dark).

### 4 — Before / after comparison
- **Compose:** side-by-side, 50/50:
  - **Before:** Snapmaker Orca loading the original Bambu file showing the
    "Customized Preset" / "newer version" warnings.
  - **After:** Snapmaker Orca loading `example_SnapmakerU1.3mf` with **no
    warnings**, on the U1 plate.
- **Overlay labels:** "Bambu file -> warnings" vs "U1-ready -> zero warnings."
- **Message:** the core proof.
- **File:** `before-after.png` (composite; capture the two Orca states then
  compose in any image editor).

### 5 — Roadmap / vision screen
- **Compose:** a title card built from `docs/ROADMAP.md` pillars
  (Diagnose . Transform . Validate . Manage . Optimize) over a dark background
  with the brand mark (`docs/brand/icon.svg`) and tagline **"The workflow platform
  for modern 3D printing."**
- **Message:** platform ambition, not a one-trick tool.
- **File:** `roadmap.png`. (Designed card, not an app screen — assemble from the
  brand assets + roadmap text.)

## Output naming + location
Save to a local `marketing/screenshots/` folder (do **not** commit binaries to
the repo). Provide both light and dark for shots 1-3, the composite for 4, and
the designed card for 5; export @1x and @2x.

## QA checklist per shot
- No personal data in visible paths.
- Status badge colors match the verdict (READY = green).
- Real file names (`example.3mf` / `..._SnapmakerU1.3mf`), real score (100).
- Consistent window size + theme within each light/dark set.
- Crisp at 100% (no upscaling); 2x export for hero use.
