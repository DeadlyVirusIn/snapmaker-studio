# Snapmaker Studio v0.4.0-beta.10 — release notes (DRAFT)

> Draft for review. Do not publish until the installer is built and approved.
> Placeholders below (asset name, size, SHA256) are filled in at build time.

> Independent open-source project — not affiliated with or endorsed by Snapmaker.
> "Snapmaker" is a trademark of its respective owner.

## What's new in beta.10

This release focuses on making Studio safer and clearer for first-time Snapmaker
U1 owners, on top of everything in beta.9.

- Advisory, honest wording everywhere. Readiness is shown as an estimate
  ("Likely ready", "Looks U1-ready"), never an absolute "will print" claim.
- The Project Doctor result leads with print readiness and risks; cost and
  pricing moved into their own optional section instead of the headline.
- Simpler navigation for beginners. Simple mode shows a short path — open a
  model, Get Started, Project Doctor, Find Models, My Designs — with the rest
  under "More tools". Advanced mode still shows every tool.
- Find Models is now an approved-site browser: browse trusted 3D-model sites,
  download the STL or 3MF there, then open it in Studio to check it. No API
  keys, no import claims; optional live search lives under Advanced.
- Plainer language: removed slicer jargon and clarified empty states.

## Carried forward from beta.9

Print Failure Troubleshooter (known-good aware), known-good comparison, Scale
Options Ladder, Compatibility / Project / Plate Color Remap Doctors, reliability
and local-API hardening.

## Install (Windows)

- Installer: `Snapmaker.Studio_0.4.0-beta.10_x64-setup.exe`  *(filename at build)*
- Size: `<filled at build>`
- SHA256: `<filled at build>`

This beta is not code-signed yet, so Windows SmartScreen may show "Unknown
publisher." That is expected. Download only from the official release page and
verify the SHA256 before installing:

```powershell
Get-FileHash -Algorithm SHA256 ".\Snapmaker.Studio_0.4.0-beta.10_x64-setup.exe"
```

Studio is local-first: no account, no cloud, nothing leaves your computer. It is
advisory — it surfaces likely print risks and guidance; it is not a slicer, not a
printer controller, and not a promise that a print will succeed.

## Notes for reviewers

Full guidance: docs/windows-install.md · docs/JUDGE_OVERVIEW.md ·
docs/WHAT_TO_TEST_FIRST.md.
