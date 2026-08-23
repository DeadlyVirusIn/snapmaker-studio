# Next moves — what would make Studio elite

Updated **2026-08-23**, after the judge-readiness sprint. Phase 1 submissions
close **7 September 2026**.

Items completed since the previous version of this document are listed first, so
this file never reads as if shipped work were still pending.

---

## The honest read on where Studio stands

**Strong.** In the Phase 1 field as surveyed on 2026-08-22
([COMPETITOR_MATRIX.md](COMPETITOR_MATRIX.md)), Studio was the sole entry doing
pre-print validation, the sole one costing a print, and the sole one naming the
right community tool for a file. That survey is dated and needs re-checking for
Phase 2. Since then Studio has added the project↔printer join, a fidelity audit,
an auditable fix ledger with a real way back, colour classification beyond four
toolheads, and a one-command self-check — all with evidence grading and
refusal-to-guess enforced by tests rather than by convention.

**Weak, and it is now one weakness rather than two.** Visibility. 20% of the Fund
score is community, weighted partly on GitHub stars, and Studio sits at the bottom
of the measured field. The product no longer has a "nothing to see" problem —
there are current screenshots from the running build and a verified demo script —
but nobody has watched it work, and the installer is still unsigned.

---

## Done in this sprint

| Was | Now |
|---|---|
| Current screenshots | Captured from the beta.22 build; README leads with them |
| One-command self-check | `u1convert selfcheck`, 15 checks, real code paths, exits non-zero on failure |
| Project ↔ printer readiness | `preflight.py` — materials vs toolheads, nozzle, real bed, capabilities, state; unknowns stay unknown |
| Fidelity audit | `fidelity.py` — per element, including `unsupported` and `unverified`; overclaims in public copy corrected |
| Reversible fix ledger | `fix_ledger.py` — every produced file recorded; return-to-original; shareable export with paths stripped |
| Multi-colour beyond four toolheads | `color_plan.py` — shares-layers vs arrives-higher-up vs cannot-classify, with heights and estimated layers |
| Print-profile matching | `process_preset.py` — the preset label now describes the project's actual layer height |
| Release governance | `test_release_docs.py` — duplicate changelog entries, hash drift and a stale trust file are now build failures |
| Demo script | Re-verified beat by beat against the current build, with the exact click path |
| Ecosystem outreach | [ECOSYSTEM_OUTREACH.md](ECOSYSTEM_OUTREACH.md) — factual, non-promotional drafts for a human to post |

---

## Tier 1 — before the deadline

### 1. Record and publish the 90-second demo
**P4 D4 J5 N4 T1 E2 R0 C5 · cx1 rr0**

[DEMO_SCRIPT_90_SECONDS.md](DEMO_SCRIPT_90_SECONDS.md) is verified against the
current build with the exact click path and the frames already captured. This
needs a screen recorder and one take, not engineering. It is the single highest
remaining item and it cannot be done from an autonomous environment.

### 2. Post the ecosystem notes
**P2 D5 J3 N1 T0 E5 R0 C4 · cx1 rr0**

The drafts exist and are deliberately not automated — posting to other people's
issue trackers is a human decision. This is the most credible route to community
visibility that does not involve asking for stars.

### 3. Windows code signing
**P4 D2 J4 N5 T1 E1 R3 C2 · cx2 rr1**

Every competing project ships unsigned and documents the SmartScreen workaround.
Being the one that does not removes the largest first-run drop-off. Blocked on
purchasing a certificate and identity verification, both human gates.

### 4. Complete the beta.22 GUI acceptance
**P3 D1 J4 N3 T1 E1 R5 C4 · cx1 rr0**

[TRUST_STATUS.md](../TRUST_STATUS.md) lists eighteen automated checks as passing
and twelve GUI/hardware items as pending, each with the smallest exact check.
Working through that list on an installed build is what moves beta.22 from
PARTIAL to accepted.

---

## Tier 2 — strongest product work after the deadline

### 5. Painted-colour enumeration
**P5 D5 J4 N4 T5 E3 R2 C2 · cx4 rr2**

`color_plan` currently reports painted colours as unclassified, because per-triangle
paint data is encoded and Studio will not guess. Decoding it properly would turn
"cannot classify" into a real answer for the hardest multi-colour projects — the
single biggest remaining accuracy gain, and genuinely difficult.

### 6. Diagnostic packs as data
**P3 D5 J3 N2 T4 E5 R2 C3 · cx3 rr2**

The ecosystem registry proved a rule set can live in JSON with a schema and a test
that rejects rules referencing facts the engine cannot measure. The same shape for
*diagnostics* would let the community contribute checks without touching engine
code. This is the strongest long-term answer to the Fund's openness criterion.

### 7. Preflight against a real printer, on hardware
**P4 D3 J3 N4 T2 E3 R4 C3 · cx2 rr1**

Every preflight branch is tested without hardware, which is the right way to build
it but not the same as knowing what a real U1 reports. In particular
`loaded_filaments()` reads a firmware object whose exact shape varies by build, and
returns "not reported" when it does not recognise one. One session with a real
printer would confirm or correct it.

### 8. A second printer
**P2 D4 J3 N1 T4 E4 R2 C3 · cx4 rr3**

"Not U1-only by construction" is still unproven. Adding one more machine — profile
plus capability detection, no per-check branching — would prove it, and will expose
every place a U1 assumption is still hard-coded.

### 9. Project reproducibility manifest
**P2 D5 J3 N1 T4 E5 R3 C4 · cx2 rr1**

A versioned JSON summary emitted beside a prepared copy: provenance, graded traits,
changes applied, fidelity result. Makes a converted project auditable by a third
party. Most of the content already exists across `traits`, `fidelity` and the
ledger; this is the assembly.

### 10. Cost from a sliced project, end to end
**P3 D4 J3 N4 T2 E2 R2 C4 · cx2 rr1**

`project_cost` reads figures a slicer recorded, but the loop is only closed when a
user slices in Orca and reopens the saved project. Making that round trip a
first-class flow — "slice it, then bring it back here" — turns a capability into a
habit.

---

## Explicitly not doing

- **Slicing, or forking a slicer.** It would make Studio a worse Orca overnight.
- **A second printer dashboard.** Fluidd already ships on the machine.
- **A browser extension.** The nearest competitor's coupling to one site's DOM
  broke it in three of its last four releases. Any local file is a better input.
- **Requiring Extended Firmware.** Most owners run stock, and its presence cannot
  be reliably detected anyway.
- **LLM features.** Everything Studio does is deterministic and explainable. An
  "AI" button would weaken the one property that makes it trustworthy.
- **Chasing feature count.** The Fund's criteria reward depth over breadth, and a
  polished capability beats six unfinished ones.

---

## If only one thing gets done

Record the video. The engineering argument is now made and testable; what is
missing is that nobody has watched it work.
