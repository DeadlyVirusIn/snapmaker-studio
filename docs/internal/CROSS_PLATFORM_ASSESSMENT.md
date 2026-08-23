# macOS and Linux — what actually blocks it

Assessed 2026-08-23, time-boxed, during the v0.5.0 sprint. FOrcaSlicer now ships
packaged macOS builds, which is a fair prompt to ask why Studio does not.

**Conclusion: not in this sprint, and not because of the application code.** The
blockers are all in producing and *verifying* a build, and shipping an unverified
one would break the rule that makes Studio's releases worth anything.

## What would port cleanly

- **The engine.** `snapstudio_core` and `snapstudio_api` are pure Python with no
  Windows-specific code in the analysis path. The G-code reader, the print plan,
  the material plan, the send check, the fidelity audit and the Moonraker client
  are all platform-neutral.
- **The frontend.** React and Tailwind; nothing Windows-specific.
- **Most of the shell.** The Tauri commands are portable apart from the sidecar
  job-object code, which is explicitly `cfg(windows)` and exists to kill the
  engine process if the app dies. Each platform needs its own equivalent.

## What actually blocks it

1. **The sidecar cannot be cross-compiled.** The engine ships frozen by
   PyInstaller, which produces a native executable per platform: a Mach-O binary
   needs a macOS machine to build, an ELF binary needs Linux. There is no
   cross-target option. This alone requires CI runners or hardware Studio does
   not have.
2. **Bundling needs the platform toolchain.** A `.dmg` needs Xcode command-line
   tools; a `.deb`/`.AppImage` needs the corresponding Linux tooling.
3. **The verification standard does not port.** The release gate is an
   installed-build acceptance run: NSIS silent install, an isolated WebView2
   profile driven over the Chrome DevTools Protocol, uninstall, registry cleanup.
   On macOS that is a DMG mount, an app bundle, WKWebView — which does not expose
   CDP the same way — and no registry. It is a second harness, not a flag.
4. **Process supervision differs.** Killing an orphaned sidecar uses a Windows job
   object. macOS and Linux need their own mechanism, and getting that wrong leaves
   a stray engine process running on a user's machine.
5. **Snapmaker Orca detection is registry- and Program-Files-based.** The handoff
   would need per-platform discovery.

## What would have to be true to do it

- A macOS runner (GitHub Actions provides one) building the sidecar and bundling
  the app.
- A macOS acceptance harness of comparable strength — otherwise the build ships
  with no evidence, and `TRUST_STATUS.md` would have to say so.
- A non-Windows equivalent of the sidecar lifetime guarantee.

That is a real piece of work with its own release gate, not a switch. It is
tracked in [../ROADMAP.md](../ROADMAP.md) rather than half-started here.

## What was explicitly not done

No macOS build was produced, and none is claimed. The README says Windows, the
release says Windows, and `TRUST_STATUS.md` lists "Windows only" as a limitation.
Shipping an unverified build for a platform nobody has tested would be the exact
failure this project's release process exists to prevent.
