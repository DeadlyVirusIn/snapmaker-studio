# Snapmaker Studio v0.4.0-beta.21.1 — Readiness Wording Cleanup

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

A small wording patch on top of beta.21. No feature changes.

## What changed

- **Validation Center wording clarified** so fit/profile checks are not described as
  print-ready. "Prints on Snapmaker U1 — Ready as-is / Ready after preparation" now
  reads **"Fits U1 profile checks — review in Orca before slicing"** (or "prepare a
  U1 copy and review in Orca"). A watertight mesh is described as **"readable by the
  slicer"**, not "clean to slice".
- **Orca review language stays prominent** before slicing — a passing profile check
  never means a print is guaranteed, especially while object spacing and plate
  layout remain advisory.
- New tests pin this wording so it cannot regress.

## Honest limits (unchanged)

- Studio prepares **U1 profile copies for review in Snapmaker Orca** — it does not slice.
- **Originals are never modified** — preparing a model writes a new copy.
- **No print-success guarantees.**
- Object placement, spacing and bed-boundary fit remain **advisory / not verified by
  Studio** and must be checked in Snapmaker Orca before slicing.

## Download & verify

- Installer: `Snapmaker.Studio_0.4.0-beta.21.1_x64-setup.exe` (attached below)
- SHA256 and size: see [docs/RELEASE_METADATA.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/main/docs/RELEASE_METADATA.md)
- The installer is not code-signed yet, so Windows SmartScreen may show "Unknown publisher". Download only from this GitHub release page and verify the checksum first:
  `Get-FileHash -Algorithm SHA256 .\Snapmaker.Studio_0.4.0-beta.21.1_x64-setup.exe`

Local-first · open source (MIT).
