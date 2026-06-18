# v0.4 Phase 1 — Execution Plan (Simple Mode · Design Insights · My Designs)

**Date:** 2026-06-18 · **Status:** planning only (no implementation) · **Source of truth:** `V0_4_PRODUCT_PROPOSAL.md`

**Goal:** turn a file tool into a **design-centric workflow platform** — novice-first, zero
3MF/profile/filament jargon, **Advanced Mode preserved** unchanged for power users.

**Grounding (what already exists):** routes `Dashboard` `/`, `Projects` `/projects`,
`LiveWorkspace` `/workspace`, `Batch` `/batch`, `Settings`; library tables `projects` +
unused **`history`** (`add_history`/`get_history`); endpoints `/doctor` `/convert` `/library`
`/library/delete`; `/doctor` already returns verdict, score, family, counts, painted,
issues, recommended_action. Theme already persists via a Zustand store — Mode follows the
same pattern.

---

## Cross-cutting: novice-language mapping (Simple Mode only)
| Engine value | Simple-Mode label |
|---|---|
| verdict READY / REPAIRABLE / CONVERTIBLE / HIGH_RISK | ✅ Ready · 🛠 Needs a quick fix · ✨ New project from a model · ⚠️ Might not print |
| score 0–100 | ★ Print-Readiness (5 stars) |
| filament_count | "N colors" |
| object_count / plate_count | "N parts" |
| family (bambu/orca/prusa/stl) | "from a Bambu design" / "a plain model (STL)" |
| painted=true | "painted areas kept" |
| convert / output 3MF | "Get it ready" / "print-ready copy" |

Advanced Mode keeps the raw terms (verdict, score, 3MF, filaments) exactly as today.

---

## Feature 1 — Simple Mode (the shell)

**Screens affected:** `Settings` (add toggle); `AppShell`/`Sidebar` (mode-aware nav + labels);
all Simple screens read the mode. Advanced screens unchanged.

**Data model changes:** none in SQLite. New persisted UI pref `mode: "simple" | "advanced"`
(default **simple**) in a Zustand store mirrored to `localStorage` (same pattern as theme).

**API changes:** none.

**UI changes:**
- `store/mode.ts` (new): `{ mode, setMode }`, persisted.
- `Settings`: "Experience" section → **Simple (recommended)** / **Advanced** radio.
- `Sidebar`/labels: Simple shows "Home / My Designs / My Printers*"; Advanced shows
  "Dashboard / Projects / Batch / Workspace". (*My Printers arrives in Phase 2 — hidden in P1.)
- Routing: same routes; Simple renders beginner components, Advanced renders current ones.
  A thin `useMode()` switch at the route/component level — no route duplication.

**Migration plan:** first launch with no stored mode → default **simple**; show a one-time
banner "Power user? Switch to Advanced in Settings." Existing users land in Simple too (safe;
Advanced is one click away).

**Estimate:** ~1 eng week (toggle + plumbing + relabel). No backend.

---

## Feature 2 — Design Insights ("What's in this design")

**Screens affected:** new **Design Insights** screen in Simple Mode (the Simple equivalent of
`LiveWorkspace`); reachable from Home (after add) and from My Designs. Advanced Mode keeps
`LiveWorkspace` (Doctor/Convert/Compare) verbatim.

**Data model changes (MVP):** none — derive everything from the existing `/doctor` result.
*Enhancement (later, not P1):* engine bounding-box extraction for "Size: 12×8×15 cm" and
material-name reading; until then the Size row is omitted (don't fake it).

**API changes (MVP):** none — reuse `POST /doctor`. (Optional later: `/insights` that bundles
doctor + bbox + material names in one call; not needed for P1.)

**UI changes:**
- `routes/DesignInsights.tsx` (new): plain-language card built from `doctor.data` →
  colors (filament_count), parts (object_count), source (family), "painted areas kept"
  (painted), and a **★ Print-Readiness** derived from score. Primary button **Get it ready**
  (calls existing `runConvert`); secondary **Check details** (opens the existing issues list).
- A `readinessStars(score)` + `familyLabel(family)` + `verdictBadge(verdict)` presenter util
  (pure, unit-testable).

**Migration plan:** none (read-only view over existing data).

**Estimate:** ~1–1.5 eng weeks (presenter + screen + states). MVP needs no backend.

---

## Feature 3 — My Designs ("Everything I've worked on" + history)

**Screens affected:** Simple **My Designs** (Simple equivalent of `Projects`, relabeled);
new per-design **history timeline** (small panel on Design Insights / a design detail).
Advanced `Projects` unchanged.

**Data model changes:** **none to schema** — the `history` table already exists. We start
*writing* to it: on each `/doctor` and `/convert` (and batch item), record an event
`(project_id, action, detail, at)`.

**API changes:**
- Wire `service.record_diagnosis` / `record_conversion` to also call `library.add_history`.
- New **`POST /history { project_id }`** → `library.get_history` (endpoint doesn't exist yet;
  the engine function does).

**UI changes:**
- `routes/Projects.tsx` already reads `/library` → add a Simple-Mode relabel + a per-card
  status in plain words. New small **Timeline** component (added → checked → made ready)
  fed by `/history`.

**Migration plan:** `history` is created by `connect()` for all existing DBs (idempotent
`CREATE TABLE IF NOT EXISTS`), so no migration; old projects simply have empty history until
their next action. No `user_version` bump needed.

**Estimate:** ~0.5–1 eng week (history wiring + endpoint + timeline + relabel).

---

## Implementation order
1. **Simple Mode shell** (unblocks the rest; lets Simple screens exist alongside Advanced).
2. **Design Insights** (highest demo value; pure presentation over `/doctor`).
3. **My Designs + history** (wire the existing table; relabel Projects; timeline).

Rationale: 1 is the prerequisite; 2 is the visible "wow"; 3 is cheap and reinforces the
"workflow platform" story. None touches the engine's conversion correctness.

## Total Phase 1 estimate
~2.5–3.5 eng weeks for all three, **no SQLite schema migration**, **no engine-correctness risk**
(read-only presentation + history logging + a UI mode flag).

---

## Smallest 1-week vertical slice (max Innovation Fund demo lift)

**Slice: "Simple Mode happy path over the existing engine."**
Home (drop a design) → **Design Insights** (plain language + ★ Print-Readiness) → **Get it
ready** (existing convert) → **Done** ("Ready to print! Original kept safe").

**Scope (1 week):**
- `store/mode.ts` + default Simple + Settings toggle (thin).
- `DesignInsights.tsx` built from the existing `/doctor` result + `readinessStars` presenter.
- A beginner **Done** screen reusing the existing `convert` result.
- Relabel Home drop zone copy.

**Explicitly out of this slice:** My Designs timeline, history endpoint, bounding-box/size,
material names, Compatibility Matrix, Your Printers. (All later phases.)

**Why this slice:** it requires **zero backend changes** (reuses `/doctor` + `/convert`),
carries **zero conversion-correctness risk**, and is exactly what reframes the product on
camera — a novice drops a file and sees *"4 colors · from a Bambu design · ★★★★☆ ready for your
U1 · [Get it ready]"* instead of verdicts and 3MF. It's the single highest demo-value change per
engineering day, and it's a true end-to-end path (input → understand → ready → done).

**Demo script delta:** record the slice as the new opening of the Innovation Fund demo —
"from downloaded file to "Ready to print!" in three taps, no jargon."

> Planning only — no code. Approval gate before the 1-week slice begins.
