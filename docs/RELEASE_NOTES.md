# Snapmaker Studio v0.4.0-beta.8

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**Scale Doctor size guidance for Snapmaker U1.**

## The Intelligence Layer for Open 3D Printing
Orca slices. Fluidd monitors. **Studio helps decide what to fix before you print.**
Before a layer is sliced, Studio reads your model and your Snapmaker U1 (read-only)
and surfaces likely print risks, what it costs, and what to sell it for — one
screen, plain language. Advisory only; not a guarantee of print success.

## New in beta.8
- **Scale Doctor now shows a "Size options for Snapmaker U1" table** — instead of
  just a maximum, you get four practical scale choices:
  - **Safest novice max** (recommended starting point),
  - **Still reasonable, tight margin**,
  - **Theoretical max, too close**, and
  - **Absolute limit, not recommended**.
- **Resulting dimensions per plate/object** for each scale choice, so you can see
  exactly how big each plate becomes.
- **The recommended option is highlighted**, and you can copy a scale percentage.
- **Multi-plate guidance** — Studio recommends scaling related parts together and
  warns when plates that need to fit together would be scaled differently.
- **Headroom warnings** — Studio flags when a scale leaves little room for brim,
  bed adhesion, or placement error.
- Scale analysis stays **read-only**: no file writes, no auto-scaling, no 3MF
  changes. This is a readiness estimate, not a guarantee of print success.

No 3MF writer/export behavior changed.

## Stability baseline (from beta.7)
beta.8 builds on beta.7's reliability work: hardened input validation, safer error
handling, geometry edge-case robustness, and verified release packaging.

## Feature set (carried forward)
- **Print Quality Doctor** and **First Layer Doctor** — advisory symptom checks.
- **Compatibility Doctor** — read-only detection of common U1 project issues.
- **Plate Color Remap** — verified safe copy; original never modified.
- **Model Discovery Hub** — search / link-out only; no downloads or imports.
- Visual 3D plate preview remains deferred (colour/part summary fallback).

## Important beta notes
- This is an **unsigned Windows beta**. Windows SmartScreen may show
  **"Unknown publisher."** Verify the installer SHA256 before installing.
- Doctors provide **advisory checks and guidance** — they do not guarantee print
  success and do not auto-edit slicer settings, printer profiles, or g-code.
- **Model Discovery is search / link-out only** — no downloads or imports; never
  scrapes.
- Code signing and additional desktop security hardening remain **planned** before a
  wider public launch.
- Real-world validation fixtures are not included in the repository (they may be
  copyrighted/commercial).

## Download (unsigned beta)
Only download from the official GitHub release, and verify the checksum.

```
File:    Snapmaker.Studio_0.4.0-beta.8_x64-setup.exe
Size:    16,072,354 bytes
SHA256:  6565119D737556BB7D2B1DCB723C1FEF4E00FA264BB36F42E2CBD6C9D1D95E6D
```

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.8/docs/windows-install.md).

_Beta — local-first; nothing leaves your computer._
