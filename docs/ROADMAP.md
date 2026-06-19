# Snapmaker Studio — Roadmap

Three-year arc from "make any file print here" → "optimize the print" →
"run the fleet." Dates are targets, not commitments; each phase ships working,
testable software on its own. Status reflects the codebase as of 2026-06.

Pillars referenced below are defined in [PRODUCT_VISION.md](PRODUCT_VISION.md) §4.

Every phase preserves the core print flow **Input → Diagnose → Transform →
Validate → Output**; **Validate is mandatory and is never removed** from the
product or the branding. Brand: [`brand/`](brand/README.md).

---

## Near-term versions

Concrete next releases. Now that Snapmaker has open-sourced the U1 firmware
(standard Klipper/Moonraker/Fluidd, local Moonraker on `:7125`, LAN-trusted),
a **local-first Printer Hub** is feasible. Full feasibility audit:
[`design/PRINTER_HUB.md`](design/PRINTER_HUB.md). _(No printer code is shipped yet.)_

### v0.5 — Printer Hub Phase A (read-only monitoring)
- Discover the U1 on the LAN (mDNS `U1.local` / port `7125`)
- Connect via Moonraker (server-side, no auth needed on-LAN)
- Live printer status
- Toolhead / material telemetry (4 toolheads)
- Job status
- **Read-only monitoring first** — no control, no slicing

### v0.6 — Printer Hub Phase B (control)
- Upload already-sliced gcode
- Start / pause / cancel
- Print job queue

### Future — closing the loop
- Slice-and-send workflow
- Snapmaker Orca handoff **or** embedded-slicer investigation
- (Studio produces a U1 *project*; printing needs sliced gcode — this is the gap
  to close. **Print sending is not shipped today.**)

---

## Phase 1 — Foundation  ·  **DONE** (2026 H1)

The Diagnose → Transform → Validate loop, proven on real files.

- **Desktop shell** — Tauri + React app: Dashboard, Projects, Workspace,
  Settings; light/dark; drag-and-drop; local sidecar architecture; one-click
  Windows installer (NSIS, per-user, bundled engine).
- **Doctor (Diagnose)** — compatibility scoring (READY/REPAIRABLE/CONVERTIBLE/
  HIGH_RISK + /100), issue detection, read-only.
- **Conversion engine (Transform)** — Bambu/Orca → U1, geometry-only/PrusaSlicer
  3MF wrap, STL wrap, U1 identity normalization, foreign-metadata scrub,
  filament-array conformance.
- **Validation** — `is_u1_clean` gate; automated real-world corpus validator.
  **Result: 112 files, 100% clean.**
- **Sidecar** — frozen Python engine, no system Python required, zero-orphan
  lifecycle (Job Object + watchdog).

**Exit criteria met:** a Bambu/Orca or STL file → one click → U1 project that opens
in Snapmaker Orca with zero warnings. (PrusaSlicer files are detected/read; full
Prusa preservation is later-phase, not shipped.)

---

## Phase 2 — Production Workflow  ·  Year 1 H2 (2026 H2)

Move from "one file" to "my work," and broaden ecosystem coverage.

- **More ecosystems (Transform):** PrusaSlicer projects (with settings), Cura,
  Creality Print — each as an ecosystem adapter (see plugin architecture).
- **Repair toolkit:** preset-migration wizard, guided auto-fix surfaced in the
  Doctor tab, explicit per-issue remediation.
- **Batch conversion:** drop a folder; convert + validate many files; summary
  report (the corpus validator, productized for users).
- **Project library (Manage):** local project database, search, tags,
  collections, history; the Workspace becomes a real home, not a one-shot view.
- **Compare (Manage):** ship the `diff` engine in the UI — original vs U1, what
  changed, geometry-preserved proof.

**Exit:** a maker manages a library and batch-converts a backlog reliably.

---

## Phase 3 — Optimization Studio  ·  Year 2 (2027)

From "it loads" to "it prints *well*."

- **Print intelligence (Optimize):** printability scoring, material
  recommendations, time + cost estimation.
- **Optimization engine:** quality/speed/material profiles, automated tuning
  (purge, supports, seams) as composable transform passes.
- **Multi-material depth:** purge-matrix optimization, toolhead assignment
  assistance, color/painting-aware advice — the hardest, highest-value seam.
- **Profile packs v1:** declarative, documented printer profiles; first
  community-contributable packs; corpus-as-CI gates them.

**Exit:** Studio improves outcomes, not just compatibility, and the first
external profile packs land.

---

## Phase 4 — Manufacturing Platform  ·  Year 2 H2 → Year 3 (2027–2028)

From "a file" to "a fleet."

- **Multi-printer management:** fleet dashboard, queue management, remote
  monitoring (Moonraker/Klipper-class first, given U1 lineage).
- **Simulation:** preview/toolpath analysis, failure prediction before printing.
- **Plugin SDK (public):** stable contracts for ecosystem adapters, printer
  profiles, transforms, validators, and views; docs + templates.

**Exit:** small shops run several printers through Studio end to end.

---

## Phase 5 — Digital Manufacturing OS  ·  Year 3+ (2028+)

- **Plugin marketplace:** community + vendor extensions, premium packs,
  rev-share; certified vendor profiles.
- **Ecosystem governance:** move toward a neutral foundation so no single vendor
  controls the translation layer.
- **AI-assisted troubleshooting:** corpus-grounded diagnosis and fix suggestions.

**Exit:** a self-sustaining, open platform — the default home for design-to-
production workflows across vendors.

---

## Cross-cutting tracks (every phase)

- **Reliability:** expand the validation corpus; corpus run wired into CI;
  failure taxonomy kept current. Never regress the success rate.
- **Trust:** open core, transparent changelog, inspectable transforms.
- **Polish:** the novice one-click experience stays first-class as power features
  grow.
- **Release readiness (near-term):** real icon/branding and Windows code signing
  before any public GA (current blockers tracked in the pre-release report).
