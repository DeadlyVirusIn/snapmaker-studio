# Snapmaker Studio — Validation Package

Every capability traces to a **real, recurring U1 community pain** surfaced across
r/snapmaker, the Snapmaker forums, Facebook U1 groups, and GitHub (Snapmaker /
OrcaSlicer issues). These are curated by theme — see
`backend/snapstudio_core/community_knowledge.py` for the in-app, matchable form.

## Problem → Solution → Outcome

| Community pain | Where it's reported | Studio solution | Outcome for the user |
|---|---|---|---|
| **"Out of bounds" with no reason** — Orca refuses to slice, doesn't say which axis | r/snapmaker, forum, FB | **Project Doctor** checks geometry vs the U1's 270³ bed pre-slice; gives the exact scale-% / rotate / split | Knows *why* and the fix in seconds instead of asking a group |
| **Prime/wipe tower collisions or tipping** | r/snapmaker, GitHub (Orca), FB | Project Doctor flags low tower clearance for multi-material | Avoids a failed multi-colour print before it starts |
| **More colours than toolheads / wrong colours** | r/snapmaker, forum | **Multi-Material Doctor** checks colours vs the real toolhead count, explains remap / pause-and-swap | Multi-colour prints come out right; original colours preserved |
| **First layer won't stick / warping** | r/snapmaker, forum, FB | **First Layer Doctor** flags adhesion risk from footprint + the printer's real bed mesh | Fewer first-layer failures; actionable steps |
| **Cryptic Klipper/firmware errors mid-print** | GitHub (U1 firmware), r/snapmaker | **Printer Doctor** turns klippy state + failed components into plain language + a 0–100 health score | Understands the fault without reading logs |
| **Converted/foreign project won't open right ("Customized Preset")** | GitHub (Orca), forum | Conversion + validation conform filament arrays/purge to the colour count | Bambu/Orca projects open and print correctly on the U1 |
| **"What does this cost / what should I charge?"** | FB sell-prints groups, Reddit | **Cost / Pricing / Profit Doctors** — true cost, tiered price, margin, break-even | Prices confidently; runs a print business, not guesswork |
| **Fixes scattered across forums** | all of the above | **Community Knowledge** attaches the known fix + confidence to each risk in the Report | The answer is in-app, at the moment of the problem |
| **No single "should I print this?" answer** | implicit across all | **Studio Intelligence Report** synthesises every Doctor into one score + next action | A 15-second decision, even for a first-timer |

## Validation logic
- **Breadth:** every shipped capability maps to a pain reported in 2+ community
  channels — none are speculative.
- **Uniqueness:** the cost/pricing/profit and pre-slice out-of-bounds explanation
  pains are **unsolved** by Orca, Fluidd, or OctoPrint (see `SUBMISSION.md`).
- **Honesty:** the curated knowledge base cites source *themes*, not individual
  users' words; Phase 2 (reviewed ingestion) is documented but not claimed as done.

## Evidence of build quality
166 automated tests green; v0.4.0-beta.1 RC built, frozen engine smoke-tested
(all endpoints 200, launch + sidecar + 0 orphans). See `AUDIT.md`.
