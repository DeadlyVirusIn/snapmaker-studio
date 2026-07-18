# Snapmaker Studio v0.4.0-beta.21.3 — Preserve Settings Summary Cleanup

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

This release cleans up how the Prepare summary reports preserved creator settings,
based on feedback from testing v0.4.0-beta.21.2.

## What changed

- **Preserved settings are no longer listed as "Changed".** Creator temperature and
  retraction values that Studio only maps onto the U1's four-toolhead layout — with
  the creator's values preserved — now appear under **Kept from the original file**,
  with the note: *"Creator temperature values were preserved and mapped to the U1
  toolhead layout."* They no longer appear under "Changed for U1 compatibility".
  A setting appears as changed only when its actual value changed.
- **Clearer summary by default.** The "Adjusted for U1 project compatibility"
  section now uses plain language (printer identity changed to Snapmaker U1, U1
  machine G-code applied, toolhead layout mapped). Raw setting keys and exact
  old/new values moved behind a **Technical detail** disclosure you can expand.
  Any real print-affecting change stays visible in the default view, and
  **Could not carry over** is always shown.
- **No more doubled output name.** Preparing a file whose name already ends in
  `_SnapmakerU1` no longer produces `..._SnapmakerU1_SnapmakerU1.3mf` — Studio now
  numbers the copy instead (for example `..._SnapmakerU1_2.3mf`).
- **Wording cleanup.** Removed overclaiming wording from the Dashboard prepare step
  and the Design Insights page.

## Honest limits (unchanged)

- Studio prepares **U1 profile copies for review in Snapmaker Orca** — it does not slice.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**
- Object placement, spacing and bed-boundary fit remain **advisory / not verified by
  Studio** and must be checked in Snapmaker Orca before slicing.

## Download & verify

- Installer: `Snapmaker.Studio_0.4.0-beta.21.3_x64-setup.exe` (attached below)
- Size: 16,160,350 bytes
- SHA256: `7f69f6716d9a042973bffb0468cc49d13cd17fa273d0a6d283f7f97d9b4cad92`
- Also recorded in [docs/RELEASE_METADATA.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.21.3/docs/RELEASE_METADATA.md)
- The installer is not code-signed yet, so Windows SmartScreen may show "Unknown publisher". Download only from this GitHub release page and verify the checksum first:
  `Get-FileHash -Algorithm SHA256 .\Snapmaker.Studio_0.4.0-beta.21.3_x64-setup.exe`

Local-first · open source (MIT).
