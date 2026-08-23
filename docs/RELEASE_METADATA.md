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
| Version | v0.4.0-beta.24 |
| Installer | `Snapmaker.Studio_0.4.0-beta.24_x64-setup.exe` |
| Size (bytes) | 16,263,985 |
| SHA256 | `50fc5434e266f0b8c025336410534d019f8d41c0ec5190290024c702126cbf26` |
| Release URL | https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.4.0-beta.24 |
| Trust status | ACCEPTED — see [docs/TRUST_STATUS.md](TRUST_STATUS.md) |

Note: verify with `Get-FileHash -Algorithm SHA256 <installer>`.

## Previous release

| Field | Value |
|---|---|
| Version | v0.4.0-beta.23 |
| Installer | `Snapmaker.Studio_0.4.0-beta.23_x64-setup.exe` |
| Size (bytes) | 16,261,551 |
| SHA256 | `30c8895175e37ccf61b9f61cc9996b2b37553e490e00cbccfc60ba508aa1ac47` |
| Release URL | https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.4.0-beta.23 |
