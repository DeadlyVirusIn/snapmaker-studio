# U1 Rigid–Flexible Tutorial — Topic Framework

> **Planning document for a tutorial co-creation application.** No article is written here,
> and no settings are proposed. Everything below routes back to
> [`U1_RIGID_FLEXIBLE_RESEARCH.md`](../research/U1_RIGID_FLEXIBLE_RESEARCH.md) for evidence
> and [`U1_RIGID_FLEXIBLE_TEST_MATRIX.md`](../testing/U1_RIGID_FLEXIBLE_TEST_MATRIX.md) for
> the physical evidence that does not exist yet.
>
> **Snapmaker Orca is the slicer throughout.** Snapmaker Studio's role in any article is
> read-only inspection and U1 profile preparation — never slicing, never printer control.

---

## 1. What this article can honestly be

**It cannot be** "the definitive rigid-flexible settings guide". We have no physical
evidence yet, and inventing settings is forbidden.

**It can be** the thing the U1 community currently lacks most: **a guide that separates what
Snapmaker has actually documented from what the internet repeats**, teaches the official
procedures that novices skip, and shows a reproducible way to test the rest on your own
machine.

That framing is honest today, is useful today, and improves — rather than collapses — once
the eight test prints are run.

### The one-sentence promise

> *Rigid-flexible printing on the U1 fails for a small number of specific, documented
> reasons — and most of them happen before the first layer.*

---

## 2. The five ideas the article is actually built on

Each is sourced. Each is the kind of thing a reader remembers.

| # | Idea | Why it earns its place | Evidence |
|---|---|---|---|
| **1** | **Flexible filament on the U1 is a manual load and a manual unload — per toolhead, with Auto Loading switched off.** | This is officially documented and routinely missed. It is the archetypal first TPU failure, and it costs nothing to get right. | Research §4.2 — **O** |
| **2** | **Weak adhesion is a defect when you want a join and a feature when you want a support.** | Reframes the whole topic. Explains why Snapmaker both discourages mixing dissimilar materials *and* publishes a dissimilar-material support recipe. Turns confusion into a decision rule. | Research §3.1.2–3.1.4 — **O**, with the synthesis flagged as our reading |
| **3** | **Beam Interlocking is the answer to weak adhesion — but it is a tool with a job, not a switch you leave on.** | Officially named for rigid-flexible combinations; upstream docs warn that too little depth gives poor adhesion. Whether it helps an already-strong pair is genuinely open. | Research §4.7 — **O** for existence and parameters, **T** for values |
| **4** | **The prime tower is a miniature of your part's interface — if the materials do not bond, the tower delaminates first.** | Officially documented failure mode, and it converts "my tower collapsed" from bad luck into a material-choice consequence the reader can predict. | Research §4.6.3 — **O** |
| **5** | **Snapmaker's own TPU speed and drying figures differ between its product page and its blog — follow the documentation.** | Nobody has written this down. It is immediately actionable, demonstrably true from two Snapmaker URLs, and it models the honesty the whole piece is built on. | Research §4.1 — **O** vs **C** conflict |

---

## 3. Proposed article structure

Working title: **"Rigid + Flexible on the Snapmaker U1: what's documented, what's folklore,
and how to test the difference."**

### Part 0 — Frame (short)
What rigid-flexible printing is on a 4-toolhead machine, why it is different from an MMU,
and what this article will and will not tell you. State the limitation up front: *no
guaranteed settings, because the evidence for them does not exist publicly.*

### Part 1 — Before the first layer (the highest-value section)
1. **Manual load, manual unload, Auto Loading off** — the official per-toolhead procedure,
   the 45° cut and why Snapmaker justifies it as reducing feeding resistance, unplugging the
   tube at the toolhead to seat the filament against the gears. *(Research §4.2)*
2. **Drying** — TPU is "extremely hygroscopic and must be dried before use"; use your
   spool's own spec, and here is where the Snapmaker figures disagree with each other.
   *(Research §4.1)*
3. **Calibration is a prerequisite, not a maintenance task** — offset calibration after any
   machine move/toolhead/hot-end change; Dynamic Flow Calibration after every filament
   change; both automatic, both cheap; and note the 0.2 mm nozzle exception. *(Research
   §4.5, §4.9)*
4. **A misaligned seam on a soft material looks like bad adhesion.** *(Research §4.9.6 —
   flagged as our hypothesis, not fact.)*

### Part 2 — Choosing the pair
1. Snapmaker's adhesion framing: some pairs bond, some do not. *(§3.1)*
2. **The reframe:** weak adhesion → supports (zero Z-distance); strong adhesion or
   interlocking → structure. *(§3.1.2)*
3. What is documented per pair — PETG+TPU described as strongly bonding; TPU 90A stated to
   co-print with PLA, PETG, PA, PET, TPU 95A. *(§3.2, §3.3, §3.6)*
4. **What is not documented, said plainly:** ABS/ASA + TPU has no official pairing guidance
   and an unresolved thermal conflict; TPU under 90A is officially still under validation.
   We are not covering either. *(§3.4, §2.5)*

### Part 3 — Making the join hold
1. Beam Interlocking: what it does, the five parameters, why depth matters. *(§4.7)*
2. **Honest gap:** no published values for TPU pairs. Use the shipped defaults, record what
   they are, and change one at a time.
3. The tower as the interface's canary. *(§4.6.3)*
4. The tower rules that are not negotiable: Rib wall, keep it square, brim, ≤ 90 mm/s, and
   never enable skip-empty-tower-layers automatically. *(§4.6.1, §4.6.5)*

### Part 4 — Using weak adhesion on purpose (supports)
1. Snapmaker's published dissimilar-material support recipe, quoted with its actual numbers
   and clearly labelled as published for **PLA/PETG**. *(§3.5.2)*
2. The base-vs-interface split and why bed temperature drives it. *(§3.5.1)*
3. Community-reported: PLA supports release cleanly from TPU; TPU-on-TPU can fuse. *(§3.5.4
   — labelled as a vendor report.)*
4. **Version watch:** a reported Orca behaviour where interface material is applied only to
   plate-touching supports — check it on your build before blaming your settings. *(§3.5.6)*

### Part 5 — When it goes wrong
1. Toolchange jams and gear bird-nesting; the retraction-at-switch discussion **presented as
   an open question with a vendor recommendation, not as a setting**. *(§4.4)*
2. Clogs: the **official** U1 procedure — 10–20 °C above normal print temp, supplied needle,
   repeat until extrusion is straight. **And the prohibition: no flame, because the U1's
   integrated hot end is an interference fit.** *(§4.8)*
3. Tower collapse and delamination. *(§4.6)*
4. Multi-colour misalignment → the calibration checklist. *(§4.9)*

### Part 6 — Test it yourself (the differentiator)
A condensed, reader-runnable version of the eight-print matrix: paired prints, one variable,
what to record, what to photograph, when to stop. This is the section nobody else is
publishing, and it is what makes the article durable rather than a settings dump that ages
out with the next Orca release.

### Part 7 — Where Snapmaker Studio fits (short, honest, non-promotional)
Studio reads the model and the project file before Orca does: colours vs toolheads, filament
metadata consistency, plate fit with tower clearance, and a prime/wipe-tower strategy
recommendation. **It does not slice, does not control the printer, and today knows nothing
about material compatibility** — that gap is exactly what the research phase set out to
define. One paragraph. No product pitch.

---

## 4. Evidence labelling in the published article

The article carries the same discipline as the research doc, visible to the reader:

- **Documented by Snapmaker** — with the link.
- **Reported by the community** — with what kind of source (forum post / vendor blog /
  third-party review) and a note that it is unverified.
- **Untested** — stated as an open question, with the test that would settle it.

Readers should be able to tell, at a glance, which sentences they can act on and which are
someone's experience. That labelling *is* the product.

---

## 5. Application positioning (recommended)

**Position as: research + protocol contributor, not settings authority.**

What we bring that is real today:
1. A **sourced, evidence-levelled research base** across every topic in scope, including
   explicitly documented gaps and two internal contradictions in Snapmaker's own material
   (TPU speeds/drying; "don't mix PLA and PETG" vs the published PLA/PETG support guide).
2. A **rigorous eight-print physical test protocol** with pre-conditions, one-variable-at-a-
   time discipline, safety stop conditions, and evidence requirements — reusable by
   Snapmaker and by the community for pairs beyond the eight.
3. **A software product that already ships** and reads real U1 project files — with an
   honest inventory of what it can and cannot claim.
4. **Demonstrated willingness to say "we do not know"**, which is the scarce quality in this
   content category.

What we explicitly do **not** claim:
- No proven settings. No bond-strength numbers. No print-success guarantees.
- No sub-90A TPU coverage. No ABS/ASA + TPU coverage.
- No suggestion that Studio validates or predicts physical print success.

**Suggested framing sentence for the application:** *"We have built the research base and the
test protocol; we would like to run the prints and publish the results with the evidence
levels intact."*

---

## 6. Risks of rejection or overclaiming

| Risk | Likelihood | Mitigation |
|---|---|---|
| **Reviewer wants finished settings, not a protocol.** | Medium–high | Lead with the two officially-sourced findings that are immediately useful (manual load/unload; documentation-vs-blog conflict). Show the protocol produces settings on a known timeline, and that unevidenced settings would be worse than none. |
| **We are seen as correcting Snapmaker publicly** (the speed/drying conflict, the PLA/PETG tension). | Medium | Frame as *reconciling* two Snapmaker surfaces for readers, not as an error report. Raise both privately in the application before publishing. Never adversarial. |
| **A community anecdote gets published as a setting** (especially the 0–4 mm retraction figure). | Medium | The C→O rule is enforced in the research doc, the matrix, and the article's visible labelling. The retraction figure stays a vendor recommendation until a test moves it. |
| **Overclaiming Studio's capability** — implying it validates material compatibility or predicts success. | Medium | §5.2 of the research doc lists the absent capabilities explicitly. Part 7 of the article is one paragraph and states the gap. A repo guard test already blocks print-success guarantees in public copy. |
| **Sub-90A TPU or ABS/ASA+TPU content is expected.** | Low–medium | Both are declared out of scope with the official reason. Offer them as a separately-resourced later phase (enclosure required for ABS/ASA). |
| **Physical results are unflattering** (e.g. interlocking does little; a tower collapses). | Medium | Negative results are published with the same weight as positive ones — that is stated in the application up front so it is not a surprise later. |
| **Orca version drift invalidates content.** | Medium | Every published setting carries the Orca version it was recorded on; Part 6 teaches readers to re-check rather than trust. |
| **Verification debt leaks into publication** (§8 of the research doc — official pages read via search extraction, not fetched directly). | **High if ignored** | **Blocking gate:** every ⚠ re-verify item is re-read on the live page and dated before anything is published or submitted. |

---

## 7. Open decisions for the maintainer

1. **Do we run the eight prints before or after applying?** Recommendation: apply with the
   research + protocol, and state that the prints are ready to run. Running first delays the
   application; applying with nothing but an idea is weaker than applying with this.
2. **Do we raise the two Snapmaker internal conflicts in the application?** Recommendation:
   yes, privately and neutrally — it demonstrates the research is real.
3. **Is a top cover available?** If yes, ABS/ASA + TPU becomes a possible phase 2. If no,
   it stays out and we say so.
4. **Which model geometry for the coupons?** Must be our own or clearly licensed; the matrix
   depends on one shared coupon across T1–T4 and T7–T8.
