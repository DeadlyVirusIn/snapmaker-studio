# Snapmaker Studio v0.4.0-beta.5

> **Independent open-source project — not affiliated with or endorsed by Snapmaker.**
> "Snapmaker" is a trademark of its respective owner.

## The Intelligence Layer for Open 3D Printing
Orca slices. Fluidd monitors. **Studio decides.** Before a layer is sliced, Studio
reads your model and your Snapmaker U1 (read-only) and tells you whether it will
print, what it costs, and what to sell it for — one screen, plain language.

### Doctor pillars
- **Project Doctor** — will it fit and print on your U1?
- **Printer Doctor** — a 0–100 health score from the U1's own signals.
- **Cost Doctor** — true cost, suggested price, and profit.

## New in beta.5

### Print Quality Doctor (MVP)
A bad print or preview? Pick the symptom (stringing, ringing, layer shift,
warping, first layer, blobs, under-extrusion, rough surface, bridging,
multi-material colour bleed) and get likely causes, safe first checks, where to
look in Snapmaker Orca, hardware/material checks and what not to change blindly.
**Advisory only — Studio never changes your settings or g-code, never guarantees
a fix, and never tells you to ignore a bad preview.**

### First Layer Doctor (MVP)
Fix the first layer before wasting filament. Pick what you see (won't stick,
nozzle too high/low, wrinkles, gaps, lifting corners, blob drag, area-specific,
toolhead-specific, breaks loose) for likely causes, beginner-first checks,
U1-specific checks (clearly marked **advanced**, e.g. heated-bed leveling, PEI
condition, bed-mesh/Fluidd range, toolhead 1), and slicer settings to inspect.
Advisory only; no printer/config/g-code changes.

### Beginner workflow guidance
A new **Get Started** page — "from model to first print" — walks a first-timer
through finding a model, checking it in Studio, fixing issues, then slicing in
Orca and printing. Steps that happen **outside Studio** (slicing, preparing the
printer) are labelled as such — Studio does not slice or send prints.

### Polish
- Doctor navigation cohesion: every Doctor/tool reachable from the sidebar; a
  "when to use each" overview; "Why Studio?" stays in the secondary/help area.
- Plate Color Remap confidence: the plate colour map tags each colour as
  **changing** or **protected**, so it's clear other colours and plates are safe.
- Model Discovery: clearer key-missing state ("connect provider API keys to
  enable live search"), link-out-only providers explained, privacy note (keys stay
  local/server-side; Studio never mirrors/re-hosts; no downloads/imports in v1).
- Scale Doctor: plain material multiplier ("about Nx the material at P%", an
  estimate), explicit joints/threads/holes/snap-fits and thin-detail warnings.
- Doctors cross-link to the right next Doctor.

## Carried from earlier betas
- Compatibility Doctor (read-only; no auto-fix), Scale Doctor (analysis-only; no
  writes), Plate Color Remap (verified safe copy; original untouched), navigation
  cleanup, and the beginner Plate Remap proof cards.
- Visual 3D plate preview remains deferred (colour/part summary fallback).

## Safety
- All new Doctors are **advisory and read-only**: no printer control, no auto-fix,
  no profile/g-code/settings writes, no guaranteed-print claims.
- Model Discovery does not download or import models (v1 is search + link-out), and
  never scrapes.
- Real-world validation fixtures are not included in the repository (they may be
  copyrighted/commercial).

## Windows install (unsigned beta)
This beta installer is **currently unsigned**, so Windows SmartScreen may show
**"Unknown publisher."** That is expected for an unsigned beta. Only download it
from the official GitHub release, and verify the checksum before installing.

```
File:    Snapmaker.Studio_0.4.0-beta.5_x64-setup.exe
Size:    16,056,194 bytes
SHA256:  0D6706D0DD65A566E4D08BA776BD2BA6B2A64ED364F1208DA97634C4CF5542E1
```

Full guidance: [docs/windows-install.md](windows-install.md). Code-signing
readiness plan: [docs/windows-code-signing.md](windows-code-signing.md).

## Quality
- Backend: 223 automated tests (220 passed, 3 conditional real-fixture tests skip
  when the fixture is absent).
- Frontend: vitest 48/48; TypeScript clean; production build clean.
- Local installer builds, launches, sidecar starts, `/health` 200, 0 orphan
  processes on exit.

_Beta — local-first; nothing leaves your computer._
