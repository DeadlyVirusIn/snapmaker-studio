# Installing the Snapmaker Studio Windows beta

This is a **prerelease (beta)** build. The Windows installer is **currently
unsigned** (no code-signing certificate yet), so Windows SmartScreen will likely
show a warning such as:

> **Windows protected your PC**
> App: `Snapmaker.Studio_0.4.0-beta.17.2_x64-setup.exe`
> Publisher: Unknown publisher

This warning is expected for an unsigned beta from a new publisher. It does not
by itself mean the file is unsafe — but you should still take normal precautions.

## Download only from the official release

Only download the installer from the official GitHub release page:

- https://github.com/DeadlyVirusIn/snapmaker-studio/releases/tag/v0.4.0-beta.10

Do not run installers for this app obtained from anywhere else.

## Verify the download (SHA256)

Before installing, confirm the file's SHA256 checksum matches the value below.

```
File:    Snapmaker.Studio_0.4.0-beta.17.2_x64-setup.exe
Size:    16121235 bytes
SHA256:  077de9444c1ef5a56d6b4f5f44a9986b094e150b26823716f5df463c8e8b845f
```

Check it in PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 ".\Snapmaker.Studio_0.4.0-beta.17.2_x64-setup.exe"
```

If the printed hash does not match, **do not run the installer** — delete it and
download again from the official release page.

## About the SmartScreen warning

Because this beta is unsigned, SmartScreen may warn you. Only proceed if you
trust the source (the official GitHub release) and you have verified the checksum
above. If anything looks off — the checksum doesn't match, or you got the file
from somewhere other than the official release — do not continue.

## Install steps

1. Download `Snapmaker.Studio_0.4.0-beta.17.2_x64-setup.exe` from the official
   release page above.
2. Verify the SHA256 (see above). If it doesn't match, stop and re-download.
3. Run the installer. On the SmartScreen prompt, choose **More info → Run anyway**
   only after you have verified the checksum and trust the source.
4. Launch **Snapmaker Studio** from the Start menu. No account or cloud is needed.

## Uninstall steps

1. Open **Settings → Apps → Installed apps** (or **Apps & features**).
2. Find **Snapmaker Studio** in the list.
3. Choose **Uninstall** and confirm. You can also use the uninstall entry in the
   Start menu folder, if present.

Studio is local-first: it runs entirely on your machine and does not upload
anything automatically, so removing the app leaves nothing behind in the cloud.

## Code signing (planned)

Code signing is planned before any wider public launch (readiness plan:
[windows-code-signing.md](windows-code-signing.md)). Code signing
identifies the publisher and generally improves trust, but note that newly
signed files can still take time to build SmartScreen reputation, so a warning
may persist for a while even after signing. Microsoft Store distribution may also
be evaluated later as an additional trusted channel.

_This build is a beta and is local-first; nothing leaves your computer._
