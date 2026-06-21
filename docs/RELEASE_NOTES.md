# Snapmaker Studio v0.4.0-beta.4

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

## The Intelligence Layer for Open 3D Printing
Orca slices. Fluidd monitors. **Studio decides.** Before a layer is sliced, Studio
reads your model and your Snapmaker U1 (read-only) and tells you whether it will
print, what it costs, and what to sell it for — one screen, plain language.

### Doctor pillars
- **Project Doctor** — will it fit and print on your U1? Catches out-of-bounds and
  printability problems before Orca does.
- **Printer Doctor** — a 0–100 health score from the U1's own signals.
- **Cost Doctor** — true cost, suggested price, and profit (with Pricing/Profit).

The **Studio Intelligence Report** synthesises these into one verdict; the Doctors
become the supporting evidence.

## New in beta.4

### Compatibility Doctor (read-only)
Open a 3MF and Studio checks it for common Snapmaker U1 / Orca / Snorca problems
before you slice: out-of-range slicer values (e.g. `wall_filament`,
`tree_support_wall_count`), a non-U1 / foreign profile signature, and relative
extrusion without a `G92 E0` layer reset. Each finding explains the likely cause,
the safest next step, and the exact setting. **It is read-only and does not
auto-fix anything** — it diagnoses and points you to the fix.

### Model Discovery Hub v1 (search + link-out)
A "Find Models" page to search 3D-model sites and check a model's source and
license before you commit. v1 is **metadata search + link-out only**: sanctioned
providers (Thingiverse, MyMiniFactory, Cults3D) via their own APIs, plus link-out
tiles for Printables, Thangs and MakerWorld. **No scraping, and no downloads or
imports in v1** — every result opens on its source site. Provider search needs
API keys configured; until then it honestly reports search as disabled rather than
showing fake results. License/attribution is always shown and a disclaimer asks
you to respect each model's terms.

### Scale Doctor preview (analysis-only)
Preview a uniform resize before you commit: scaled dimensions, whether it still
fits the U1 build volume, and the material/cost change. It is **analysis-only —
it writes no files and does not resize or export your model**, uses
"likely safe / caution / not recommended" wording (**never guarantees a successful
print**), and warns that holes, threads, snap-fits, joints and tolerances may not
scale and that the thin-wall check is approximate.

### Also in beta.4
- **Code-signing readiness plan** documented (no certificate used; this build is
  still an unsigned beta — see below).
- **Print Quality Doctor is planned only and is NOT shipped in this release**
  (design doc only).

## Carried from beta.3
- Clearer navigation: every Doctor directly reachable from the sidebar; "Why
  Studio?" in a secondary/help area; Plate Color Remap grouped next to the
  Multi-Material Doctor.
- Beginner-friendly Plate Color Remap with "what will change / what will stay the
  same" proof cards, protected painted/gold details, "Create safe copy — original
  stays unchanged", and a verified-safe-copy success card. Real-world validation
  fixtures are not included in the repository (they may be copyrighted/commercial).
- Visual 3D plate preview remains deferred (colour/part summary fallback shipped).

## Windows install (unsigned beta)
This beta installer is **currently unsigned**, so Windows SmartScreen may show
**"Unknown publisher."** That is expected for an unsigned beta. Only download it
from the official GitHub release, and verify the checksum before installing.

```
File:    Snapmaker.Studio_0.4.0-beta.4_x64-setup.exe
Size:    16,031,077 bytes
SHA256:  0FDDD084F678FA0182B5676F04849248868E362DEF90062176E75F33E8398C09
```

Full guidance: [docs/windows-install.md](windows-install.md). Code-signing
readiness plan: [docs/windows-code-signing.md](windows-code-signing.md). Signing
is planned before any wider public launch (a signed file can still take time to
build SmartScreen reputation).

## Quality
- Backend: 210 automated tests (207 passed, 3 conditional real-fixture tests skip
  when the fixture is absent).
- Frontend: vitest 43/43; TypeScript clean; production build clean.
- Local installer builds, launches, sidecar starts, `/health` 200, 0 orphan
  processes on exit.

_Beta — local-first; nothing leaves your computer._
