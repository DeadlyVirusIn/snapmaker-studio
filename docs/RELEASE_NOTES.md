# Snapmaker Studio v0.4.0-beta.6

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**Reliability, validation, and beginner-workflow polish.**

## The Intelligence Layer for Open 3D Printing
Orca slices. Fluidd monitors. **Studio helps decide what to fix before you print.**
Before a layer is sliced, Studio reads your model and your Snapmaker U1 (read-only)
and surfaces likely print risks, what it costs, and what to sell it for — one
screen, plain language. Advisory only; not a guarantee of print success.

### Doctor pillars
- **Project Doctor** — will it fit and print on your U1?
- **Printer Doctor** — a 0–100 health score from the U1's own signals.
- **Cost Doctor** — true cost, suggested price, and profit.

## New in beta.6
- Improved app reliability and input validation.
- Fixed incorrect app version display in Settings and status areas.
- Improved Plate Color Remap validation when required colour selections are missing.
- Improved Scale Doctor validation for unusual scale inputs.
- Improved report output safety checks.
- Reduced unnecessary background polling during batch operations.
- Strengthened Windows release packaging checks so the bundled engine matches the
  desktop app.
- Updated product wording to make clear Studio provides advisory readiness checks,
  not print guarantees.

## Feature set (from beta.5, carried forward)
- **Print Quality Doctor (MVP)** — pick a symptom for likely causes, safe first
  checks, where to look in Orca, and what not to change blindly.
- **First Layer Doctor (MVP)** — pick what you see for likely causes, beginner
  checks, clearly-marked advanced checks, and slicer settings to inspect.
- **Beginner Workflow guidance** — a "Get Started: from model to first print" page;
  steps outside Studio (slicing, preparing the printer) are labelled as such.
- **Doctor navigation improvements** — every Doctor reachable from the sidebar with
  a "when to use each" overview.
- **Plate Remap confidence improvements** — each colour tagged changing or
  protected; verified safe copy, original untouched.
- **Model Discovery Hub polish** — clear provider/key state and privacy note.
- **Scale Doctor guidance improvements** — plain material-multiplier estimate and
  explicit fit/feature warnings.
- **Compatibility Doctor** — read-only detection of common U1 project issues.
- Visual 3D plate preview remains deferred (colour/part summary fallback).

## Important beta notes
- This is an **unsigned Windows beta**. Windows SmartScreen may show
  **"Unknown publisher."** Verify the installer SHA256 before installing.
- **Model Discovery v1 is search / link-out only** — it does not download or import
  third-party models, and never scrapes.
- Doctors provide **advisory checks and guidance** — they do not guarantee print
  success.
- Advisory Doctors **do not auto-edit** slicer settings, printer profiles, or g-code.
- Code signing and additional desktop security hardening remain **planned** before a
  wider public launch.
- Real-world validation fixtures are not included in the repository (they may be
  copyrighted/commercial).

## Download (unsigned beta)
Only download from the official GitHub release, and verify the checksum.

```
File:    Snapmaker.Studio_0.4.0-beta.6_x64-setup.exe
Size:    16,057,930 bytes
SHA256:  E9F6E0A6FA33908E532655F42117B043CD6065ED56CF9FE3D48A1792A3C9A547
```

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.6/docs/windows-install.md).

_Beta — local-first; nothing leaves your computer._
