# Snapmaker Studio — Innovation Fund Submission (DRAFT)

> Submission-ready package. **Not submitted.** External submission requires
> manual human action + credentials.
>
> Independent open-source project — not affiliated with or endorsed by Snapmaker.

## Project title
**Snapmaker Studio — the open, local-first workflow platform that prepares 3D
designs for the Snapmaker U1 (review in Orca before slicing).**

## Category
Open-source software / ecosystem & developer tools / user onboarding &
compatibility.

## Short description (~40 words)
Snapmaker Studio is a free, local-first desktop app that helps makers understand
a design, catch risks before slicing, and turn Bambu/Orca and STL files into a
prepared Snapmaker U1 profile copy in one click (review in Orca before slicing) (PrusaSlicer detection today;
full conversion next) — removing the biggest barrier for makers adding a U1.

## Long description
Makers adopting a new printer face a hidden tax: their existing library of
projects won't load cleanly. A Bambu or PrusaSlicer file opened in Snapmaker
Orca throws "Customized Preset" and "newer-version" warnings, carries foreign
printer/filament identity, and multi-material files fail in subtle ways. The
result is friction exactly at the moment of adoption.

Snapmaker Studio removes that tax. Drop in any file; the **Doctor** diagnoses U1
compatibility and scores it; one click **converts** it into a genuine U1 project
— preserving geometry, colors, and filament count — and a **validator** proves
the output is clean before the user wastes a print. It's local-first (no account,
no cloud), open source, and ships as a one-click Windows installer with a bundled
engine (no Python required).

It is already real: a real-world corpus of **112 files converts at 100%**, and a
former-Bambu project now opens in Snapmaker Orca with **zero warnings**. The
architecture is a kernel + plugins, so supporting the next printer or slicer is a
profile/adapter pack — not a rewrite. The long-term vision is "the operating
system for multi-material 3D printing": diagnose -> transform -> validate ->
manage -> optimize, across the whole ecosystem.

## Value proposition
- **For makers:** keep your library when you choose a U1. One click, no terminal,
  no lost work, no cloud.
- **For Snapmaker:** a polished, open onboarding funnel that **lowers the barrier
  to buying/using the U1** — built and maintained by the community, not the
  vendor. Foreign files become U1-native.
- **For the ecosystem:** a neutral, trustworthy compatibility layer that grows
  more valuable as printers proliferate.

## Ecosystem impact
- **De-risks switching to U1** — the #1 friction for cross-shopping makers.
- **Multi-material focus** — solves the hardest, highest-value compatibility seam
  (toolheads, purge math, filament-array consistency) where U1 competes.
- **Open + extensible** — community adds slicers/printers via profile packs;
  Snapmaker gets first-class, certified U1 support.
- **Measurable goodwill** — open source, local-first, no lock-in; aligns with
  maker trust.
- **Compounding asset** — the validation corpus + failure taxonomy is a public
  good no single slicer will build.

## Milestones (fundable)
| # | Milestone | Outcome | Evidence |
|---|---|---|---|
| M1 | Reliable U1 conversion (DONE) | Bambu/Orca/Prusa/geometry/STL -> U1 profile copy | 112-file corpus, 100% validation gate; review in Orca |
| M2 | Public beta installer | Signed, branded one-click Windows app | Signed `0.3.0` installer; icon/branding shipped |
| M3 | Project library + batch | Manage + convert a whole backlog | library UI + batch report |
| M4 | Ecosystem breadth | PrusaSlicer/Cura/Creality adapters | corpus expanded across families |
| M5 | Plugin SDK + certified U1 pack | Community profile packs; certified U1 | public SDK + first external pack |

## Funding use plan
- **Code signing certificate (EV/OV)** — remove SmartScreen friction for novices
  (the current GA blocker).
- **Cross-platform packaging** — macOS/Linux builds + CI release pipeline.
- **Corpus + reliability** — expand the validation corpus and wire it into CI.
- **Branding/onboarding polish** — finalize icon set, first-run experience, docs.
- **Plugin SDK** — stabilize and document the adapter/profile contracts.
- **Part-time maintainer time** — sustain reviews, releases, and community packs.

## Why Snapmaker's open U1 firmware matters
Snapmaker has open-sourced the U1 firmware (Klipper, Moonraker, Fluidd), so each U1
**exposes a standard local Moonraker/Klipper ecosystem on the LAN** — no cloud
required. That makes Snapmaker Studio a natural fit as the **local workflow layer
above the firmware**: understand a design → check it → get it ready → (next)
discover and monitor the U1 directly over the local network. It keeps the product
**local-first with no cloud dependency**, and it opens a clear path to a future
**Printer Hub** (discovery, live status, toolhead/material telemetry, job status).
_Full print sending is **not** shipped yet — it depends on a slicing step; see the
phased plan in [`ROADMAP.md`](ROADMAP.md) and the audit in
[`design/PRINTER_HUB.md`](design/PRINTER_HUB.md)._

## Proof links (current)
- Repo: github.com/DeadlyVirusIn/snapmaker-studio
- Vision: `docs/PRODUCT_VISION.md` . Roadmap: `docs/ROADMAP.md`
- Reliability: `../PROOF.md` (112-file validation corpus, 112/112 passed the internal validation gate — not a print-success guarantee)
- Release process: `RELEASE.md`

## Asks / notes for submission
- Confirm fund category + word limits before pasting the short/long descriptions.
- Code signing is the single highest-leverage funded item for novice reach.
- We are complementary to (Snapmaker) Orca — the on-ramp, not a competitor.
