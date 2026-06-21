# Windows code-signing readiness plan

> Status: **plan only. The installer is currently UNSIGNED.** No certificate has
> been purchased or installed; nothing here enables signing or changes the release
> process. This documents exactly what to do when a certificate is available.

## Current gap

`Snapmaker Studio_<version>_x64-setup.exe` is built unsigned, so Windows
SmartScreen shows "Unknown publisher" (see [windows-install.md](windows-install.md)).
Releases ship with a published SHA256 so users can verify integrity in the
meantime. Signing is the proper fix but requires a code-signing certificate.

## Certificate type needed

- An **Authenticode code-signing certificate** from a trusted CA.
- **OV (Organization Validation):** cheaper; builds SmartScreen reputation over
  time/downloads after signing.
- **EV (Extended Validation):** typically grants SmartScreen reputation faster,
  but requires a hardware token or a cloud HSM (e.g. Azure Trusted Signing /
  an HSM-backed key) — keys are non-exportable by design.
- Recommendation: evaluate **Azure Trusted Signing** (subscription, cloud-managed
  keys, no physical token) vs a traditional OV/EV cert. Microsoft Store
  distribution can be evaluated separately as an additional trusted channel.

## Where signing plugs into the build (Tauri v2 / NSIS)

The desktop app is Tauri v2 bundling NSIS. Signing is configured under
`bundle.windows` in `desktop/src-tauri/tauri.conf.json`. Two options:

- **Certificate thumbprint (local cert store):**
  add `bundle.windows.certificateThumbprint` (+ optional `digestAlgorithm`,
  `timestampUrl`). Tauri signs the app exe and the NSIS installer with `signtool`.
- **Custom sign command (HSM / cloud signing):**
  add `bundle.windows.signCommand` to invoke the cloud/HSM signer
  (e.g. Azure Trusted Signing's `trusted-signing-cli`, or `signtool` with a
  dlib/credential provider).

> Do NOT add these keys now: with no certificate present they make `tauri build`
> fail, which would break the current unsigned beta pipeline. Add them only once a
> cert/thumbprint or sign command is actually available. Keep a timestamp URL set
> when you do, so signatures remain valid after the cert expires.

## Local secret handling

- Never commit certificates, `.pfx`/`.p12` files, thumbprints tied to a private
  key, or passwords to the repo. Add `*.pfx`/`*.p12` to `.gitignore` before any
  local signing.
- Prefer the Windows certificate store (reference by thumbprint) or an HSM/cloud
  signer over a loose `.pfx` on disk.
- If a `.pfx` must be used locally, keep it outside the repo and pass its password
  via an environment variable, never a command-line literal or a file in-tree.

## CI secret handling (if/when CI builds releases)

- Store the certificate/credentials as encrypted CI secrets (e.g. GitHub Actions
  secrets), never in the workflow file or repo.
- For EV/HSM: use a cloud signing service (Azure Trusted Signing) with a
  federated/OIDC credential rather than shipping a private key to CI.
- Inject secrets at build time only; mask them in logs; scope them to the release
  workflow.

## Verification command

After signing, verify before publishing:

```powershell
Get-AuthenticodeSignature ".\Snapmaker Studio_<version>_x64-setup.exe"
# Status should be 'Valid' with the expected signer/publisher.
```

or with the Windows SDK:

```
signtool verify /pa /v "Snapmaker Studio_<version>_x64-setup.exe"
```

## SmartScreen reputation caveat

Signing identifies the publisher and generally improves trust, **but a newly
signed file (especially with a fresh OV certificate) can still trigger SmartScreen
until it builds reputation** across downloads. EV certs usually shorten this.
Do not claim that signing makes the warning disappear immediately, and never tell
users to blindly bypass SmartScreen.

## Checklist (when a cert is available)

- [ ] Acquire OV/EV cert or set up Azure Trusted Signing.
- [ ] Store credentials securely (cert store / HSM / CI secret) — never in-repo.
- [ ] Add `bundle.windows.certificateThumbprint` or `signCommand` to
      `tauri.conf.json` (with `timestampUrl`).
- [ ] Build; confirm the installer and app exe are both signed.
- [ ] Verify with `Get-AuthenticodeSignature` / `signtool verify`.
- [ ] Update release notes: state it is signed; keep the SmartScreen-reputation
      caveat until reputation is established.
- [ ] Re-enable any CI release signing steps.
