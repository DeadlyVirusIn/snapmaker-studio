# Code signing policy

Snapmaker Studio is an independent, MIT-licensed open-source project maintained in
public at <https://github.com/DeadlyVirusIn/snapmaker-studio>.

This page exists because signing programs for open-source projects require the
project to publish who can release code and how. It is also simply useful: anyone
downloading an installer should be able to see how it was produced.

## Project

| | |
|---|---|
| Name | Snapmaker Studio |
| Repository | <https://github.com/DeadlyVirusIn/snapmaker-studio> |
| Licence | MIT |
| Distribution | GitHub Releases, free of charge |
| Platforms | Windows 10/11 x64 |

## Team and roles

| Role | Who | Responsibility |
|---|---|---|
| Author | Kunal Khurana (@DeadlyVirusIn) | Writes and commits code |
| Reviewer | Kunal Khurana (@DeadlyVirusIn) | Reviews changes before release |
| Approver | Kunal Khurana (@DeadlyVirusIn) | Approves a signing request for a release |

This is a single-maintainer project; the same person holds all three roles.
Multi-factor authentication is enabled on the GitHub account and on any signing
service account.

## How a release is produced

1. Every change lands on `main` through the checks in
   `.github/workflows/ci.yml`: the Python engine suite, the end-to-end
   `u1convert selfcheck`, the desktop unit tests, `tsc --noEmit`, a production
   Vite build, and `cargo check`.
2. The Windows installer is built from that source with
   `npm run release:windows`, which freezes the Python engine with PyInstaller
   and bundles it with the Tauri shell into an NSIS installer.
3. Installed-build acceptance runs against the produced installer
   (`tools/acceptance/run.ps1`) — install, launch, drive the real UI, uninstall,
   verify cleanup.
4. The installer's SHA256 is recorded in
   [docs/RELEASE_METADATA.md](RELEASE_METADATA.md) and published on the release.
5. Verification state for the build is recorded in
   [docs/TRUST_STATUS.md](TRUST_STATUS.md), which distinguishes automated checks
   from ones still pending.

Binaries are built only from this repository's own source.

## What ships in the installer

- `snapmaker-studio-desktop.exe` — the Tauri shell, built from `desktop/src-tauri`.
- `snapstudio-api.exe` — the Python engine from `backend/`, frozen with
  PyInstaller.
- An NSIS uninstaller.

No third-party proprietary component is bundled. Third-party dependencies are the
declared packages in `desktop/package.json`, `desktop/src-tauri/Cargo.toml` and
`backend/pyproject.toml`. Snapmaker Orca is *not* bundled — Studio launches it if
the user has installed it separately. See
[THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

## Privacy

Snapmaker Studio runs entirely locally. It has no account, sends no telemetry, and
uploads nothing. It reads files the user opens and, when the user configures a
printer address, makes read-only requests to that printer on the local network.
See [docs/SECURITY.md](SECURITY.md).

## Uninstall

Uninstall from Windows Settings → Apps, or run `uninstall.exe` in the install
directory. This removes the application and its sidecar; it is verified as part of
the acceptance run.

## Attribution

If code signing is provided by the SignPath Foundation, this project will display:

> Free code signing provided by [SignPath.io](https://signpath.io), certificate by
> [SignPath Foundation](https://signpath.org).

## Honest note on what signing changes

Signing an installer replaces the "unknown publisher" SmartScreen warning with one
that names a verified publisher, and begins accumulating SmartScreen reputation.
It does not remove the warning immediately —
[Microsoft's own documentation](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)
states that EV certificates no longer bypass SmartScreen either. Reputation builds
over clean installs. This project will not claim otherwise.
