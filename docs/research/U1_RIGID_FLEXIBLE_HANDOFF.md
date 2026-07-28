# U1 Rigid–Flexible Research — Handoff

**Branch:** `research/u1-rigid-flexible-tutorial` · **Head:** `86ec35c` · **Written:** 2026-07-28
**State:** documentation complete, evidence re-verified, **no physical tests run, nothing published, nothing pushed or merged.**

---

## 1. What this work is

Preparation for Snapmaker's U1 rigid-flexible / flexible-material tutorial co-creation
programme. Three deliverables plus a product proposal, all research-and-protocol only.

**It deliberately contains no proven settings.** The value is that every statement is
separated into *officially verified* / *community-reported* / *inferred and untested*, and
that the untested parts have a runnable protocol attached.

**Non-negotiables carried from the project's own rules:** Snapmaker Orca slices, Studio never
does. Studio never claims to validate physical bonding or print success. No invented values.

---

## 2. The four documents

| File | What it is | Status |
|---|---|---|
| [`docs/research/U1_RIGID_FLEXIBLE_RESEARCH.md`](U1_RIGID_FLEXIBLE_RESEARCH.md) | Evidence base. Every finding tagged **O** / **C** / **T** with source + retrieval date. Contains the transcribed adhesion table (§3.1.5) and the DFC conflict resolution (§4.5). | Complete; 2 rows outstanding (§8.2) |
| [`docs/testing/U1_RIGID_FLEXIBLE_TEST_MATRIX.md`](../testing/U1_RIGID_FLEXIBLE_TEST_MATRIX.md) | Eight controlled prints, four pairs. Pre-conditions, one-factor rule, safety stops, evidence requirements, T8 pre-registration gate. | Complete; blocked on 3 Orca reads |
| [`docs/tutorials/U1_RIGID_FLEXIBLE_TOPIC_FRAMEWORK.md`](../tutorials/U1_RIGID_FLEXIBLE_TOPIC_FRAMEWORK.md) | Proposed article structure, seven core ideas, positioning, rejection risks. | Complete |
| [`docs/product/FLEXIBLE_MATERIAL_DOCTOR_PROPOSAL.md`](../product/FLEXIBLE_MATERIAL_DOCTOR_PROPOSAL.md) | Whether a Flexible Material Doctor can exist without becoming a slicer. Inputs, tiered rules, wording, architecture, tests, non-goals. | Complete; **not implemented, deliberately** |

Prior art this builds on: [`U1_PRINT_PROFILE_RESEARCH.md`](U1_PRINT_PROFILE_RESEARCH.md)
(prime/wipe tower).

---

## 3. Evidence discipline — read before editing anything

- **O** = officially verified (Snapmaker docs, wiki, support centre, product page).
- **C** = community-reported (forums, vendor blogs, third-party, adjacent ecosystems).
- **T** = inferred / requires physical testing.

**A C finding never becomes an O setting.** It becomes a T hypothesis, and only recorded
physical evidence moves it.

**Conflict rule (research §1.2):** material-specific beats generic · newer beats older ·
documentation beats marketing/blog · **both are always written down, never silently merged.**

---

## 4. The three things most likely to be got wrong by the next person

### 4.1 Dynamic Flow Calibration
Snapmaker's generic guidance says run it after a filament change. Its **TPU-specific guide
says turn it off** — TPU is soft and compressible, which makes the calibration unreliable.
**Any job with TPU → DFC off. No TPU → generic guidance stands.** Never restate one as the
other. All eight tests hold it **constant OFF** (matrix P3), evidenced by screenshot (E9).

### 4.2 ABS/ASA + TPU
They **are** officially classified — both **Bondable (–)**. Do not write that they lack a
classification. They are out of scope because there is no published combined recipe, and
because Snapmaker states high-temperature filaments **cannot be printed at the same time**
as TPU (the top cover's two circulation modes are mutually exclusive).

### 4.3 Withdrawn claim — do not resurrect
An earlier draft said Snapmaker prohibits flame/thermal burnout on the U1's interference-fit
hot end. **That could not be found on the U1 pages and is retracted** (research §4.8.2).
Avoiding torch methods is recorded as *our* protocol choice, not a Snapmaker quote.

---

## 5. Where the physical work is blocked

Nothing can be printed until these are read out of Snapmaker Orca and written down verbatim.
**Read-only — change nothing, save nothing.**

| # | Read | Blocks |
|---|---|---|
| 1 | Toolchange retraction length, **Snapmaker TPU 95A HF** and **TPU 90A** profiles → *Setting Overrides*. Record the exact installed Orca version alongside. | T7/T8 **and** Step 1 of the T8 pre-registration gate |
| 2 | Beam Interlocking defaults: beam width, direction, beam layers, depth (cells), boundary avoidance (cells). | T2, T4 |
| 3 | Does this build apply support-**interface** material to supports growing from the model, or only plate-touching ones? | T5, T6 (they are invalid if it is plate-only and the model has model-borne supports) |

Also outstanding, documentation-side: **re-open the Snapmaker U1 specs page** to date research
rows 2.2 and 2.4 — the only two rows not read live on 2026-07-28.

**Gate before any print:** matrix §0 pre-conditions P1–P10. Orca must be **2.3.4 or later**
(TPU profiles require it — *not* a DFC requirement). Record the installed version, don't
assert "latest".

---

## 6. Experimental-design decisions already made — don't quietly undo them

- **One-factor-at-a-time**, where a factor may be a *named, pre-registered, inseparable
  bundle*. Bundles are legal only if named before the run, applied whole, and reported as a
  bundle.
- **T5/T6 is a bundle comparison** (Orca support defaults vs the published PLA/PETG recipe
  extrapolated whole to a TPU interface). It can evaluate the bundle only — **never**
  attribute an outcome to Top Z distance, interface layers, pattern, spacing, or base
  pattern individually.
- **T8's value is pre-registered and frozen before T7 is sliced.** If the two shipped TPU
  values differ, use one reduction *rule* (a single policy-level factor) or split into
  T8a/T8b. Never report two different numeric changes as one measurement.
- **T7/T8 interpretation is fixed in advance:** if T7 records zero toolchange incidents, T8
  **cannot** claim improved reliability — only adverse effect or neutrality. Clean + clean is
  not proof the lower value is better.
- **T7 predicts nothing about the 95A↔90A bond.** No official interfacial-strength statement
  exists between TPU grades.

---

## 7. Decisions the maintainer still owns

1. **Apply before or after running the eight prints?** Recommendation in the framework: apply
   now with research + protocol, state the prints are ready to run.
2. **The T8 experimental value or reduction rule** — must be chosen deliberately, on paper,
   after item 5.1 is read. **Not** during a print session, and not by an agent.
3. **Coupon geometry** — must be our own or clearly licensed; one shared coupon spans
   T1–T4 and T7–T8. No private/copyrighted model names in any evidence.
4. **Raising the two documentation-signposting items with Snapmaker** (generic vs TPU-specific
   DFC; product-page settings vs blog examples). Framed as "a pointer between your own pages
   would help readers" — never as error reports.
5. **Whether the Flexible Material Doctor gets built at all.** The proposal is staged behind
   gates; Phase 1 needs nothing from the prints, Phase 3 needs all of them.

---

## 8. Hard rules for whoever picks this up

- Documentation-only until the maintainer says otherwise. **No product implementation.**
- **No invented settings or material-pair classifications.** Absent = say absent.
- **No push, no merge, no external publication** without explicit authorisation.
- Snapmaker Orca remains the slicer; Studio never claims to predict physical success.
- Preserve evidence levels and source dates on every edit.
- Anonymise all evidence: no real IPs, hostnames, local paths, usernames, serials, or
  private model names.
- Prints are **supervised** — first 15 minutes continuously, then every 30 minutes. Safety
  stops S1–S8 are in the matrix; aborting is a correct outcome, and a supervised abort is data.

---

## 9. Commit history on this branch

| SHA | What |
|---|---|
| `11fb8b9` | Initial four documents — research, matrix, framework, proposal |
| `2e86715` | Corrective pass: DFC TPU rule, adhesion table transcribed, PLA/TPU support evidence, T8 pre-registration, flame claim withdrawn |
| `86ec35c` | Consistency + experimental-design cleanup: Orca version gate, ABS/ASA reasons, T1/T5/T6/T7/T8 design, Doctor F5 split, verification flags reconciled |

**Test baseline, unchanged across all three:** backend `345 passed, 3 skipped` (`py -3.13 -m pytest -q`,
run from `backend/`) · desktop `161 passed, 25 files` (`npm run test`, run from `desktop/`).

> Environment note: `python` is not on PATH on this machine and the default `py` (3.14) lacks
> the project's dependencies. Use **`py -3.13`**.

---

## 10. Suggested next prompt

```
On branch research/u1-rigid-flexible-tutorial (commit 86ec35c), clear the Orca-dependent
items in U1_RIGID_FLEXIBLE_RESEARCH.md §8.2. Open Snapmaker Orca READ-ONLY — change and save
nothing — and transcribe verbatim: (1) toolchange retraction length in the Snapmaker TPU 95A
HF and TPU 90A filament profiles under Setting Overrides, with the exact installed Orca
version; (2) shipped Beam Interlocking defaults (beam width, direction, beam layers, depth in
cells, boundary avoidance in cells); (3) whether support-interface material is applied to
supports growing from the model or only plate-touching ones. Record each with its retrieval
date, then fill Step 1 of the T8 pre-registration gate in the test matrix. Do NOT choose the
T8 experimental value — that is the maintainer's decision. Also re-open the Snapmaker U1 specs
page to clear research rows 2.2 and 2.4. Re-run py -3.13 -m pytest -q and npm run test. Report
each item, what changed, and the commit SHA. Do not push or merge.
```
