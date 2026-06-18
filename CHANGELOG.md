# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

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
