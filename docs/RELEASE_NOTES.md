# Snapmaker Studio v0.4.0-beta.21.2 — Preserve Creator Settings

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

This release fixes a trust issue reported by users: preparing a U1 profile copy could
silently replace slicer settings the model's creator had tuned (nozzle temperatures,
Z-hop, prime/wipe tower, print order), which could cause stringing, webbing and other
print-quality problems.

## What changed

- **Studio now preserves creator slicer settings by default** when preparing a U1
  profile copy. Temperatures, retraction, speed, acceleration, cooling, supports,
  layer height, flow, walls, infill, seam, ironing, brim, prime/wipe tower and print
  order are kept from the original file wherever technically possible.
- **You choose the preparation mode** before preparing:
  - **Preserve creator settings** (default) — keeps the creator's slicer settings
    where possible; Studio changes only the minimum U1 project wrapper fields needed
    for Snapmaker Orca.
  - **Apply Studio recommended U1 settings** — uses Studio's recommended U1 starter
    settings; this can change speed, temperature, retraction, supports, cooling and
    other print behavior. Never applied unless you choose it.
  - **Custom** — review the settings summary before preparing.
- **Every change is visible.** After preparing, Studio shows which settings were kept
  from the original file, which changed only for U1 compatibility, and which could
  not be carried over (with the reason).
- **STL files are clearly identified as geometry-only** — an STL does not include
  creator slicer settings, so Studio uses a U1 starter profile unless you choose
  another profile in Orca.
- Preparing with preserved creator settings may show Snapmaker Orca notices (for
  example a "Customized Preset" dialog) — that is the creator's tuned settings being
  kept, and the summary says so.

## Honest limits (unchanged)

- Studio prepares **U1 profile copies for review in Snapmaker Orca** — it does not slice.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**
- Object placement, spacing and bed-boundary fit remain **advisory / not verified by
  Studio** and must be checked in Snapmaker Orca before slicing.

## Download & verify

- Installer: `Snapmaker.Studio_0.4.0-beta.21.2_x64-setup.exe` (attached below)
- Size: 16,156,282 bytes
- SHA256: `febd9d1be9e3a96a9567cad987c5cf14352815868e3d29ca9ef030045d98aa4a`
- Also recorded in [docs/RELEASE_METADATA.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.21.2/docs/RELEASE_METADATA.md)
- The installer is not code-signed yet, so Windows SmartScreen may show "Unknown publisher". Download only from this GitHub release page and verify the checksum first:
  `Get-FileHash -Algorithm SHA256 .\Snapmaker.Studio_0.4.0-beta.21.2_x64-setup.exe`

Local-first · open source (MIT).
