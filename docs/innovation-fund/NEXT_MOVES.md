# Next moves — what would make Studio elite

Written after the 2026-08-22 sprint, against a **Phase 1 submission deadline of
7 September 2026**. Ranked, with the reasoning visible so the ranking can be
argued with.

Scoring per item, each 0–5: user pain solved (**P**), Fund differentiation (**D**),
judge visibility (**J**), novice benefit (**N**), technical depth (**T**), open-
ecosystem value (**E**), reliability benefit (**R**), implementation confidence
(**C**); minus complexity (**cx**) and regression risk (**rr**).

---

## The honest read on where Studio stands

**Strong:** the only pre-print validation project in a field of 41. The only one
that costs a print. The only one that names the right community tool for a file.
Evidence grading and refusal-to-guess are a discipline, not a feature, and they
are enforced by tests.

**Weak, and it is the same weakness twice:**

1. **Community visibility.** 20% of the score is community, weighted partly on
   GitHub stars. Studio is at the bottom of the measured field while u1hub is at
   51★. This is not a product problem; it is a "nobody has seen it" problem.
2. **Nothing to see.** There are no current screenshots, no demo video, and the
   installer is unsigned. A judge with four minutes and a SmartScreen warning may
   never reach the good part.

Every item in tier 1 attacks one of those two.

---

## Tier 1 — before the deadline (highest value per hour)

### 1. A 90-second demo video, published
**P4 D4 J5 N4 T1 E2 R0 C5 · cx1 rr0**

The script is written and reproducible
([DEMO_SCRIPT_90_SECONDS.md](DEMO_SCRIPT_90_SECONDS.md)) against a sample project
in the repository. A judge who watches 90 seconds understands the product; a judge
who has to install an unsigned beta may not. This is the single highest-leverage
remaining action and it needs recording, not engineering.

### 2. Current screenshots in the README
**P3 D3 J5 N5 T1 E1 R0 C5 · cx1 rr0**

The README's screenshot references predate several redesigns. The placement card
and the "best tool for this project" panel are the two most persuasive surfaces in
the app and neither has ever been pictured. Anonymise per the project's own rules.

### 3. Tell the ecosystem it was named
**P2 D5 J3 N1 T0 E5 R0 C4 · cx1 rr0**

Studio's registry points people at FOrcaSlicer, ImageMap, U1 Print Hub, the
Snapmaker U1 Toolkit and the MakerWorld converter. Those maintainers do not know.
A short, non-promotional issue or discussion post on each — "Studio detects X in a
project and points users here; correcting our description is a one-line PR" — is
honest, useful to them, and the most credible route to community visibility that
exists. It also invites exactly the contribution the registry was designed for.

### 4. Windows code signing
**P4 D2 J4 N5 T1 E1 R3 C2 · cx2 rr1**

Every competing project ships unsigned and documents the SmartScreen workaround.
Being the one that does not is a real differentiator and removes the largest
first-run drop-off. Cost and identity verification are the blockers, not code —
`docs/windows-code-signing.md` already scopes it.

### 5. A one-command self-check for the judge
**P2 D3 J5 N2 T2 E3 R2 C5 · cx1 rr0**

`u1convert selfcheck` running the whole documented flow over the shipped sample
and printing a pass/fail table. Turns "clone and hope" into 20 seconds of visible
evidence, and doubles as a smoke test for a fresh install.

---

## Tier 2 — strongest product work after the deadline

### 6. Multi-colour intelligence beyond four toolheads
**P5 D5 J4 N5 T5 E4 R2 C3 · cx3 rr2**

The gap nobody has filled. A U1 has four toolheads; projects routinely carry more
colours. Studio already refuses to auto-cap them, which is correct but not helpful.
What is missing is the classification: **layer-based** colour (distinct Z ranges —
can be printed with manual swaps at named layers) versus **painted** colour (stored
per-triangle — swaps are impossible and the colour count must come down).

Studio can already read both. Turning that into "this project needs 6 colours; 4
are painted and must map to toolheads, 2 change at layer 41 and layer 96, so you
can swap by hand" would be the most useful multi-colour answer in the ecosystem,
and it is analysis rather than slicing — squarely in Studio's lane.

### 7. Fidelity audit: what conversion silently drops
**P4 D5 J4 N3 T4 E4 R3 C4 · cx2 rr1**

`Metadata/layer_heights_profile.txt`, `custom_gcode_per_layer.xml`,
`layer_config_ranges.xml` and per-object setting overrides are carried, rewritten
or dropped by every converter in this field, and **none of them documents which**.
Studio can enumerate exactly what a prepared copy preserved and what it could not,
per part. That is a report no competitor can produce about themselves, and it is
the natural extension of the preservation guard that already exists.

### 8. Printer Doctor: project ↔ printer readiness
**P5 D4 J4 N5 T3 E3 R4 C4 · cx2 rr1**

Printer Hub reports printer state; the Doctors report project needs. Nothing joins
them. "This project needs 6 filaments and your printer reports 4 loaded", "this
project uses a 0.2 nozzle and your printer reports 0.4", "this project relies on
object exclusion and your firmware exposes it" — all from data Studio already
collects on both sides. High user value, low new machinery.

### 9. Reversible fix ledger
**P4 D4 J4 N5 T3 E3 R4 C4 · cx2 rr2**

Every fix already writes a new copy and reports its changes. What is missing is
one place that lists them, shows before/after, and offers "revert to the original"
as a first-class action rather than a file the user has to find. This is what turns
a set of fixes into a trustworthy fix *engine*, and it is the last piece of the
Diagnose → Explain → Fix → Validate → Undo loop.

### 10. Print-profile matching by layer height
**P3 D2 J2 N4 T2 E2 R2 C4 · cx2 rr2**

The one documented converter rule Studio does not implement: choose the U1 base
profile whose layer height matches the source instead of always using one base.
Real quality impact on conversion fidelity, modest work, contained risk.

---

## Tier 3 — platform bets worth making once the above lands

### 11. Diagnostic packs as data
**P3 D5 J3 N2 T4 E5 R2 C3 · cx3 rr2**

The ecosystem registry proved that a rule set can live in JSON with a schema and a
test that rejects rules referencing facts the engine cannot measure. The same shape
applied to *diagnostics* would let the community contribute checks — "this filament
at this layer height on this plate tends to warp" — without touching engine code.
That is what makes Studio a foundation rather than an application, and it is the
strongest long-term answer to the Fund's openness criterion.

### 12. A second printer
**P2 D4 J3 N1 T4 E4 R2 C3 · cx4 rr3**

The claim "not U1-only by construction" is currently unproven. Adding one more
Snapmaker machine — profile plus capability detection, no per-check branching —
would prove it. Worth doing precisely because it will expose every place a U1
assumption is still hard-coded.

### 13. Project reproducibility manifest
**P2 D5 J3 N1 T4 E5 R3 C4 · cx2 rr1**

A signed, versioned JSON summary of everything Studio knows about a project —
provenance, traits with confidence, changes applied, validation result — emitted
alongside a prepared copy. Makes a converted project auditable by a third party and
gives other tools something concrete to consume. Natural successor to `traits`.

---

## Explicitly not doing

- **Slicing, or forking a slicer.** It would make Studio a worse Orca overnight.
- **A second printer dashboard.** Fluidd already ships on the machine.
- **A browser extension.** The nearest competitor's DOM coupling to one site broke
  it in three of its last four releases. Any local file is the better input.
- **Requiring Extended Firmware.** Most owners run stock, and its presence cannot
  be reliably detected anyway.
- **LLM features.** Everything Studio does today is deterministic and explainable.
  An "AI" button would weaken the one property that makes it trustworthy.
- **Chasing feature count.** A polished 8/10 capability beats six unfinished ones,
  and the Fund's criteria reward depth over breadth.

---

## If only one thing gets done

Record the video. The product's problem is not capability any more; it is that
nobody has watched it work.
