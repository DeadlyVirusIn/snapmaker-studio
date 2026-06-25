# Snapmaker Studio — Roadmap

Three-year arc from "make any file print here" → "optimize the print" →
"run the fleet." Dates are targets, not commitments; each phase ships working,
testable software on its own. Status reflects the codebase as of 2026-06.

Pillars referenced below are defined in [PRODUCT_VISION.md](PRODUCT_VISION.md) §4.

Every phase preserves the core print flow **Input → Diagnose → Transform →
Validate → Output**; **Validate is mandatory and is never removed** from the
product or the branding. Brand: [`brand/`](brand/README.md).

---

## Shipped (as of v0.4.0-beta.17)

- **Scale Doctor — prepare scaled copy (STL) — SHIPPED (beta.17).** Creates a real
  scaled U1 3MF from an STL (geometry truly scaled; original never modified). 3MF scaled
  export is next (blocked with a clear message for now).
- **Compatibility Doctor — Prepare U1 copy — SHIPPED (beta.17).** Wires the existing
  repair/convert path to a one-click clean-U1-copy action (no more dead end).

### Next
- Verified 3MF scaled export (multi-part / multi-plate uniform scaling, Orca-checked).
- Per-card Business pricing (Cost/Pricing/Profit honoring the Settings filament price).
- File-aware First Layer Doctor (use the bed/stability-aware path after a file pick).

## Shipped (as of v0.4.0-beta.15)

LIVE in the published beta — routes, endpoints, and tests exist (mocked where no
hardware is in CI). Status is one of **SHIPPED**, **partially shipped**, or **PLANNED**.

- **Printer Hub — monitoring + control + send — SHIPPED.** Discover the U1
  (`U1.local:7125`), live status, temps, 4 toolheads, history, health, firmware
  (read-only); plus user-confirmed control: pause / resume / cancel / start, upload
  sliced gcode, emergency stop. Studio never auto-starts. Real-U1 hardware verification
  is a manual checklist ([`PRINTER_HUB_VERIFICATION.md`](PRINTER_HUB_VERIFICATION.md)) —
  there is no U1 in CI.
- **Close-the-loop send — SHIPPED (no slicing).** Upload already-sliced gcode and start
  a print from Studio. Studio does **not** slice; you slice in Snapmaker Orca and send
  the exported gcode.
- **Plate Color Remap — 2D visual preview SHIPPED; 3D render PLANNED.** The wizard shows
  a 2D plate map (object colour chips, from→to, protected painted/gold accents, untouched
  plates). A full rendered 3D plate preview is still future.
- **Print Quality Doctor — evidence integration SHIPPED.** Symptom advice grounded in the
  user's own file via the other doctors (overhang/supports, tip/stability, first-layer
  area, bed fit, materials, colours). Advisory, no guarantees.
- **Source Check — file/source detection SHIPPED.** Detects STL / generic 3MF /
  Bambu-family (Orca/Bambu, +U1 flag) / PrusaSlicer / Cura; reports what Studio can read,
  what it cannot convert yet, and the safe next step. Repair/preset **migration**
  (actually preparing a non-U1 source) is PLANNED.
- **Studio Model Browser — SHIPPED.** Approved 3D-model sites in a locked, Studio-owned
  browser window; manual download → Open in Studio ([`model-browser-direction.md`](model-browser-direction.md)).
- **Open in Snapmaker Orca — SHIPPED.** One-way handoff of a validated U1 copy to an
  installed Snapmaker Orca. Studio does not slice or control Orca.
- **Doctors + workflow — SHIPPED:** Project, Compatibility, Scale, First Layer,
  Multi-Material, Cost/Pricing/Profit; Batch Prepare; Project Library; Compare/diff.

## Near-term (next)

The U1 firmware is open (stock Klipper/Moonraker/Fluidd, local Moonraker on `:7125`,
LAN-trusted), so the Printer Hub above is built on solid ground. Next focus is **proof +
beginner polish** (real screenshots, hardware verification, onboarding), then deeper
conversion — not new headline features.

### Distribution & trust
- The current Windows beta installer is **unsigned**, so SmartScreen shows
  "Unknown publisher" (see [`windows-install.md`](windows-install.md)).
- **Paid code signing is deferred** — planned after Snapmaker Studio shows adoption
  or wins Innovation Fund support. It is **not a release blocker**. Until then we use
  free trust mitigations only: release from the official GitHub repo, publish the
  installer **SHA256**, and provide a PowerShell verification command. No signing is
  claimed while the installer is unsigned.
- Optionally evaluate **Microsoft Store** distribution later as an additional
  trusted channel.

### Planned / future
- **Repair / preset migration wizard** — Source Check already *detects* non-U1 sources
  (PrusaSlicer/Cura/generic); the next step is safely *preparing* a clean U1 copy from
  them, with clear "what carried over / what didn't" reporting.
- **Rendered 3D plate preview** — a full geometry render of the plate (the 2D colour-map
  preview ships today; 3D is the future upgrade).
- **Deeper Print Quality intelligence** — extend the evidence base with more signals and
  known-good deltas.
- **Corpus validator wired into CI**; broader ecosystem adapters.
- **Embedded slicing is out of scope** — slicing stays in Snapmaker Orca; Studio prepares
  and (for already-sliced gcode) sends.

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
