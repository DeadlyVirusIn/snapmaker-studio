# Snapmaker Studio v0.4.0-beta.11

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**One-click "Open in Snapmaker Orca" — hand a prepared U1 copy straight to the slicer.**

## The Intelligence Layer for Open 3D Printing
Snapmaker Orca slices. Fluidd monitors. **Studio helps decide what to fix before you print.**
Before a layer is sliced, Studio reads your model and your Snapmaker U1 (read-only)
and surfaces likely print risks, what it costs, and what to sell it for — one
screen, plain language. Advisory only; not a guarantee of print success.

## New in beta.11
- **One-click "Open in Snapmaker Orca."** Once Studio has prepared a validated U1
  copy, hand it straight to Snapmaker Orca to slice. Studio detects an installed
  Snapmaker Orca at its real install location and launches it with the prepared
  file — a one-way handoff. **Studio checks the model first. Snapmaker Orca slices
  it next.** Studio does not slice and does not control Orca.
- **Graceful fallbacks.** If Snapmaker Orca isn't installed, the card shows
  **Install Snapmaker Orca** (official releases) and **Copy path** instead. Clear
  error states for "not installed," "prepared file missing," and "couldn't launch."
- **The install path is never shown in the UI**, and the handoff only appears once
  a prepared/safe-copy file actually exists.
- **Snapmaker Orca vocabulary alignment.** Product-specific copy (Compatibility
  Doctor, the handoff card) now consistently says "Snapmaker Orca," matching the
  verified Snapmaker U1 profile (name, 270 mm Z, 4 toolheads).

## Carried forward from beta.10
- Approved-site **Model Browser v1** — browse trusted sites in a locked in-app
  window; manual download/open only; no scraping, no auto-import, no API keys.
- **"Fails even with supports"** troubleshooting + known-good print comparison in
  the Print Quality Doctor.
- **Scale Options Ladder**, **Compatibility Doctor**, **Project Doctor**, and
  **Plate Color Remap** (verified safe copy; original never modified).
- Local-API and reliability hardening.

## Important beta notes
- This is an **unsigned Windows beta**. Windows SmartScreen may show
  **"Unknown publisher."** Verify the installer SHA256 before installing.
- The Model Browser is **approved-site browsing only** — manual download/open;
  no API keys, no auto-import, no download interception; never scrapes.
- Doctors provide **advisory checks and guidance**, not print guarantees, and do
  not auto-edit slicer settings, printer profiles, or g-code.
- "Open in Snapmaker Orca" is a one-way file handoff you initiate; Studio never
  passes slicing commands or controls Orca.
- **CSP hardening and code signing remain planned** before a wider public launch.

## Download (unsigned beta)
Only download from the official GitHub release, and verify the checksum.

```
File:    Snapmaker.Studio_0.4.0-beta.11_x64-setup.exe
Size:    16,092,069 bytes
SHA256:  9818f1a8ea5507257a58831c419303d32014bd34efb0f81c2bcde27cd5d78a56
```

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.11/docs/windows-install.md).

_Beta — local-first; nothing leaves your computer._
