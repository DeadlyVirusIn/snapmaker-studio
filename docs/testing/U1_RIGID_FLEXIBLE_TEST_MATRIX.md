# U1 Rigid–Flexible Physical Test Matrix

> **Protocol only — no results recorded yet.** This document defines eight controlled
> prints that convert the **T** (inferred / requires testing) findings in
> [`U1_RIGID_FLEXIBLE_RESEARCH.md`](../research/U1_RIGID_FLEXIBLE_RESEARCH.md) into
> recorded physical evidence.
>
> **Snapmaker Orca slices every one of these prints.** Snapmaker Studio is used only to
> inspect the model and prepare the U1 profile copy; it never slices and never controls
> the printer. Nothing in this matrix is a claim that any print will succeed — the whole
> point is that we do not yet know.

---

## 0. Before any test runs — pre-conditions

Every one of these must be recorded in §4's run header. If any is unknown, **do not start**;
an unrecorded pre-condition makes every result in that run uninterpretable.

| # | Pre-condition | Why | Source |
|---|---|---|---|
| P1 | Multi-toolhead offset calibration completed on this machine, in this position, since the last toolhead/hot-end change or machine move. Record the date. | Misalignment presents as bad adhesion on a soft material and would silently contaminate every bond result. | Research §4.9.2 |
| P2 | Hot-end copper plate ↔ calibration sensor gap within **0.1–0.4 mm**; pogo pins and steel balls cleaned and greased. | Official prerequisite for trustworthy offset calibration. | Research §4.9.3 |
| P3 | **Dynamic Flow Calibration run after every filament change**, for every toolhead in the job. Held constant across all eight tests — it is never a variable here. | Official instruction; keeping it constant stops it becoming a hidden variable. | Research §4.5.3 |
| P4 | Snapmaker Orca version recorded (**must be ≥ V2.3.1** for Dynamic Flow Calibration). | Version-specific slicer behaviour is a known confounder (support-interface bug, §3.5.6). | Research §4.5.2 |
| P5 | **The shipped retraction-at-toolchange value is read out of the Orca profile and written down verbatim, per filament.** No test changes it unless the test says so. | The widely-circulated "0–4 mm" figure is a vendor recommendation, not a verified default. | Research §4.4 |
| P6 | **The shipped Beam Interlocking defaults are read out of Orca and written down verbatim** (beam width, direction, beam layers, depth, boundary avoidance). | No published values exist for TPU pairs; we use defaults and record them rather than inventing a recipe. | Research §4.7.4 |
| P7 | Support-interface behaviour check: confirm on this Orca build whether the interface material is applied to supports **growing from the model**, not only plate-touching supports. | If it reproduces, T5/T6 are invalid unless all supports start on the plate. | Research §3.5.6 |
| P8 | No nozzle is shared between two different materials within the matrix. Toolhead↔material assignment is fixed at the start (§2) and never reassigned mid-matrix. | Prevents cross-material residue being mistaken for a bond result. | Research §4.8.4 |
| P9 | Every spool dried and logged per §3 **before** its first use in the matrix, and re-dried per §3 if it has been out of a dry container beyond the stated window. | TPU is "extremely hygroscopic and must be dried before use". | Research §4.1 |
| P10 | Ambient temperature and relative humidity recorded at the start of each run. | Cheap to record; expensive to reconstruct later. | — |

**Out of scope, deliberately:** ABS/ASA + TPU (no official pairing guidance; unresolved
thermal conflict; enclosure not assumed present) and TPU below 90A (officially still under
validation by Snapmaker). See Research §3.4 and §2.5.

---

## 1. The one-variable-at-a-time rule

This is the rule that makes the matrix worth running. It is not advisory.

1. **Tests are run in pairs.** Within a pair (T1/T2, T3/T4, T5/T6, T7/T8), **exactly one**
   thing differs. Everything else — model, orientation, plate position, layer height,
   temperatures, speeds, tower settings, toolhead assignment, spool, drying state — is
   byte-identical between the two.
2. **The differing variable is named in the test header** and is the only field allowed to
   differ in the two runs' recorded settings.
3. **If anything else changes** — a spool runs out, a hot end is swapped, Orca is updated,
   the machine is moved — the pair is **void**. Re-run **both** halves. Do not re-run only
   the second half against an older first half.
4. **No mid-print adjustments.** No live tuning of flow, temperature, or speed. A print that
   needed intervention is a **failed run**, recorded as such, not a rescued result.
5. **One change per iteration when following up.** If T2 fails and you want to try a deeper
   interlocking depth, that is a **new pair** (T2a/T2b) with the new value recorded, not an
   edit to T2.
6. **Failures are results.** A collapsed tower or a delaminated seam is recorded with the
   same rigour as a success. Nothing is quietly re-run until it looks good.
7. **Every recorded value is transcribed from the slicer/printer UI**, never remembered,
   never inferred, never copied from this document.

---

## 2. Fixed toolhead assignment for the whole matrix

Assigned once, at the start, and never changed (pre-condition P8). Toolhead numbering
follows the U1's four toolheads as shown in Orca / on the touchscreen.

| Toolhead | Material class | Used by |
|---|---|---|
| **T0** | Rigid A — PLA | T1, T2, T5, T6 |
| **T1** | Rigid B — PETG | T3, T4 |
| **T2** | Flexible A — TPU 95A | T1–T8 |
| **T3** | Flexible B — TPU 90A | T7, T8 |

> **Loading:** every TPU toolhead is loaded and unloaded **manually**, with **Auto Loading
> disabled for that toolhead** (Settings → Print Preferences → Auto Loading), filament end
> trimmed at ~45°, per the official procedure (Research §4.2). Record loading mode used and
> whether the load succeeded first time — that is itself data for the tutorial.

---

## 3. Filament and drying record (fill one per spool, before first use)

Copy this block per spool into the run log. **A spool with no completed record must not be
used in the matrix.**

```
SPOOL RECORD
  Spool ID (arbitrary, e.g. TPU95-01):
  Material / grade:                        (e.g. TPU 95A)
  Shore hardness as stated by manufacturer:
  Brand / product name:
  Colour:
  Nominal diameter:
  Purchase or open date:
  Storage between uses:                    (sealed + desiccant / dry box / open air)
  Dried?                                   yes / no
    Dryer temperature (°C):
    Dry duration (h):
    Method:                                (filament dryer / oven / dry box with heat)
    Dried on (date/time):
  Hours out of dry storage since drying:
  Re-dry trigger for this matrix:          >24 h out of dry storage → re-dry before use
  Printed from a dry box during the run?   yes / no
  Manufacturer's stated nozzle temp range:
  Manufacturer's stated bed temp range:
  Manufacturer's stated speed range:
  Manufacturer's stated drying spec:
  Notes (kinks, ovality, prior jams):
```

**Reference points, cited not prescribed** — Snapmaker's own TPU 90A page states drying at
**70 °C for 6 hours**, nozzle **210–240 °C**, bed **25–60 °C**, speed **30–50 mm/s**,
cooling fan **ON**, 0.2 mm nozzle **not recommended**, and manual load/unload only
(Research §4.1). A Snapmaker *blog* states ~55 °C for 4–6 h and far higher speeds; the
documented product-page figures win, and the discrepancy is itself recorded (Research §4.1).
**For each spool, follow that spool manufacturer's own spec and record it** — do not copy
Snapmaker's TPU 90A figures onto a third-party spool.

---

## 4. Per-run header (fill for every single run, all eight tests)

```
RUN HEADER
  Test ID:                                 (T1 … T8)
  Run number for this test:                (1, 2, … — re-runs get new numbers)
  Date / time started:
  Operator:
  Ambient temp (°C) / RH (%):
  Machine serial or local label:           (do not publish; anonymise in evidence)
  Top cover fitted?                        yes / no
  Snapmaker Orca version:
  Studio version used to inspect/prepare:
  Offset calibration last run (date):
  Copper-plate ↔ sensor gap checked?       yes / no    measured:
  Dynamic Flow Calibration run this session, per toolhead?   T0 / T1 / T2 / T3
  Spool IDs in use, per toolhead:          T0:  T1:  T2:  T3:
  Loading mode per TPU toolhead:           manual / auto   Auto Loading disabled? yes/no
  First-time load success per TPU toolhead: yes / no  (retries: )
  Pre-condition P1–P10 all met?            yes / no   (if no: STOP, do not run)
  THE ONE VARIABLE UNDER TEST:
  Result: PASS / FAIL / VOID               (VOID = protocol broken, see §1.3)
```

---

## 5. Common settings to record for every test

Transcribed from Orca, per filament where applicable. **Record, do not prescribe** — these
are captured so the result is reproducible and so a reader can see what was actually used.

**Process / global**
- Layer height, first-layer height
- Wall loops, top/bottom layers, infill density and pattern
- Print sequence, plate position of the specimen

**Per filament (each toolhead in the job)**
- Nozzle temperature (first layer and other layers), bed temperature
- Flow ratio / pressure advance state (and whether DFC set it)
- Max volumetric speed
- Retraction length, retraction speed, **retraction at toolchange / material-switch value**
- Cooling fan settings
- Filament type string as set in Orca (this is what Studio reads back)

**Multi-material**
- Filament ↔ toolhead mapping
- Flush/purge volumes matrix and multiplier
- Whether Beam Interlocking is **on or off**, and if on: beam width, direction, beam layers,
  **interlocking depth (cells)**, **boundary avoidance (cells)** — verbatim from Orca

**Tower settings (record for every test, all eight)**
- `wipe_tower_wall_type` (rectangle / cone / **rib**)
- `prime_tower_width`, tower X/Y position on the plate
- `prime_tower_brim_width`
- `wipe_tower_rib_width`, `wipe_tower_extra_rib_length`, `wipe_tower_fillet_wall`
- `prime_volume`, `flush_multiplier`
- `wipe_tower_max_purge_speed` — **must be ≤ 90 mm/s** (Research §4.6.5)
- `wipe_tower_no_sparse_layers` — **must be OFF for every test in this matrix**

> **Tower baseline for the whole matrix:** wall type **Rib**, `no_sparse_layers` **OFF**,
> max purge speed **≤ 90 mm/s**, tower kept square, brim at or above the Orca default.
> This mirrors Snapmaker's U1 prime-tower-collapse guidance and Studio's existing safety
> rails. The tower is **not** a variable in this matrix — but its outcome **is** a recorded
> result in every test, because a rigid/flexible tower is the same bonded interface as the
> part (Research §4.6.3).

---

## 6. Evidence required for every test

Minimum evidence set. A test with missing evidence is **incomplete**, not passed.

| # | Evidence | Notes |
|---|---|---|
| E1 | Photo: the specimen on the plate immediately after the print finishes, before removal. | Shows tower and part together. |
| E2 | Photo: the **prime/wipe tower**, full height, from two angles. | Tower outcome is a first-class result here. |
| E3 | Photo: the **material interface**, macro, before any load is applied. | Interface quality baseline. |
| E4 | Photo: the interface **after** the pass/fail action (peel, flex cycles, or support removal). | The actual outcome. |
| E5 | Photo or screenshot: **Orca settings pages** for process, each filament, and multi-material/interlocking. | Proves the recorded settings; anonymise file paths and usernames. |
| E6 | Screenshot: Studio's read-only report for the same file (Project Doctor + Multi-Material Doctor verdicts). | Establishes what Studio *did* and *did not* see — direct input to the Doctor proposal. |
| E7 | Written note of anything unusual during the run: audible clicks, toolchange hesitation, tower contact, stringing between tower and part. | Free-text, timestamped where possible. |
| E8 | If failed: photo of the failure mode itself (delaminated seam, collapsed tower, jammed filament in gears, torn support surface). | Failures are results. |

**Anonymisation (project hard rule):** no real IP addresses, hostnames, local file paths,
usernames, machine serials, or private/copyrighted model names in any published photo or
screenshot. Crop or blur before the image leaves the machine.

---

## 7. Safety stop conditions — abort the print immediately

Applies to all eight tests. **Aborting is the correct outcome; a supervised abort is data.**

| # | Stop if… | Then |
|---|---|---|
| S1 | The prime/wipe tower tips, detaches, or is dragged by the nozzle. | Abort. Photograph in place before clearing. Record as FAIL with the tower as cause. |
| S2 | Filament visibly bird-nests around the extruder gears, or a toolchange stalls/repeats. | Abort. Do **not** force-feed. Manual unload per the official procedure. Record as FAIL (loading/toolchange). |
| S3 | Extrusion stops or goes intermittent on any toolhead. | Abort. Follow the **official** unclog procedure: heat 10–20 °C above that filament's normal print temp and use the supplied needle. **Never apply a flame — prohibited on the U1's interference-fit hot end** (Research §4.8.2). |
| S4 | The part detaches from the plate or a layer shift is visible. | Abort. Record; do not resume. |
| S5 | Any smell of burning, smoke, unusual noise, or a component visibly out of position. | **Abort and power down at the switch.** Do not restart until inspected. Escalate before any further run. |
| S6 | A toolhead fails to park/pick up, or the machine reports a calibration/firmware error. | Abort. Re-run pre-conditions P1–P2 before any further test. Do not "just retry". |
| S7 | The run is unattended and any of S1–S6 cannot be observed. | **Do not run this matrix unattended.** Every run in this matrix is supervised for at least the first 15 minutes and checked at least every 30 minutes thereafter. |
| S8 | The one variable under test can no longer be held (spool ran out mid-pair, Orca auto-updated, machine moved). | Mark the run **VOID** and re-run **both** halves of the pair (§1.3). |

---

## 8. The eight controlled prints

Each test below states: hypothesis · model requirements · filaments & drying · toolheads ·
Orca settings to record (beyond §5) · tower settings · evidence · pass/fail · safety ·
one-variable rule.

---

### T1 — PLA + TPU 95A, **flat interface**

- **Hypothesis.** A flat (non-interlocked) PLA↔TPU 95A interface on the U1 produces a bond
  that separates under modest peel load, because PLA and TPU are reported not to form a
  permanent chemical bond (Research §3.2.3). This run establishes the **baseline** that T2
  is measured against. *We do not predict a specific force; we record what happens.*
- **Model requirements.** A two-material coupon: a flat rectangular plate, PLA on one side
  of a **planar vertical interface**, TPU 95A on the other, with a short unbonded tab at one
  end of each material to grip for peeling. Suggested envelope ~60 × 25 × 6 mm, interface
  area ~60 × 6 mm. Same STL/3MF used for T1–T4 so all four are comparable. Model must be our
  own or clearly-licensed geometry; no private/copyrighted model names in evidence.
  **All supports (if any) must start on the build plate** (pre-condition P7).
- **Filaments & drying.** PLA (rigid A) and TPU 95A (flexible A). Complete spool records per
  §3 for both. TPU dried per its manufacturer's spec; re-dried if >24 h out of dry storage.
- **Toolheads.** PLA → **T0**. TPU 95A → **T2**. TPU loaded **manually**, Auto Loading
  disabled on T2, 45° cut. Record first-time load success.
- **Orca settings to record.** All of §5. Specifically: **Beam Interlocking = OFF** (state
  this explicitly in the record, do not leave it implied); retraction-at-toolchange verbatim
  per filament; PLA and TPU temperatures; TPU max volumetric speed.
- **Tower settings.** Matrix baseline (§5): Rib wall, no-sparse-layers OFF, purge speed
  ≤ 90 mm/s, square tower, brim ≥ Orca default. Record all values. Note tower position
  relative to the part.
- **Evidence.** E1–E8. Additionally: macro photo of the interface **before** peel (E3) and
  the separated or intact interface **after** peel (E4).
- **Pass / fail.**
  - **Records-complete (the real gate):** PASS only if the print completed without S1–S6,
    every §5 setting was transcribed, and E1–E7 exist.
  - **Bond observation (recorded, not pass/fail):** apply a slow manual peel at the tab.
    Record which of: *separated cleanly at the interface* / *separated with material transfer*
    / *TPU tore before the interface gave* / *did not separate under hand load*. Photograph.
  - **Automatic FAIL:** tower collapse (S1), toolchange jam (S2), or any mid-print
    intervention.
- **Safety.** S1–S8. Supervise the first toolchange specifically — it is the highest-risk
  moment for the TPU toolhead.
- **One-variable rule.** T1 and T2 differ **only** in Beam Interlocking OFF→ON. Identical
  model, orientation, plate position, spools, temperatures, speeds, tower settings,
  toolhead assignment. If any of those changes, both are VOID.

---

### T2 — PLA + TPU 95A, **Beam Interlocking**

- **Hypothesis.** Enabling Beam Interlocking at the **shipped Orca defaults** measurably
  changes the PLA↔TPU 95A interface outcome versus T1 — Snapmaker states the feature
  "significantly strengthen[s]" weak interfacial bonds and names rigid–flexible combinations
  explicitly (Research §4.7.1). **We do not assume it does; T1/T2 is the test.** It is a
  genuine possible outcome that it changes little at default depth, since upstream
  documentation warns "too few cells will result in poor adhesion" (Research §4.7.3).
- **Model requirements.** **Identical file to T1.** No geometry change of any kind.
- **Filaments & drying.** **Same spools** as T1, same drying state, ideally same session.
  Record hours elapsed since T1.
- **Toolheads.** Identical to T1 (PLA → T0, TPU 95A → T2).
- **Orca settings to record.** All of §5, plus — **the variable** — Beam Interlocking **ON**
  with **defaults unchanged**, recorded verbatim: interlocking beam width, interlocking
  direction, interlocking beam layers, **interlocking depth (cells)**, **interlocking
  boundary avoidance (cells)**. **Do not tune these.** If the defaults are later judged
  inadequate, that becomes a new pair T2a/T2b with one changed value.
- **Tower settings.** Identical to T1. Record again from the UI (do not copy T1's record —
  enabling interlocking may alter derived values, and that itself is worth capturing).
- **Evidence.** E1–E8, plus a macro photo showing the interlocking structure at the
  interface if it is visually resolvable, and a slicer preview screenshot of the interlocked
  region.
- **Pass / fail.** Same gate as T1. Comparison is recorded as: *T2 interface separated at
  lower / similar / higher hand load than T1*, plus the same four-way separation-mode
  classification. **Do not convert this into a strength figure or a percentage** — hand peel
  is qualitative, and saying otherwise would be fake precision.
- **Safety.** S1–S8. Interlocking increases toolchange count at the interface; watch S2.
- **One-variable rule.** Beam Interlocking is the **only** difference from T1.

---

### T3 — PETG + TPU 95A, **flat interface**

- **Hypothesis.** A flat PETG↔TPU 95A interface bonds better than the PLA↔TPU baseline (T1),
  because Snapmaker describes PETG + TPU as a strongly-bonding pair printable as structural
  parts without special bonding settings (Research §3.3.1). Baseline for T4.
- **Model requirements.** **Same coupon geometry as T1/T2**, with PETG replacing PLA.
  Supports (if any) start on the plate.
- **Filaments & drying.** PETG (rigid B) and **the same TPU 95A spool as T1/T2** where
  possible. Full §3 records. Note that PETG's bed temperature differs from TPU's stated
  25–60 °C range — record the bed temperature actually used and which material's requirement
  it favours (Research §3.3.4). This is a recorded constraint, not a setting we invent.
- **Toolheads.** PETG → **T1**. TPU 95A → **T2**. TPU manual load, Auto Loading disabled.
- **Orca settings to record.** All of §5. **Beam Interlocking = OFF**, stated explicitly.
  Record PETG max volumetric speed and both nozzle temperatures verbatim.
- **Tower settings.** Matrix baseline. **Watch the tower especially closely here** — the
  official prime-tower guidance warns that poor inter-material adhesion delaminates the
  tower at the material interface (Research §4.6.3), and PETG/TPU is the pair where the
  official claim (strong bond) and the tower-failure mode can be checked against each other.
- **Evidence.** E1–E8. Tower photos (E2) are especially important in T3/T4.
- **Pass / fail.** Same gate as T1. Record the same four-way separation-mode classification,
  plus a note on whether tower layers show any interface delamination.
- **Safety.** S1–S8. PETG stringing between tower and part is a realistic S1 precursor —
  abort if strings are being dragged into the part.
- **One-variable rule.** T3 and T4 differ **only** in Beam Interlocking OFF→ON. T3 differs
  from T1 only in the rigid material (PLA→PETG) **and** the bed/nozzle temperatures that
  PETG requires — this cross-pair difference is acknowledged and is why T1↔T3 is a weaker
  comparison than T1↔T2. State that limitation in any write-up.

---

### T4 — PETG + TPU 95A, **Beam Interlocking**

- **Hypothesis.** Beam Interlocking on an already-strongly-bonding pair adds little
  interface benefit while adding print time, material, and toolchanges — i.e. it is the
  wrong tool for PETG+TPU. **This is the most decision-useful question in the matrix**: if
  confirmed, the honest guidance becomes "interlock the weak pair, not the strong one."
  It may equally turn out that interlocking helps everywhere. We do not know.
- **Model requirements.** **Identical file to T3.**
- **Filaments & drying.** Same spools as T3, same session where possible.
- **Toolheads.** Identical to T3.
- **Orca settings to record.** All of §5, plus — **the variable** — Beam Interlocking **ON**,
  **defaults unchanged**, all five parameters verbatim. Also record the slicer's reported
  estimate delta versus T3 (print time and material) **as shown by Orca**, clearly labelled
  as a slicer estimate, not a measurement.
- **Tower settings.** Identical to T3, re-recorded from the UI.
- **Evidence.** E1–E8, plus slicer preview of the interlocked region and the Orca time/
  material estimate screenshot for both T3 and T4.
- **Pass / fail.** Same gate as T3. Comparison recorded as: interface behaviour T4 vs T3
  (four-way classification), plus the Orca-reported cost in time/material. No numeric bond
  strength claim.
- **Safety.** S1–S8.
- **One-variable rule.** Beam Interlocking is the only difference from T3.

---

### T5 — PLA part with **TPU support interface**, baseline

- **Hypothesis.** TPU used as the **support interface** under a PLA part releases more
  cleanly than PLA-on-PLA supports and leaves a better surface, because weak inter-material
  adhesion is officially framed as a *feature* for supports with zero Z-distance
  (Research §3.5.3). The inverse direction (PLA supporting TPU) is community-reported to
  work well (Research §3.5.4); **this direction is unsourced** (Research §3.5.5) and is
  exactly why it is being tested.
- **Model requirements.** A PLA part with a **plate-borne overhang** — e.g. a bridge or
  cantilever ~40 mm wide with a 30–40 mm unsupported span, supported from the plate only.
  **No model-borne supports** (pre-condition P7 — if the Orca build applies interface
  material only to plate-touching supports, model-borne supports would invalidate the test).
  Same geometry for T5 and T6.
- **Filaments & drying.** PLA (rigid A) + TPU 95A (flexible A). Full §3 records.
- **Toolheads.** PLA → **T0**. TPU 95A → **T2** (support interface material). Manual TPU load.
- **Orca settings to record.** All of §5, plus the full support block **verbatim**: support
  on/off and type, support filament (base) and **support interface filament**, top Z
  distance, bottom Z distance, top/bottom interface layers, interface pattern, interface
  spacing, support base pattern, support threshold angle. **Beam Interlocking = OFF.**
  **T5 uses the shipped Orca support defaults** for everything except the interface-material
  assignment — that is what makes it a baseline.
- **Tower settings.** Matrix baseline; record fully.
- **Evidence.** E1–E8, plus: macro of the **downward-facing surface** after support removal;
  photo of the removed support raft itself; a note on removal effort (*fell away / peeled by
  hand / needed tools / tore the part surface*).
- **Pass / fail.**
  - **Records-complete gate** as in T1.
  - **Recorded observations:** support removal effort (four-way, above); downward surface
    quality (visible interface lines / scarring / clean); whether any TPU remained fused to
    the part.
  - **Automatic FAIL:** the overhang collapsed, the support detached mid-print, or S1–S6.
- **Safety.** S1–S8. A soft support that deforms rather than supports can let the overhang
  droop into the nozzle path — watch the first bridging layer.
- **One-variable rule.** T5 and T6 differ **only** in the support-interface settings changed
  in T6 (listed there). Same model, same spools, same toolheads, same tower, same part
  temperatures.

---

### T6 — PLA part with **TPU support interface**, optimized

- **Hypothesis.** Applying Snapmaker's **officially published dissimilar-material support
  recipe** — top Z distance **0**, top interface layers **3**, interface pattern
  **Rectilinear Interlaced**, top and bottom interface spacing **0**, support base pattern
  **Rectilinear** (Research §3.5.2) — improves both release and downward-surface quality
  versus the T5 defaults. Note that the recipe is published for **PLA/PETG**, not for TPU
  interfaces; applying it here is a **deliberate, declared extrapolation**, and if it does
  not transfer, that is a publishable finding in its own right.
- **Model requirements.** **Identical file to T5.**
- **Filaments & drying.** Same spools as T5.
- **Toolheads.** Identical to T5.
- **Orca settings to record.** All of §5 and the full support block as in T5, with **the
  variable** being the support-interface settings above, each recorded verbatim as actually
  set. **Nothing else changes** — not layer height, not temperature, not the part model.
  Beam Interlocking remains OFF.
- **Tower settings.** Identical to T5, re-recorded.
- **Evidence.** E1–E8 plus the same support-specific evidence as T5, photographed from the
  same angle and distance as T5 so the two are directly comparable.
- **Pass / fail.** Same gate as T5. Comparison recorded as: removal effort T6 vs T5;
  downward surface T6 vs T5 (better / same / worse, with photos side by side). No claim
  that the settings are "correct" — only what was observed on this model, this machine.
- **Safety.** S1–S8. Top Z distance 0 means the interface is in contact with the part;
  watch for the support welding rather than releasing, and abort on S4 if the part lifts.
- **One-variable rule.** Only the support-interface settings differ from T5. If the recipe
  requires a temperature change to be applied at all, that is a **second variable** — split
  it into T6a (settings only) and T6b (settings + temperature) rather than confounding them.

---

### T7 — **TPU 95A + TPU 90A**, baseline

- **Hypothesis.** Two TPU grades bond well to each other (same polymer family; Snapmaker
  states TPU 90A co-prints with TPU 95A — Research §3.6.1), but the **all-flexible prime/
  wipe tower is the weak point**: a soft tower may deform under nozzle contact instead of
  standing, and two flexibles loaded simultaneously doubles the manual-load and toolchange
  risk (Research §3.6.4). This run establishes the baseline at **shipped Orca defaults**.
- **Model requirements.** **Same coupon geometry as T1–T4** (so interface behaviour is
  comparable across the whole matrix), with TPU 95A in place of the rigid material and
  TPU 90A in place of flexible A. Supports, if any, plate-borne only.
- **Filaments & drying.** TPU 95A and TPU 90A. **Both** get full §3 spool records, both
  dried per their own manufacturers' specs. This is the run most sensitive to moisture —
  print from dry storage if at all possible and record whether you did.
- **Toolheads.** TPU 95A → **T2**. TPU 90A → **T3**. **Both loaded manually**, Auto Loading
  disabled on both, 45° cuts. **Record load attempts and success for each** — this pair is
  the best available data on flexible-only loading behaviour.
- **Orca settings to record.** All of §5, at **shipped defaults for both filaments**.
  **Beam Interlocking = OFF.** Record both retraction-at-toolchange values verbatim, both
  max volumetric speeds, both temperature sets, and both cooling-fan configurations.
- **Tower settings.** Matrix baseline (Rib, no-sparse-layers OFF, ≤90 mm/s, square, brim
  ≥ default). **Tower outcome is a headline result of this test, not a footnote.**
- **Evidence.** E1–E8, with E2 (tower, two angles, full height) mandatory and given equal
  weight to the interface photos. Add a photo of the tower **base** specifically.
- **Pass / fail.**
  - **Records-complete gate** as in T1.
  - **Recorded observations:** tower outcome (*stood clean / visibly deformed / leaned /
    contacted by nozzle / collapsed*); interface separation mode (four-way as T1);
    toolchange behaviour across the run.
  - **Automatic FAIL:** S1 (tower) or S2 (jam) — and for this test, note that a tower
    failure here is a *substantive finding*, not merely a lost run.
- **Safety.** S1–S8, with S1 and S2 at heightened attention. Supervise continuously through
  the first five toolchanges.
- **One-variable rule.** T7 and T8 differ **only** in the change listed in T8.

---

### T8 — **TPU 95A + TPU 90A**, optimized

- **Hypothesis.** The dominant failure mode for an all-flexible job is **toolchange filament
  handling**, not interface bonding — so the single highest-value change is the
  **retraction-at-toolchange value** for both flexible filaments (Research §4.4). Reducing it
  from the shipped default improves toolchange reliability without harming the interface.
  **This is currently a vendor claim (C-level) and this test is the only thing that can
  raise it.**
- **Model requirements.** **Identical file to T7.**
- **Filaments & drying.** Same spools as T7, same drying state, same session where possible.
- **Toolheads.** Identical to T7.
- **Orca settings to record.** All of §5, with **exactly one change from T7**: the
  **retraction-at-toolchange / material-switch value** for both TPU filaments, moved from the
  shipped default (recorded in P5) to a **single stated lower value chosen at run time and
  written down before slicing**. Do not also change retraction length, retraction speed,
  purge volumes, temperatures, or speeds. Beam Interlocking stays OFF.
  > The vendor-suggested range is 0–4 mm (Research §4.4.1). We are testing *a* lower value,
  > recorded verbatim — we are **not** endorsing that range, and the tutorial must not
  > present it as a Snapmaker setting.
- **Tower settings.** Identical to T7, re-recorded.
- **Evidence.** E1–E8 as T7, plus an explicit toolchange-behaviour log: number of
  toolchanges completed, any hesitation, any audible gear slip, any visible filament
  deformation at the gears on unload.
- **Pass / fail.** Same gate as T7. Comparison recorded as: toolchange incidents T8 vs T7
  (count and description); tower outcome T8 vs T7; interface separation mode T8 vs T7.
  **A single paired run cannot establish that a value is "correct"** — it can only show
  whether this run behaved differently. Say exactly that in any write-up.
- **Safety.** S1–S8. A **lower** retraction at toolchange can increase oozing and
  tower/part contamination — watch for strings being dragged (S1 precursor).
- **One-variable rule.** The retraction-at-toolchange value is the only difference from T7.
  Any further tuning becomes T8a/T8b.

---

## 9. Matrix summary

| ID | Pair | Rigid / flexible A | Flexible B | The one variable | Primary question |
|---|---|---|---|---|---|
| T1 | A | PLA | TPU 95A | *(baseline)* | Flat rigid–flexible interface behaviour |
| T2 | A | PLA | TPU 95A | Beam Interlocking ON (defaults) | Does interlocking change a weak-bond pair? |
| T3 | B | PETG | TPU 95A | *(baseline)* | Is the officially "strong" pair strong here? |
| T4 | B | PETG | TPU 95A | Beam Interlocking ON (defaults) | Does interlocking help a strong pair, or just cost? |
| T5 | C | PLA part | TPU 95A interface | *(baseline, Orca defaults)* | Does TPU release cleanly as a support interface? |
| T6 | C | PLA part | TPU 95A interface | Official dissimilar-support recipe applied | Does the PLA/PETG support recipe transfer to TPU? |
| T7 | D | TPU 95A | TPU 90A | *(baseline)* | Does an all-flexible job hold — especially the tower? |
| T8 | D | TPU 95A | TPU 90A | Retraction at toolchange lowered | Is toolchange retraction the real flexible failure mode? |

**Cross-matrix comparisons that are valid:** within a pair (T1↔T2, T3↔T4, T5↔T6, T7↔T8).
**Cross-matrix comparisons that are weaker and must be labelled as such:** T1↔T3 (rigid
material *and* temperatures differ), any comparison involving T7/T8 (no rigid material at
all). Do not present weak comparisons as controlled results.

---

## 10. What this matrix can and cannot establish

**Can:** whether these specific configurations, on one machine, with these spools, produced
a bond/release/tower outcome that a person could observe and photograph; whether a named
variable changed that outcome in a paired run; what the shipped Orca defaults actually are.

**Cannot:** bond strength in engineering units; statistical significance (n=1 per cell);
generalisation to other spools, brands, geometries, machines, or Orca versions; any claim
that a configuration "will print" for a reader. Eight prints are a starting point, not a
dataset.

**Anything published from these results must carry that limitation in the same breath as
the result.**
