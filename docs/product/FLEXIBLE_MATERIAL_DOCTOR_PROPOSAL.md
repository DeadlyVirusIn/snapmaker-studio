# Flexible Material Doctor — proposal (not implemented)

> **Proposal only. Nothing in this document is built, and nothing in this phase changes
> conversion or validation behaviour.** This is the "can we, and should we, without becoming
> a slicer?" review requested by the research phase.
>
> Evidence base: [`U1_RIGID_FLEXIBLE_RESEARCH.md`](../research/U1_RIGID_FLEXIBLE_RESEARCH.md).
> Physical evidence needed: [`U1_RIGID_FLEXIBLE_TEST_MATRIX.md`](../testing/U1_RIGID_FLEXIBLE_TEST_MATRIX.md).

---

## 1. The question

Studio's Doctors answer *"what will bite me, and why?"* before Orca slices. A design that
mixes a rigid and a flexible material carries risks Studio is currently blind to — it counts
colours, not materials. Can it answer flexible-material questions **without** modelling flow,
adhesion physics, or slicing?

**Answer: yes, but only for a narrow, honest set of questions**, and only if the boundary in
§6 is held absolutely.

---

## 2. Verdict up front

**Recommended: build it, scoped to preparation and procedure — not to settings.**

The valuable thing is not "what temperature should my TPU be" (Orca's profiles already
answer that, and Studio must not compete). It is:

> *"This project mixes a rigid and a flexible material. Here is what that changes about how
> you load, calibrate, support, and tower it — and here is which of that is documented by
> Snapmaker versus reported by users."*

That is a **read-only explanation layer over facts Studio can already see in the file**, plus
officially-sourced procedure. It requires no new physics and no slicing.

**Blocking condition:** anything derived from the test matrix (interlocking guidance,
retraction guidance, support-interface guidance) ships **only after** the corresponding test
has physical evidence. Until then the Doctor states the open question, not an answer.

---

## 3. Inputs — all already available

No new capability is required for the MVP.

| Input | Source in the existing codebase | Available today? |
|---|---|---|
| `filament_type` per slot (`["PLA","TPU",…]`) | `canonical.py`, `intelligence.py`, `source_compatibility.py` | **Yes** |
| Filament / colour count | `fingerprint.py`, `mm_doctor.py` | **Yes** |
| Real toolhead count when a printer is connected | `moonraker.py` → `toolhead_fit.py` | **Yes** |
| Painted regions present | `fingerprint.py` (`painted_triangles`) | **Yes** |
| Per-filament array / purge consistency | `doctor.py::_filament_inconsistencies`, `filaments.py` | **Yes** |
| Model height / footprint / tip risk | `mesh_diagnostics.py` | **Yes** |
| Multi-material tower clearance on the plate | `bed_fit.py` (`multi_material=True`) | **Yes** |
| Support-interface filament assignment | — | **No** — would need reading the support keys from `project_settings.config`. Read-only, mechanical, no new physics. Phase 2. |
| Beam Interlocking on/off + parameters | — | **No** — same: read the keys if present. Phase 2. |
| Shore hardness | — | **Not derivable.** `filament_type` says "TPU", not "95A". Must be asked or left unknown. **Never guessed.** |
| Drying state | — | **Not derivable.** User-stated or unknown. |

> The Shore-hardness gap is the sharpest honesty constraint. Snapmaker's official line is
> that the U1 is compatible with **TPU ≥ 90A**, with softer grades under validation
> (Research §2.5). Studio cannot tell 95A from 85A from a project file. It must therefore
> **ask or stay silent** — never assume the supported case.

---

## 4. Rules — what it would actually say

Each rule below is tagged with the evidence level it inherits. **A rule may not ship above
the evidence level of its source.**

### Tier A — ships on today's evidence (officially sourced, no test required)

| ID | Trigger | Output | Evidence |
|---|---|---|---|
| **F1** | Any filament slot has type `TPU` (or a known flexible type). | "This project uses a flexible filament. On the U1, flexible filament is loaded **and unloaded manually**, with Auto Loading turned off for that toolhead. Trim the end at about 45°." + link | **O** — Research §4.2 |
| **F2** | Flexible present. | "Snapmaker documents drying TPU before use — check your spool's own drying spec." | **O** — §4.1 |
| **F3** | Flexible present **and** hardness unknown. | "Snapmaker documents U1 compatibility for TPU **90A and harder**; softer grades are still under validation. Studio can't read hardness from the file — check your spool." | **O** — §2.5 |
| **F4** | ≥ 2 distinct filament **types** in the project (any mix). | "This is a multi-**material** print, not just multi-colour. Different materials bond differently — and if they bond poorly, the **prime tower** can delaminate at the material boundary before the part does." + link to the U1 prime-tower guide | **O** — §4.6.3 |
| **F5** | Flexible + rigid mix present. | "Snapmaker Orca has **Beam Interlocking** for rigid–flexible combinations, which mechanically stitches the two materials at the boundary. It's a slicer setting — turn it on in Orca if you need the join to hold." | **O** — §4.7.1 |
| **F6** | Any multi-material project. | "Run **Dynamic Flow Calibration** after every filament change, and re-run multi-toolhead offset calibration if you've moved the printer or changed a toolhead or hot end." | **O** — §4.5.3, §4.9.2 |
| **F7** | Flexible present + existing tower-clearance warning from `bed_fit`. | Escalate the existing tower message: material mismatch adds a second, independent tower failure mode on top of the geometric one. | **O** — §4.6.3 + existing code |

### Tier B — states the open question only (no answer until the matrix runs)

| ID | Trigger | Output | Blocked on |
|---|---|---|---|
| **F8** | Rigid + flexible mix. | "Whether Beam Interlocking meaningfully strengthens *this* pair isn't published — Snapmaker recommends it for weak-adhesion combinations. Studio doesn't have measured values." | T1–T4 |
| **F9** | Flexible present, ≥ 2 toolheads in use. | "Filament handling during toolchanges is the most commonly reported problem with flexibles on toolchangers. Studio doesn't recommend a retraction value — check your Orca profile." | T7–T8 |
| **F10** | Support interface uses a different material from the part *(needs the Phase-2 input)*. | "Snapmaker publishes a dissimilar-material support recipe for **PLA and PETG**. Whether it transfers to a TPU interface hasn't been established." | T5–T6 |

### Tier C — never ships without physical evidence

Specific interlocking depth values · specific retraction-at-toolchange values · specific
support-interface Z-distance/spacing for TPU · any per-pair "this will hold" statement ·
any sub-90A TPU guidance · any ABS/ASA + TPU guidance.

### Rule the Doctor must enforce on itself

Every finding renders with its evidence level visible: **Documented by Snapmaker** /
**Reported by users** / **Not established**. Same discipline as the research doc, in the UI.

---

## 5. Output wording

Follows the existing Doctor contract (`{level, text}` findings + `fixes`, levels
`ok` / `warn` / `risk`, plain language, no raw setting keys in Simple Mode).

**Wording rules:**
- Never "this will print" / "this will hold" / "safe to print". *(Already guarded by
  `backend/tests/test_public_claims.py`.)*
- Never imperative on a slicer value Studio hasn't verified. Say *"check this in Orca"*, not
  *"set this to X"*.
- Always name the actor: *"Snapmaker documents…"* / *"Users report…"* / *"This hasn't been
  established."*
- Prefer explaining the **mechanism** over issuing an instruction — the tower-as-canary
  framing (F4) teaches; "increase brim" does not.
- Never imply Studio checked the physical outcome. It read a file.

**Example (Tier A, `warn`):**

> **Flexible + rigid materials in one project**
> This project mixes PLA and TPU. On the U1, flexible filament is loaded **and unloaded
> manually** — turn Auto Loading off for that toolhead and trim the filament at about 45°.
> Because the two materials bond weakly, watch the **prime tower**: Snapmaker documents that
> poorly-bonding material pairs can delaminate at the tower's material boundary.
> *Documented by Snapmaker · Studio doesn't check the physical bond.*

---

## 6. Architecture — and the line that must not be crossed

### Where it lives

```
backend/snapstudio_core/flexible_doctor.py     # new: pure, read-only, no I/O
backend/snapstudio_core/data/
    flexible_materials.json                    # new: flexible type list + evidence-tagged rule copy
backend/snapstudio_api/service.py              # wire: pass filament types into the assessment
backend/snapstudio_core/intelligence_report.py # wire: one more section, same pattern as Multi-Material
desktop/src/…                                  # surface inside the existing Multi-Material surface
```

Mirrors `mm_doctor.py` exactly: a pure `assess(...)` function taking plain values, returning
`{schema_version, available, overall_level, overall_text, findings, fixes}`. No file I/O, no
network, no mutation. Slots into `intelligence_report.py` beside the existing Doctors.

### Surface

**Extend the Multi-Material Doctor, do not add a new Doctor.** The repo's own UX reviews
already flag "Doctor" proliferation and dead-end surfaces as a novice problem
(`docs/NOVICE_UX_RED_TEAM.md`, `docs/internal/FABEL_DEVIL_ADVOCATE_REVIEW.md`). "Will my
colours print right?" and "will my materials work together?" are the same user moment.
Internally it is `flexible_doctor.py`; to the user it is the Multi-Material Doctor getting
smarter.

### The line — what makes this not a slicer

| Studio does | Studio must never do |
|---|---|
| Read `filament_type` from the project file | Compute flow, pressure advance, or purge volumes |
| Name a documented Snapmaker procedure | Emit a temperature, speed, or retraction value as a recommendation |
| Say Beam Interlocking exists and what it is for | Choose interlocking depth or generate interlocking geometry |
| Say the tower can delaminate on poor-adhesion pairs | Modify tower geometry or generate G-code |
| Say the support-interface recipe is published for PLA/PETG | Assign support materials or rewrite the support block |
| Warn that hardness is unknown | Infer hardness from anything |
| Ask the user, and stay silent if unanswered | Assume the supported case |

Additionally, and unchanged from existing rules: never modify the original file; never
auto-enable `wipe_tower_no_sparse_layers`; never auto-raise `wipe_tower_max_purge_speed`
above 90 mm/s; never touch `filament_colour` / `filament_type` / `filament_settings_id`.

---

## 7. Tests required before it could ship

| Test | Asserts |
|---|---|
| `test_flexible_doctor.py::test_no_flexible_is_unavailable` | No TPU → `available` False or a single `ok` finding; never a scary warning on an all-rigid project. |
| `…::test_flexible_triggers_manual_loading_finding` | TPU present → F1 fires with manual-load wording. |
| `…::test_hardness_never_assumed` | Output never contains "95A"/"90A"/"supported hardness" unless the user supplied it. |
| `…::test_no_numeric_settings_emitted` | Findings/fixes contain **no** temperature, speed, retraction, or interlocking-depth numbers. Regex guard — this is the anti-slicer test. |
| `…::test_evidence_level_present_on_every_finding` | Every finding carries a source tag. |
| `…::test_tier_b_states_question_not_answer` | Tier-B findings contain "hasn't been established"-class wording and no directive. |
| `…::test_pure_and_read_only` | `assess()` does not mutate its inputs. |
| `test_public_claims.py` (extend) | New copy contains no print-success guarantee and no "will hold"/"safe to print". |
| `test_intelligence_report.py` (extend) | The new section appears in availability/status without disturbing existing Doctors. |

**Plus the existing suites must stay green** — the whole point is that this is additive.

---

## 8. Non-goals

1. **Not a slicer.** No G-code, no toolpaths, no flow model, no adhesion physics.
2. **Not a settings recommender for materials.** Orca's material profiles own that.
3. **No printer control.** Printer Hub remains the only local, user-confirmed control surface.
4. **No prediction of physical success.** Structural and metadata validation says nothing
   about whether a bond holds — this proposal must not blur that.
5. **No hardness inference. No drying inference. No brand inference.**
6. **No sub-90A TPU support**, while Snapmaker lists it as under validation.
7. **No ABS/ASA + TPU guidance**, with no official pairing source.
8. **No auto-fix.** Read-only advisory only; the user acts in Orca.
9. **No new top-level Doctor** in the navigation.
10. **Nothing built in this phase.**

---

## 9. Staging

| Phase | Content | Gate |
|---|---|---|
| **0 — now** | This proposal. Nothing built. | — |
| **1** | Tier A rules (F1–F7) on today's inputs, inside the Multi-Material surface, with evidence tags in the UI. | Research §8 verification debt cleared (official pages re-read on the live URLs). |
| **2** | Read support-interface and Beam-Interlocking keys from the project settings; Tier B open-question findings (F8–F10) become file-aware. | Phase 1 shipped and reviewed. |
| **3** | Any Tier-C content — **only** for questions the eight-print matrix actually answered, published with its limitations attached. | Matrix run, evidence recorded, results reviewed. |

**No phase skips its gate.** In particular, Phase 3 cannot begin from community reports
alone — that is the exact failure mode this whole research phase exists to prevent.
