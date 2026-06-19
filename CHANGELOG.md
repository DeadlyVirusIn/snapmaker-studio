# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.4.0-beta.1] - UNRELEASED

> Positioning: **the workflow platform for modern 3D printing** — understand any
> design, validate it, get it ready, and monitor your U1 (read-only). Snapmaker Orca
> still slices; Studio does not slice, send prints, or control printers. Independent
> open-source project, not affiliated with Snapmaker. Snapmaker U1 is the first
> printer target.

### Added
- **Project Intelligence** (`/insights`) — real, read-only design data: model dimensions (bounding box, mm), triangle count + complexity tier, detected materials (color + type), object/plate/color counts, source ecosystem, verdict and readiness score. No fake data — every value is derived from the file or the existing engine.
- **Validation Center** (`/report`) — a first-class readiness report: pass/warn/fail checks (incl. bed-fit vs the U1 270×270×270 build volume) plus a preservation answer to *What will be preserved? / What will change? / What might be lost?*
- **U1 Printer Hub** (read-only) — discover a networked Snapmaker U1 over its stock LAN-trusted Moonraker API and watch live status: print state, progress, bed + per-toolhead temperatures. **Monitoring only** — GET requests exclusively; no upload, no print start/stop, no printer modification. New `Printers` tab in the desktop app.
- **Canonical project representation** (`/canonical`) — the smallest source-neutral view of a design, the seam where multi-ecosystem support begins. A thin read-only layer over Project Intelligence that normalizes any source into one shape, including a Prusa INI (`Slic3r_PE.config`) reader so Prusa materials + printer model surface like Bambu's. Honest about limits: Prusa multi-material is *detected*, not yet preserved through conversion.
- **Adaptive Print Strategies** (`/strategies`, `/strategy/recommend`) — five research-backed, intent-based U1 print profiles (Fastest, Balanced (default), Best Quality, Maximum Reliability, Advanced). **Recommendation-only — Snapmaker Orca still slices.** Recommendation uses real design signals (color count, source, dimensions, complexity) and never fabricates duration, tool-change count, or purge volume. Print Strategy selector in the conversion flow: Simple Mode shows plain-language names + a *Recommended* badge; Advanced Mode shows the raw settings. Grounded in `docs/research/U1_PRINT_PROFILE_RESEARCH.md`.

### Changed
- **Product positioning rework** across app, README, docs, brand, and landing — from "U1 converter" to a workflow platform (Understand → Validate → Prepare → Monitor). Nav/labels reworded (e.g. "Batch prepare"); "U1 Control Center" → "Workflow Platform"; live engine status in the footer; global search wired to My Designs.
- **Honesty pass:** dropped "any printer / any file / Operating System / Perfect prints" overclaims; PrusaSlicer is shown as *detected* (full conversion = roadmap); added the "independent open-source project, not affiliated with Snapmaker" disclaimer to README, landing, app About, and brand docs.

### Fixed
- **Clean import in Snapmaker Orca.** Converting a customized Bambu/Orca project no longer triggers Orca's "Customized Preset" popup or the "Print By Object" collision warning:
  - clears `different_settings_to_system` (the "differs from system preset" marker carried from the source) during U1 normalization;
  - resets `print_sequence` to `by layer` (the U1 default; "by object" caused the collision warning).
  - The customized setting *values* are preserved — only the markers/sequence are normalized.
- **Validator hardened:** `is_u1_clean` (and the corpus gate) now fail if `different_settings_to_system` is non-empty or `print_sequence != "by layer"`, so these warning triggers can't regress silently. Regression tests added (real-world `KidsCrocsWithSupport` finding).
- **Legacy optimization safety reconciliation:** the bundled `u1_fast_prime_tower` optimization no longer carries `wipe_tower_max_purge_speed: 200` (now 90, the U1-documented safe cap) and its description matches its data. Tests now scan all bundled optimizations/profiles to enforce ≤90 mm/s tower speed, no auto-enabled no-sparse-layers, and no touching of protected per-design data. (Opt-in optimize mode only; default conversion unchanged.)

## [0.3.0-beta.1] - 2026-06-18

### Added
- **Desktop app** (Tauri + React + TypeScript): live Workspace (Doctor → Convert → Compare), Project Library, Batch convert, Settings, and a real-data Dashboard.
- **Project Library** — SQLite index of diagnosed/converted files; `/library` endpoints with name search and tag filter; auto-recorded on doctor/convert.
- **Batch conversion** — background job queue with live per-file progress; `/batch` + `/batch/status` endpoints.
- **Compare** in the desktop workspace — wires the existing `/diff` engine into a side-by-side panel (geometry, counts, normalized settings); STL inputs skip diff with a clear note.
- Bundled engine **sidecar** (PyInstaller-frozen, loopback + token), spawned by the desktop shell with zero orphan processes on exit.
- One-click **Windows installer** (NSIS) with the Studio Hub app icon.
- Official **Brand Identity Asset Pack** alignment across logo/icon/favicon/app-icon/hero/social SVGs, README, and landing page (7-stream spectrum, Primary Dark `#0A101C`, Inter).

### Changed
- README: product value proposition, Studio Hub hero, Input → Diagnose → Transform → Validate → Output workflow, real app screenshots, Architecture section, corrected roadmap.
- Landing page repaletted to the official palette.

### Fixed
- Clean Bambu/Orca 3MF → Snapmaker U1 conversion for a real-world corpus (112 files → 100% Doctor READY), incl. identity normalization, foreign-token scrub, and filament-array conform.

## [0.2.0] - 2026-06-17

### Added
- `doctor` — read-only compatibility check: will a file load cleanly on the U1, and if not, why (verdicts READY / REPAIRABLE / CONVERTIBLE / HIGH_RISK; `--json`)
- `diff` — read-only comparison of two projects (structure, geometry, settings, counts; `--json`)

### Changed
- README: badges, compatibility matrix, 30-second quick start, doctor & diff sections
- Added CONTRIBUTING guide and issue templates
- Public packaging metadata for the `snapmaker-studio` distribution

## [0.1.0] - 2026-06-17

### Added
- Repair incompatible 3MF projects into U1-ready projects (`u1convert repair --mode u1`)
- Convert STL files directly into native Snapmaker U1 projects (`u1convert repair part.stl`)
- Project integrity validation (`u1convert validate`)
- Preservation of painted and multi-colour models during repair
- Optional, reversible print-optimization profiles (`--mode optimize --opt-profile`)

### Notes
- Output is intended for Snapmaker Orca.
- OBJ/GLB input, batch processing, and a desktop GUI are planned (see the roadmap in the README).
