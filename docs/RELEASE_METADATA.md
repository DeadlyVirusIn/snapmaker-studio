# Release Metadata — canonical source

This file is the single source of truth for the released version, installer name,
size and hash. Update it first on every release.

**One duplication is allowed, on purpose:** the README's download block repeats the
size and SHA256, because telling someone to open a second document before verifying
a download is how verification stops happening. That copy is only safe while it is
checked, so `backend/tests/test_release_docs.py` fails the build if the README and
this file disagree, if a superseded hash survives in a download instruction, if the
app manifests carry a different version, or if `TRUST_STATUS.md` does not lead with
the release named here.

Every *other* document must link here rather than restate these values.

## Current release

| Field | Value |
|---|---|
| Version | v0.6.1 |
| Installer | `Snapmaker.Studio_0.6.1_x64-setup.exe` |
| Size (bytes) | 16,927,507 |
| SHA256 | `b062ac52e6e935e79267cbd00aee859c3eb39b768f14a6be3856f944472bdb7b` |
| Release URL | https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.6.1 |
| Trust status | ACCEPTED — see [docs/TRUST_STATUS.md](TRUST_STATUS.md) |

A stable release, not a prerelease, so GitHub's "latest release" points at it.

Note: verify with `Get-FileHash -Algorithm SHA256 <installer>`.

## Previous release

| Field | Value |
|---|---|
| Version | v0.6.0 |
| Installer | `Snapmaker.Studio_0.6.0_x64-setup.exe` |
| Size (bytes) | 16,900,712 |
| SHA256 | `e85c18a8589574e107e019d99c504fa5f6ccf15f65fd35416b67e0ec3eff461f` |
| Release URL | https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.6.0 |

## Superseded

| Field | Value |
|---|---|
| Version | v0.5.0 |
| Installer | `Snapmaker.Studio_0.5.0_x64-setup.exe` |
| Size (bytes) | 16,871,622 |
| SHA256 | `73124b2162ea3581db3237b4e9400d3cb4b9a339bc3bdafb9e5a793c336cf12c` |
| Release URL | https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.5.0 |
