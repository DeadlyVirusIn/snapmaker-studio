# Roadmap Recommendation (research — no code)

**Date:** 2026-06-18 · Ranks future initiatives and sequences them to v1.0.
Scores 1–5 (5 = best). "Effort" is inverted in the composite (less effort = higher).

## Scoring
| Initiative | Fund impact | User value | Effort (5=cheap) | Defensibility | Composite |
|---|---|---|---|---|---|
| **Project Intelligence** | 4 | 4 | 5 | 3 | **16** |
| **Validation Center** | 4 | 4 | 4 | 3 | **15** |
| **Multi-Ecosystem (Prusa import)** | 5 | 4 | 2 | 5 | **16** |
| **Printer Hub (monitor, U1/Moonraker)** | 5 | 5 | 3 | 4 | **17** |
| **Printer Profiles** | 4 | 4 | 3 | 4 | **15** |
| **Visual model viewer** | 3 | 5 | 3 | 2 | **13** |
| **Slice-and-send workflow** | 4 | 5 | 1 | 3 | **13** |
| **Discover / marketplace** | 3 | 4 | 2 | 2 | **11** |

### Rationale (per initiative)
- **Printer Hub (monitor)** — highest composite. The open U1 firmware makes it cheap-ish and *vendor-aligned* (answers "why not let Snapmaker do it" — we ride their open stack). Highly demoable: a live printer in the app. Read-only first (no slicing dependency).
- **Multi-Ecosystem / Prusa import** — top **defensibility + Fund impact**: directly kills "single-printer file-fixer." The canonical IR (Sprint 2) is the moat. Higher effort (INI parser + tool-capacity UX).
- **Project Intelligence** — cheapest high-value win (builds on Doctor + library); reframes "fixer" → "understands your design." Mostly shipped in Simple Mode; extend with size/material/printability.
- **Validation Center** — productizes the core promise; pairs 1:1 with Printer Profiles; the hardened `is_u1_clean` gate is its engine.
- **Printer Profiles** — foundation for multi-target + the Hub (a profile becomes a real device); medium effort, good defensibility.
- **Visual model viewer** — huge UX/demo value, weak defensibility (commodity); do it for the demo, not the moat.
- **Slice-and-send** — highest user value, **highest effort** (needs a slicer or Orca handoff) + the U1 prints gcode Studio doesn't make. Defer; bridge via Orca handoff.
- **Discover / marketplace** — lowest composite; legal-bounded (per `design/DISCOVER_LOWRISK.md`), defer to download-then-open + official APIs.

## Recommended sequence through v1.0
- **v0.3.x (now):** ship beta.2 (Clean Import fix). Stabilize. *(Released-infra owned by user.)*
- **v0.4 — "Understands & validates"** (cheap, reframes the product)
  - Project Intelligence (size/material/printability) + Validation Center (per-target readiness report). Demo clip recorded here.
- **v0.5 — "Knows your printer"** (vendor-aligned, demoable)
  - Printer Hub **Phase A** (discover/monitor U1 via open Moonraker; read-only). Printer Profiles framework underneath.
- **v0.6 — "Speaks every ecosystem"** (the moat)
  - Canonical IR + **Prusa importer** (multi-material preserved, 5→4 merge UX). First true cross-ecosystem proof. Add ≥1 second export target behind Profiles.
- **v0.7 — "Manages the print"**
  - Printer Hub **Phase B** (upload sliced gcode, start/pause/cancel, queue). Visual model viewer for the workspace.
- **v0.8–v0.9 — "Closes the loop"**
  - Slice-and-send (Orca handoff first; embedded slicer investigation). Discover (download-then-open + official APIs).
- **v1.0 — "Cross-ecosystem workflow platform"**
  - Understand → validate → prepare (any ecosystem) → monitor/send (U1) → manage library, with a stable plugin/profile SDK. The OS claim becomes earned, not asserted.

## Why this order (the through-line)
Each release retires one reviewer objection (Sprint 3) **and** ships standalone value:
intelligence/validation kill "just a fixer" cheaply → Hub kills "can't touch the printer"
and is vendor-aligned → Prusa/IR kill "single-printer" and build the moat → send/viewer/
discover complete the loop. Effort rises as proof accrues; the moat (canonical IR + Hub on
open firmware + profile packs) compounds rather than being front-loaded.
