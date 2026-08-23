# Next moves — what would make Studio elite

Updated **2026-08-23**, after the beta.24 release sprint. Phase 1 submissions
close **7 September 2026** — fifteen days from this update.

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
there are current screenshots, a recorded demo of the running application, and a
release verified against real hardware. What is still missing is people: one star,
no issues, and an unsigned installer.

---

## Done since the last update

| Was | Now |
|---|---|
| Record and publish the demo | Recorded from the installed beta.24 build — `docs/media/snapmaker-studio-demo.mp4`, 71 seconds, surfaced at the top of the README |
| Post the ecosystem notes | Four posted 2026-08-23; see [ECOSYSTEM_OUTREACH.md](ECOSYSTEM_OUTREACH.md) for the URLs. ImageMap skipped — issues disabled |
| Installed-build acceptance | `tools/acceptance/run.ps1` — 21 checks against the shipped installer, not a dev server |
| Real hardware verification | `tools/hardware/verify.ps1` — 13 read-only checks against a real U1; it found and fixed a genuine bug in how loaded filament was read |
| Release acceptance | beta.24 is the first build marked **ACCEPTED** with software, installed-application and hardware evidence all recorded |
| Code signing | Prepared to the last legal step — [CODE_SIGNING_POLICY.md](../CODE_SIGNING_POLICY.md) answers every SignPath eligibility criterion; only the form and MFA remain |
| Submission text | [INNOVATION_FUND.md](../INNOVATION_FUND.md) rewritten from the current product, against the fund's rules as re-read on 2026-08-23 |

---

## Tier 1 — before the deadline

### 1. Submit the entry
**P5 D0 J5 N0 T0 E5 R0 C5 · cx0 rr0**

Everything the form asks for is written in
[INNOVATION_FUND.md](../INNOVATION_FUND.md). The form itself asks for the
maintainer's name and email and represents them personally. Phase 1 closes
7 September 2026 and there is no published way to revise a submission afterwards,
so it is worth sending once and sending it late rather than early.

### 2. Share the project in a Snapmaker community channel
**P3 D1 J4 N2 T0 E4 R0 C4 · cx1 rr0**

This is a stated entry requirement, separate from the form, and it is also the
only route to the 20% community component that does not involve asking for votes.

### 3. Apply to SignPath Foundation
**P4 D1 J3 N5 T1 E1 R1 C2 · cx1 rr0**

Free for qualifying open-source projects; the earlier plan to fund an EV
certificate was wrong, because EV no longer bypasses SmartScreen. The application
accepts terms on the maintainer's behalf, which is why it is not automated.

### 4. Get one real user report
**P5 D5 J5 N5 T0 E5 R0 C5 · cx2 rr0**

43 downloads and zero issues is the weakest part of the submission, and no amount
of engineering fixes it. The outreach notes are the first channel that exists; a
maintainer's correction would be the project's first external feedback of any
kind.

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
