# Snapmaker Studio — Product Vision

> **The Operating System for Multi-Material 3D Printing.**

Snapmaker Studio is not a converter. Conversion is the first useful thing it
does — the wedge — not the product. The product is a single, local-first
desktop platform that owns the *workflow* between a 3D model and a reliable,
multi-material print, across every slicer and every printer.

**The print flow — the spine of the product and the brand:**
**Input → Diagnose → Transform → Validate → Output.**
Validate is a mandatory stage, never skipped: every conversion is *proven clean*
before output. (Brand: see [`brand/`](brand/README.md). Tagline: _One place. Any
file. Any printer. Perfect prints._)

---

## 1. Mission

**Give makers one place to take any model, from any ecosystem, to a reliable
multi-material print — without losing their work to format wars, vendor lock-in,
or silent compatibility failures.**

(Full mission statement: see [PRODUCT_MISSION.md](PRODUCT_MISSION.md).)

## 2. Vision

In three years, when a maker downloads a model, inherits a project, or switches
printers, the answer to "will this print, and how do I make it print here?" is a
single app: **Snapmaker Studio.** It diagnoses, repairs, converts, optimizes,
validates, and manages — locally, openly, and across ecosystems — the way an IDE
became the home for code regardless of language or compiler.

Multi-material is the forcing function. Single-color printing is largely solved;
multi-material/multi-tool is where compatibility breaks, presets diverge, purge
math goes wrong, and files silently fail to load. That is exactly the seam
Snapmaker Studio operates in, and it widens as the ecosystem fragments.

## 3. Core Principles

1. **Local-first.** No account, no cloud, no telemetry required. Files never
   leave the machine. Privacy and offline reliability are features, not promises.
2. **Preserve, never destroy.** Geometry, painting, and color are sacred. The
   engine fails safe and never silently reduces colors or mutates meshes. Inputs
   are never overwritten.
3. **Cross-ecosystem by default.** Bambu, Orca, Prusa, Cura, Creality, raw STL —
   inputs are first-class. We meet users where their files already are.
4. **Truthful state.** "Validated" must mean it actually loads clean. The Doctor
   and validator never report success they can't prove (verified against a
   real-world corpus, not a happy path).
5. **Open and inspectable.** The engine is open source. A maker can read exactly
   what we change in their file. Trust is earned by transparency.
6. **Extensible.** Every capability is a module behind a stable contract, so the
   community and vendors can add ecosystems and tools without forking.

## 4. Product Pillars

The platform is organized into five durable pillars. Features map to pillars;
pillars do not change when printers do.

| Pillar | What it owns | Today |
|---|---|---|
| **Diagnose** | Compatibility scoring, issue detection, "will it print here?" | Doctor (READY/REPAIRABLE/CONVERTIBLE/HIGH_RISK, score/100) |
| **Transform** | Convert/repair/normalize across ecosystems, preserving design | Bambu/Orca→U1, Prusa/geometry-only 3MF wrap, STL wrap, identity normalization |
| **Validate** | Prove output is clean before the user wastes a print | `is_u1_clean` gate + real-world corpus (112 files, 100%) |
| **Manage** | Projects, versions, libraries, comparison, history | Workspace + diff foundation (mock UI shipped; engine in progress) |
| **Optimize** | Printability, material/cost/time intelligence, tuning | Optimization profiles (foundation in engine) |

The **Diagnose → Transform → Validate** loop is the proven core today; **Manage**
and **Optimize** are where the platform compounds.

## 5. 3-Year Roadmap

See [ROADMAP.md](ROADMAP.md) for the phased plan. Summary arc:
- **Year 1 — Reliable cross-ecosystem conversion + project workspace.** Own the
  "make any file print on my printer" job, end to end, with a polished app.
- **Year 2 — Optimization Studio + project library + batch.** Move from "it
  loads" to "it prints *well*"; manage many projects, not one file.
- **Year 3 — Manufacturing platform + plugin marketplace.** Multi-printer,
  simulation/failure-prediction, and a community/vendor extension ecosystem.

## 6. Plugin Architecture Vision

Snapmaker Studio is a **kernel + plugins**, not a monolith. The kernel is the
pure engine (`snapstudio_core`) and the local sidecar API; everything ecosystem-
or printer-specific is a plugin behind a stable contract.

Plugin types:
- **Ecosystem adapters** — read/normalize a slicer family (Bambu, Orca, Prusa,
  Cura, Creality). Adding a slicer = adding an adapter, not editing the core.
- **Printer profiles** — a printer's identity block, presets, bed, and rules
  (e.g. the U1 identity layer). New printer = new profile pack.
- **Transforms** — repair/optimize passes (purge tuning, support strategy,
  preset migration) that run over the normalized model.
- **Validators** — pluggable "is it clean for target X?" checks.
- **Views** — UI panels/workflows in the desktop shell.

Why this matters: the hard-won knowledge (what triggers a "Customized Preset"
warning, min-4 filament blocks, array-length consistency) lives in declarative
profile/adapter packs that a community can extend and a vendor can certify —
without a single fork. The corpus validator becomes the CI that keeps every
plugin honest.

## 7. Ecosystem Strategy

- **Be the neutral layer.** We are not a slicer and not a printer vendor. We are
  Switzerland for 3D printing files — which is precisely why both makers and
  vendors can trust us.
- **Files as the network.** Every shared/inherited project that "just works" in
  Studio is a proof point. Compatibility is the growth loop.
- **Community profile/adapter packs.** Crowdsource the long tail of slicers and
  printers; the kernel + corpus keep quality high.
- **Vendor partnerships.** Printer makers gain a polished, open onboarding path
  for foreign files onto their hardware without building it themselves.
- **Knowledge as a moat.** The validation corpus + categorized failure taxonomy
  is a compounding asset no single slicer is incentivized to build.

## 8. Why Snapmaker Studio should exist even if OrcaSlicer exists

OrcaSlicer is an excellent **slicer** — its job is to turn *one* prepared,
already-compatible project into G-code for a configured printer. Studio owns a
different, unmet job: **getting a foreign/broken/ambiguous file *to* that
clean, compatible state in the first place — across ecosystems.**

- **Orca assumes you're already in its world.** It doesn't repair a Bambu H2D
  project so it loads clean on a Snapmaker U1; it shows the "Customized Preset"
  and "newer version" warnings (the exact problem Studio eliminates).
- **Orca is per-fork, per-vendor.** Snapmaker Orca, Bambu Studio, and stock Orca
  diverge. Studio is the layer *above* the forks that reconciles them.
- **Orca is a slicer, not a workflow.** No cross-ecosystem diagnosis, no
  preservation-guaranteed conversion, no project library, no corpus-validated
  "this will load clean," no multi-printer management.
- **Studio makes Orca better.** The output of Studio is a clean project that
  opens warning-free in (Snapmaker) Orca. We are complementary, not competitive —
  the on-ramp to the slicer, not a replacement for it.

In short: Orca slices; Studio makes anything *sliceable here*.

## 9. Why it becomes more valuable as new printers appear

Studio's value scales with **fragmentation**, and the market is fragmenting fast
(Bambu, Snapmaker U1, Creality K-series, Prusa XL/CORE, Anycubic, etc.), each
with its own format dialect, preset identity, and multi-tool quirks.

- **Each new printer = a new conversion target and a new source.** The value of
  a universal translator grows with the number of languages — combinatorially.
- **Migration is the recurring pain.** Every maker who switches or adds a printer
  faces "rebuild years of projects." Studio turns that into a one-click convert.
- **Multi-material multiplies the edge cases** (toolhead counts, purge matrices,
  filament-array consistency) — exactly where Studio's engine is differentiated.
- **The corpus + profile packs are leverage.** Supporting printer N+1 is adding a
  profile pack validated by the existing corpus, not a rewrite. Marginal cost
  falls while addressable value rises.

A slicer's value is roughly constant per user; Studio's value rises with every
printer and ecosystem added to the world.

## 10. Innovation Fund positioning

Snapmaker Studio is a strong fit for an innovation/ecosystem fund (e.g.
Snapmaker's) because it **grows the hardware's addressable market without the
vendor building or maintaining it**:

- **De-risks switching to U1.** A Bambu/Prusa owner's existing library becomes
  U1-ready in one click — directly lowering the barrier to buying the printer.
- **Open-source + local-first** aligns with maker trust and avoids the vendor
  having to own a cloud/account product.
- **Leverage, not headcount.** A small grant funds a platform that the community
  extends; the vendor gets an onboarding funnel and goodwill, not a cost center.
- **Defensible public good.** Funds a neutral compatibility layer that benefits
  the whole ecosystem while disproportionately benefiting the sponsoring printer
  (which gets first-class, certified profile support).
- **Measurable.** Corpus success rate, converted-files count, and printers
  supported are concrete milestones a fund can track.

## 11. Open-source strategy

- **Core is open (MIT).** The engine (`snapstudio_core`), CLI, and desktop shell
  are open source. Trust in a tool that rewrites your files *requires* this.
- **Open profile/adapter format.** Printer profiles and ecosystem adapters are
  declarative, documented, and community-contributable.
- **Corpus-as-CI, in the open.** The validation methodology (not users' private
  files) is public, so contributions can't regress reliability.
- **Public roadmap + transparent changelog.** Build in the open; community
  decides the long tail of supported hardware.
- **Governance toward a foundation** as adoption grows, to guarantee neutrality
  (no single vendor controls the translation layer).

## 12. Commercial strategy

Open core, with revenue that never compromises the local-first, no-lock-in
promise. The free, open desktop platform stays fully capable for makers.

- **Studio Pro (individual/prosumer).** Convenience + power on top of the open
  core: batch/fleet workflows, advanced optimization, simulation/failure
  prediction, priority profile packs. Local; one-time or modest subscription.
- **Vendor partnerships / certified profiles.** Printer makers sponsor and
  certify first-class profile packs and onboarding flows.
- **Innovation/ecosystem grants** (see §10) fund platform milestones.
- **Marketplace rev-share** (Year 3) on premium community plugins.
- **Optional team/manufacturing tier** for multi-printer/queue management in
  small production shops.

Non-goals: no ads, no selling user data, no cloud-lock, no paywalling basic
compatibility. The translation layer for the ecosystem must stay trustworthy and
free at its core.

## Traction & proof points (today)

Not a deck promise — shipped and measured:

- **112 real-world files, 100% clean conversion** (Bambu, Orca, Prusa/geometry,
  STL; single + multi-color; custom presets; large + non-English files), proven
  by an automated validation corpus.
- **Zero-warning output in Snapmaker Orca** on real user files (e.g. a Bambu H2D
  project → U1, confirmed warning-free by a user).
- **One-click Windows installer** (~14 MB) with a bundled engine — **no Python,
  no terminal, no cloud, no account**.
- **Zero orphan processes** across graceful close, crash, and force-kill
  (OS-level Job Object guarantee).
- **Truthful validation:** conversion reports success only when the output is
  provably clean (no foreign Bambu/BBL/H2D identity survives).

### Metrics we steer by
Corpus success rate · ecosystems supported · printers supported · converted-files
count · "validated-but-warns" defects (target: 0) · geometry/color-loss incidents
(target: 0) · clicks from foreign file → clean print (target: 1).

---

### One-line positioning

> **OrcaSlicer slices. Snapmaker Studio makes anything sliceable — anywhere.**
