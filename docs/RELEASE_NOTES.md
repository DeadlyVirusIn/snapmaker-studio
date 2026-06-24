# Snapmaker Studio v0.4.0-beta.12 — beta.11 completion release

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

**Completes the beta.11 scope: Plate Color Remap clarity, more Print Quality
paths, a clearer known-good comparison, a tighter security policy — on top of the
one-click "Open in Snapmaker Orca" handoff from beta.11.**

## The Intelligence Layer for Open 3D Printing
Snapmaker Orca slices. Fluidd monitors. **Studio helps decide what to fix before you print.**
Advisory only; not a guarantee of print success. Studio does not slice and does
not control Orca.

## New in this completion release
- **Plate Color Remap — no more dead ends.** When a plate's colours are painted
  per-face (no swappable filament slot), Studio now explains that in plain
  language instead of a blank "no base colors detected." The colour + plate
  preview (source → target swatches, protected colours, gold accents, untouched
  plates, what changes vs stays) is shown up front. Original file never modified.
- **Print Quality Doctor — two new paths.** Added **"Won't stick / lets go of the
  bed"** (bed adhesion) and **"Supports fail or won't separate"** (support
  failure), each with likely causes, first checks, the Snapmaker Orca settings to
  look at, and what to avoid. 12 symptom paths in total.
- **Known-good comparison — clearer.** The "fails even with supports" flow now
  opens with plain framing: compare a failed print with one that worked; name the
  problem file, what printed before, and the filament that worked vs failed —
  Studio points at what likely changed and what to try next. Advisory, never a
  guarantee.
- **Tighter security policy.** The desktop app now ships a Content-Security-Policy
  (was none): the main window is restricted to its own assets, the local loopback
  engine, and Tauri IPC. The approved-site Model Browser is a separate locked
  window governed by the site's own policy and still gets no app IPC.
- **One-click "Open in Snapmaker Orca"** (from beta.11) — prepare a validated U1
  copy and hand it straight to an installed Snapmaker Orca; falls back to Install
  Snapmaker Orca + Copy path. One-way handoff.

## Carried forward
Approved-site Model Browser v1 (manual download/open; no scraping, no auto-import,
no API keys), Scale Options Ladder, Compatibility Doctor, Project Doctor, local-API
and reliability hardening.

## Known limitations (honest)
- **In-window Model Browser controls** (Back to Studio / Run Project Doctor *inside*
  the site window) are intentionally not added: giving the third-party page those
  controls would require granting the remote page app IPC (forbidden by our
  security model), and hosting the site inside a local toolbar shell is blocked by
  the sites' own `X-Frame-Options`. The safe control surface is the Studio **Find
  Models** page (Open downloaded file → Run Project Doctor), which is unchanged.
- **Full 3D plate render** for Plate Color Remap remains deferred; the colour/plate
  swatch preview is the current visual.
- **File ecosystem:** STL and 3MF reads are core and covered by the test suite;
  PrusaSlicer projects are detected/read; full cross-slicer *conversion* is
  deliberately not attempted (export-stability risk without proven need).
- This is an **unsigned Windows beta** — Windows SmartScreen may show "Unknown
  publisher." Verify the SHA256 before installing. Code signing remains planned.

## Download (unsigned beta)
Only download from the official GitHub release, and verify the checksum.

```
File:    Snapmaker.Studio_0.4.0-beta.12_x64-setup.exe
Size:    16,090,535 bytes
SHA256:  593bd0dc88473dac7df53ccee32949b2dafab6640074ff3b4607b21763c93b32
```

Full guidance: [docs/windows-install.md](https://github.com/DeadlyVirusIn/snapmaker-studio/blob/v0.4.0-beta.12/docs/windows-install.md).

_Beta — local-first; nothing leaves your computer._
