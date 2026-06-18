# Platform Expansion — Innovation Fund Design Proposal

**Date:** 2026-06-18 · **Status:** research & design only (no implementation) · **Target:** v0.4+

**Thesis:** Snapmaker Studio is currently perceived as a *repair/conversion tool*. To
become **"The Workflow Platform for Modern 3D Printing,"** it must (a) be **multi-printer**,
(b) be **intelligent** about projects, and (c) own the **full workflow loop** with
durable history — not just transform-and-hand-off. The good news: the engine is already
**profile-data-driven** (`snapstudio_core/data/profiles/*.json`, `data/templates/`,
`u1_rules.json`) and the library already has an unused **`history`** table, so much of
this is *generalization of existing structure*, not greenfield.

---

## Evaluation of the 5 idea areas

Scales: Effort S/M/L/XL · Impact Low/Med/High/Very-High.

### 1. Discover (MakerWorld · Printables · Cults3D · Thingiverse)
- **Feasibility:** Mixed. **Thingiverse** + **Printables** have official APIs (keys, within
  TOS). **MakerWorld** (Bambu) and **Cults3D** have no open public API — fetching means
  scraping (brittle, TOS-violating).
- **Effort:** **L–XL** — per-site adapters, auth, rate limits, download + unzip, license capture.
- **Legal/TOS:** **HIGH RISK.** Scraping MakerWorld/Cults likely breaches TOS; redistributing
  models touches per-model licenses (CC-BY/NC/ND, attribution, no-derivatives). Must never
  re-host; only fetch on the user's behalf and preserve license + attribution.
- **Fund impact:** High narrative ("any file, from anywhere"), but legal exposure undercuts a
  fundable, defensible story.
- **Demo impact:** Very High ("paste a link → U1-ready in 10s").
- **Differentiation:** High — but the *risky* kind. Most tools avoid it deliberately.
- **Verdict:** **Defer / de-scope.** Phase it as **official-API-only import + "open a
  downloaded file with its metadata"**, not a scraper. Legal review before any MakerWorld/Cults work.

### 2. Project Intelligence (metadata · source · materials · printability · compatibility)
- **Feasibility:** **High.** Bambu/Orca 3MF already embed `slice_info`, `project_settings`,
  filament arrays, painting, plate data — the engine parses most of this today. Library already
  stores `source_family` / `filament_count`.
- **Effort:** **S–M** — a `ProjectInfo` extractor over existing parsers + library schema columns.
- **Legal/TOS:** None (local files).
- **Fund impact:** **High** — reframes "converter" as **analysis platform**: "Studio understands
  your project."
- **Demo impact:** High — rich project cards (source, materials, est. stats, printability badge).
- **Differentiation:** High — unique read on cross-ecosystem files.
- **Verdict:** **Top candidate.** Cheap, builds directly on Doctor + Library.

### 3. Validation Center (printer-aware validation · compatibility scoring · readiness reports)
- **Feasibility:** **High.** `doctor` + `validate` already produce verdicts/scores; generalize
  the ruleset per printer profile; a "readiness report" is an aggregate + export.
- **Effort:** **M.**
- **Legal/TOS:** None.
- **Fund impact:** **High** — "validation is always on" is already the core promise; a named
  **Validation Center** with per-printer scoring + exportable readiness reports productizes it.
- **Demo impact:** High — score gauges, a shareable/exportable readiness report.
- **Differentiation:** High, and on-brand (Validate is the non-removable workflow step).
- **Verdict:** **Top candidate.** Synergizes 1:1 with Printer Profiles.

### 4. Workflow History (import → diagnose → transform → validate → export)
- **Feasibility:** **Very High.** The `library.history` table **already exists** (`add_history`/
  `get_history`) — just unused. Wire events from doctor/convert/diff/batch.
- **Effort:** **S** — emit events + a `/history` endpoint + a timeline view.
- **Legal/TOS:** None.
- **Fund impact:** **Med** — strong supporting evidence for the "workflow platform" claim.
- **Demo impact:** Med — per-project timeline reads as a "platform," not a one-shot tool.
- **Differentiation:** Med.
- **Verdict:** **Cheapest win.** Highest value-per-effort; do it first as connective tissue.

### 5. Printer Profiles (Snapmaker U1 · Prusa XL · Bambu X1C · extensibility)
- **Feasibility:** **High framework / Medium-per-printer.** Engine is already profile-driven for
  U1; generalize `data/profiles/<printer>.json` (identity + template + rules + filament arrays +
  validation set). Framework is cheap; **correctness per target** (real settings templates, valid
  output that opens in the target slicer) is the real, test-heavy work.
- **Effort:** **M (framework) + M each printer.**
- **Legal/TOS:** Low — output 3MF is an open format; no scraping. (Reverse-engineering a target's
  project schema is normal interop.)
- **Fund impact:** **Very High** — this is **THE** differentiator. Makes "any printer" *true* and
  converts positioning from "U1 converter" → "cross-printer platform."
- **Demo impact:** **Very High** — one input file → U1 **or** Prusa XL **or** X1C output.
- **Differentiation:** **Very High.**
- **Verdict:** **Highest strategic value.** Start with the framework + **one** second printer as
  proof; expand later.

---

## Ranking — Innovation Fund value per implementation effort

| Rank | Opportunity | Effort | Fund value | Value/Effort | Notes |
|---|---|---|---|---|---|
| 1 | **Workflow History** | S | Med | ★★★★★ | Table already exists; instant "platform" feel |
| 2 | **Project Intelligence** | S–M | High | ★★★★★ | Extends Doctor+Library; reframes the product |
| 3 | **Validation Center** | M | High | ★★★★ | Productizes the core promise; pairs with profiles |
| 4 | **Printer Profiles** | M + M/printer | Very High | ★★★★ | The real differentiator; framework cheap, correctness costly |
| 5 | **Discover** | L–XL | High (risky) | ★★ | Legal exposure; de-scope to official-API import |

---

## Architecture proposal (design only)

Backward-compatible; U1 remains the default so nothing regresses.

**Engine (`snapstudio_core`)**
- `profiles/` registry: each printer = `data/profiles/<id>.json` (identity tokens, base template,
  clamp/rules set, filament arrays, validation ruleset). `list_profiles()` enumerates them.
- Generalize `convert_to_u1(path)` → `convert(path, target="snapmaker_u1")`; `diagnose`/`validate`
  take a `target` profile. U1 logic moves behind the profile interface.
- New `intelligence.py` → `ProjectInfo` (source family, materials/filaments, painting, object/plate
  counts, est. stats, printability score, per-target compatibility).
- New `report.py` → readiness report (per-target scores + issues), JSON + a printable HTML/MD export.

**Local API (`snapstudio_api`)**
- `GET /profiles`, `POST /doctor {path,target}`, `POST /convert {path,target}`,
  `POST /report {path,targets[]}`, `GET /history {project_id}`, `POST /import {url}` (later, gated).

**Library (SQLite) — schema v2 (additive)**
- `projects`: + `target`, `materials` (json), `printability` (int), `source_url`, `license`.
- `history`: wire real events (import/diagnose/transform/validate/export).

**Desktop**
- **Validation Center** view: pick target(s) → per-printer score + readiness report export.
- **Project detail**: Intelligence panel (source/materials/printability) + History timeline.
- Target/printer picker in Workspace + Batch.
- **Discover** (later): `import-from-URL` behind an adapter interface, official APIs only, license +
  attribution preserved.

---

## Roadmap

- **v0.3.x (now):** ship beta, stabilize (release-readiness work continues in parallel).
- **v0.4 — "Multi-Printer Workflow Platform"** (the differentiation milestone):
  1. Workflow History (wire the existing table) — *connective tissue, S.*
  2. Project Intelligence (`ProjectInfo` + library v2) — *reframes the product, S–M.*
  3. Validation Center (per-target scoring + readiness report export) — *M.*
  4. Printer Profiles framework + **one** second target (proof, e.g. Prusa XL **or** Bambu X1C output) — *M+M.*
- **v0.5 — "Discover & Visualize":** official-API import (Thingiverse/Printables) with legal review,
  more printer targets, and a visual model/diff view.

---

## Top 3 opportunities (recommended for v0.4)

1. **Project Intelligence + Workflow History (bundled).** Lowest effort, immediately converts the
   UI from "tool" to "platform" — rich project cards + a real workflow timeline, all on existing
   parsers and the existing `history` table.
2. **Validation Center.** Productizes the always-on validation promise into a named, demoable,
   exportable feature with per-printer compatibility scoring.
3. **Printer Profiles framework + one second printer.** The decisive differentiator — proves "any
   printer," not "U1 only." Ship the framework + a single proof target first to bound risk.

## Recommended next major milestone

**v0.4 "Multi-Printer Workflow Platform."** Sequence: History → Intelligence → Validation Center →
Printer Profiles (framework + 1 proof printer). This directly neutralizes the "just a converter"
risk and gives the Innovation Fund a defensible, demoable platform story — **without** the legal
exposure of marketplace scraping, which is deferred to v0.5 under official-API-only scope.

> Design only — nothing here is implemented. Approval gate before any v0.4 work begins.
