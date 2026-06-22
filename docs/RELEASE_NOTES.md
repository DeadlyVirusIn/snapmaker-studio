# Snapmaker Studio v0.4.0-beta.7

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**Stability, validation, and release-reliability update.**

## The Intelligence Layer for Open 3D Printing
Orca slices. Fluidd monitors. **Studio helps decide what to fix before you print.**
Before a layer is sliced, Studio reads your model and your Snapmaker U1 (read-only)
and surfaces likely print risks, what it costs, and what to sell it for — one
screen, plain language. Advisory only; not a guarantee of print success.

### Doctor pillars
- **Project Doctor** — will it fit and print on your U1?
- **Printer Doctor** — a 0–100 health score from the U1's own signals.
- **Cost Doctor** — true cost, suggested price, and profit.

## New in beta.7
- Improved robustness for unusual or invalid model dimensions.
- Improved handling of large STL inputs.
- Improved validation for pricing and numeric inputs.
- Improved local API request validation and safer error handling.
- Improved backend dependency stability for reproducible builds.
- Improved Windows release packaging verification.
- Improved local API hardening.
- Reserved/internal endpoints are now documented more clearly.
- Workspace navigation decision documented for future cleanup.

No changes to 3MF writer/export behavior. No changes to Model Discovery scope.

## Feature set (from beta.5/beta.6, carried forward)
- **Print Quality Doctor** and **First Layer Doctor** — pick a symptom for likely
  causes, safe first checks, where to look in Orca, and what not to change blindly.
- **Beginner Workflow guidance** — "Get Started: from model to first print"; steps
  outside Studio (slicing, preparing the printer) are labelled as such.
- **Compatibility Doctor** — read-only detection of common U1 project issues.
- **Plate Color Remap** — verified safe copy; each colour tagged changing or
  protected; your original is never modified.
- **Scale Doctor** — analysis-only resize preview with fit and feature warnings.
- **Model Discovery Hub** — search / link-out only; no downloads or imports.
- Visual 3D plate preview remains deferred (colour/part summary fallback).

## Important beta notes
- This is an **unsigned Windows beta**. Windows SmartScreen may show
  **"Unknown publisher."** Verify the installer SHA256 before installing.
- **Model Discovery is search / link-out only** — it does not download or import
  third-party models, and never scrapes.
- Doctors provide **advisory checks and guidance** — they do not guarantee print
  success and do not auto-edit slicer settings, printer profiles, or g-code.
- Code signing and additional desktop security hardening remain **planned** before a
  wider public launch.
- Real-world validation fixtures are not included in the repository (they may be
  copyrighted/commercial).

## Download (unsigned beta)
Only download from the official GitHub release, and verify the checksum.

```
File:    Snapmaker.Studio_0.4.0-beta.7_x64-setup.exe
Size:    16,059,074 bytes
SHA256:  0447D6B26E9902AB5E1A6A2A7DB96DF89535658317EF0DA589BE610692F6A632
```

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.7/docs/windows-install.md).

_Beta — local-first; nothing leaves your computer._
