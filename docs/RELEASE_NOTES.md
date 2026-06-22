# Snapmaker Studio v0.4.0-beta.9

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**Troubleshooting for prints that fail even with supports — plus reliability hardening.**

## The Intelligence Layer for Open 3D Printing
Orca slices. Fluidd monitors. **Studio helps decide what to fix before you print.**
Before a layer is sliced, Studio reads your model and your Snapmaker U1 (read-only)
and surfaces likely print risks, what it costs, and what to sell it for — one
screen, plain language. Advisory only; not a guarantee of print success.

## New in beta.9
- **"Fails even with supports" troubleshooting** added inside Print Quality Doctor.
- **Known-good print mode** — if a file has printed successfully before, Studio
  compares what *changed* instead of blaming the file or profile.
- Helps you compare: **filament that worked, filament that failed, failure stage,
  support contact, first layer, material condition, active print temperature,
  cooling, and toolhead/printer differences.**
- **Support-heavy and silk PLA guidance** — silk PLA can vary by brand and batch.
- Explains that **supports being enabled does not guarantee success.**
- Explains that **a low temperature shown after a stopped print may be cooldown**,
  not the active print temperature.
- Encourages **changing one setting at a time.**
- Frames **speed as a troubleshooting knob, not an automatic defect.**
- Advisory-only: **no file writes, no auto-fix, no slicer/profile/g-code edits, no
  guarantee of print success.**

## Reliability improvements
- Improved local API origin handling for the desktop app.
- Added a database migration foundation for future library updates.
- Added frontend/backend contract checks to reduce response-shape drift.
- Improved internal validation coverage.

## Feature set (carried forward)
- **Print Quality Doctor** and **First Layer Doctor** — advisory symptom checks.
- **Scale Doctor** — analysis-only resize preview + "Size options for Snapmaker U1".
- **Compatibility Doctor** — read-only detection of common U1 project issues.
- **Plate Color Remap** — verified safe copy; original never modified.
- **Model Discovery Hub** — search / link-out only; no downloads or imports.
- Visual 3D plate preview remains deferred (colour/part summary fallback).

## Important beta notes
- This is an **unsigned Windows beta**. Windows SmartScreen may show
  **"Unknown publisher."** Verify the installer SHA256 before installing.
- **Model Discovery is search / link-out only** — no downloads or imports; never
  scrapes.
- Doctors provide **advisory checks and guidance**, not print guarantees, and do not
  auto-edit slicer settings, printer profiles, or g-code.
- **CSP hardening and code signing remain planned** before a wider public launch.
- Real-world validation fixtures are not included in the repository (they may be
  copyrighted/commercial).

## Download (unsigned beta)
Only download from the official GitHub release, and verify the checksum.

```
File:    Snapmaker.Studio_0.4.0-beta.9_x64-setup.exe
Size:    16,079,395 bytes
SHA256:  89700D29A0788E16373A23F181D04607E6D722B95175F37163F0D4E1EFBE017D
```

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.9/docs/windows-install.md).

_Beta — local-first; nothing leaves your computer._
