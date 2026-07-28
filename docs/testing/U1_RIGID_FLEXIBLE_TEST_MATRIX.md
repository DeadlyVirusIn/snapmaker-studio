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
| **P3** | **Dynamic Flow Calibration is OFF for every test in this matrix.** Before starting each print, confirm the **"Dynamic Flow Calibration" box is unticked** in the touchscreen Print Preferences step (Start → Next → Print Preferences), and record that state in the run header **and** as a screenshot (E9). **REPLACES the earlier precondition, which wrongly required DFC after every filament change.** | Snapmaker's TPU-specific guide states: *"Because TPU is soft and compressible it tends to expand and contract during extrusion. This makes dynamic flow calibration unreliable and can negatively affect print quality. Make sure this feature is turned off when starting a print job."* **Every test T1–T8 has TPU loaded**, so the TPU-specific rule governs all of them. Holding it **constant OFF** means DFC can never become a hidden variable, and it keeps every run inside current official TPU guidance. | Research §4.5.B, §4.5.D |
| P3b | Do **not** apply the generic "run DFC after every filament change" guidance anywhere in this matrix, and do not treat DFC-off as general calibration advice outside TPU jobs. | The generic guidance remains correct for non-TPU work; conflating the two in either direction is the error this matrix was corrected to remove. | Research §4.5.A, §4.5.D |
| **P4** | **Record the exact installed Snapmaker Orca version** (read it from Orca, do not assume). It **must be 2.3.4 or later**, because Snapmaker's official **TPU 90A** and **TPU 95A HF** filament profiles require 2.3.4+. If the profiles are missing, import them via Filament Management before recording. **DFC is not the reason for this gate** — DFC is OFF throughout (P3). Record the version as *"the version installed on this machine on this date"*, not as "the latest version". | Every test loads TPU and depends on the official TPU profiles. Version-specific slicer behaviour is also a known confounder (support-interface behaviour, §3.5.6), so the exact build must be on record for each run. | Research §2.8 |
| P5 | **The shipped toolchange-retraction values are read out of the Orca profiles and written down verbatim — separately for TPU 95A HF and for TPU 90A, and for each rigid filament used.** Location: filament profile → **Setting Overrides**. No test changes them unless the test says so. | Snapmaker gives the **direction only** ("lower the toolchange retraction length under 'Setting Overrides'") and publishes **no value**; the circulated "0–4 mm" is a vendor figure. The shipped numbers must be facts on paper before T8 can be designed. | Research §4.4.0, §4.4.3 |
| **P5b** | **T8's experimental value is pre-registered and frozen before either T7 or T8 is sliced** — see §8/T8 and the pre-registration block there. No value may be chosen during a print session. | Choosing the value after seeing T7 turns a controlled comparison into an unrecorded search. | §1 rule 8 |
| P6 | **The shipped Beam Interlocking defaults are read out of Orca and written down verbatim** (beam width, direction, beam layers, depth, boundary avoidance). | No published values exist for TPU pairs; we use defaults and record them rather than inventing a recipe. | Research §4.7.4 |
| P7 | Support-interface behaviour check: confirm on this Orca build whether the interface material is applied to supports **growing from the model**, not only plate-touching supports. | If it reproduces, T5/T6 are invalid unless all supports start on the plate. | Research §3.5.6 |
| P8 | No nozzle is shared between two different materials within the matrix. Toolhead↔material assignment is fixed at the start (§2) and never reassigned mid-matrix. | Prevents cross-material residue being mistaken for a bond result. | Research §4.8.4 |
| P9 | Every spool dried and logged per §3 **before** its first use in the matrix, and re-dried per §3 if it has been out of a dry container beyond the stated window. | TPU is "extremely hygroscopic and must be dried before use". | Research §4.1 |
| P10 | Ambient temperature and relative humidity recorded at the start of each run. | Cheap to record; expensive to reconstruct later. | — |

**Out of scope, deliberately:**

- **ABS/ASA + TPU.** Not because the pairs are unclassified — **they are officially
  classified "–" (Bondable)** in Snapmaker's adhesion table. They are excluded because
  (a) **no published combined process recipe** exists, (b) their **documented
  thermal/cooling requirements are incompatible** — Snapmaker states that high-temperature
  filaments such as ABS/ASA "cannot be printed at the same time as low-temperature
  filaments, such as PLA, TPU, and PVA", the top cover's two circulation modes being
  mutually exclusive — and (c) covering them needs a **separately resourced top-cover
  phase** with the hardware fitted. See Research §3.4.
- **TPU below 90A**, officially still under validation by Snapmaker. See Research §2.5.

---

## 1. The one-factor-at-a-time rule

This is the rule that makes the matrix worth running. It is not advisory.

1. **Tests are run in pairs.** Within a pair (T1/T2, T3/T4, T5/T6, T7/T8), **exactly one
   pre-registered factor** differs. Everything else — model, orientation, plate position,
   layer height, temperatures, speeds, tower settings, toolhead assignment, spool, drying
   state — is byte-identical between the two.

   > **What "one factor" means here.** A factor is normally a single setting (T2/T4: Beam
   > Interlocking on/off; T8: the pre-registered toolchange-retraction change). It may also
   > be a **named, pre-registered, inseparable bundle** — a published recipe applied whole,
   > as in T5/T6. A bundle is legitimate **only if** it is (a) named and written down before
   > either run, (b) applied in full with nothing added or omitted, and (c) reported as a
   > bundle. **A bundle comparison can evaluate the bundle and nothing else** — it can never
   > attribute an outcome to one setting inside it. Anything not meeting all three
   > conditions is not one factor; it is an uncontrolled multi-change and is not run.
2. **The differing factor is named in the test header** and is the only thing allowed to
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
8. **Pre-registration.** Where a test changes a numeric value, that value is **written down
   and frozen before the first run of the pair is sliced**, together with its rationale and
   the date it was fixed. Values are never chosen mid-session, and never chosen after seeing
   the baseline result. A value picked at run time makes the pair **VOID**.

> Snapmaker's own prime-tower guide gives the same instruction in its own words: **"Apply
> one corrective action at a time to accurately identify the root cause."** (Research §4.6.3b)

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
  Dynamic Flow Calibration state at print start:   OFF (required)  /  ON (=> VOID run)
    "Dynamic Flow Calibration" box confirmed unticked in Print Preferences?  yes / no
    Screenshot/photo of that screen captured (E9)?                           yes / no
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
>
> **Two officially-documented tower facts that apply to every run here:** TPU wipe towers
> "have weak layer-to-layer support and low rigidity, making them more likely to collapse
> when pulled or bumped"; and by default the wipe tower is printed with **all** involved
> materials, which further reduces vertical stability when those materials adhere poorly —
> Snapmaker's own example being **TPU & PLA** (Research §4.6.6–4.6.7).
>
> **Wipe-tower shell filament: hold at the Orca default (all involved materials) for the
> whole matrix, and record it.** Snapmaker's official mitigation — assigning a single spool
> to the wipe tower under **"Filament for Features"** — is deliberately **not** applied here.
> If a tower failure (S1) occurs, that mitigation may only be explored as a **new, separately
> pre-registered pair**, never by editing a run mid-pair. Record the shell assignment in
> every run so it is visibly constant.

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
| **E9** | **Photo or screenshot of the touchscreen Print Preferences screen showing the "Dynamic Flow Calibration" box unticked**, captured for every run. | P3 is the correction this matrix exists to enforce; an unphotographed DFC state is an unverifiable run. |

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
| S3 | Extrusion stops or goes intermittent on any toolhead. | Abort. Follow Snapmaker's published options in order: **Heat Creep/Flow Check** (raise the nozzle slightly above the filament's standard print temp and check the purge line falls straight), then **Needle/Cold Pull** with the supplied nozzle cleaning needle, repeating until extrusion is straight and stable (Research §4.8.1, §4.8.3). **This project uses no flame or torch method on any hot end** — our protocol rule, not a quoted Snapmaker prohibition (Research §4.8.2b). |
| S4 | The part detaches from the plate or a layer shift is visible. | Abort. Record; do not resume. |
| S5 | Any smell of burning, smoke, unusual noise, or a component visibly out of position. | **Abort and power down at the switch.** Do not restart until inspected. Escalate before any further run. |
| S6 | A toolhead fails to park/pick up, or the machine reports a calibration/firmware error. | Abort. Re-run pre-conditions P1–P2 before any further test. Do not "just retry". |
| S7 | The run is unattended and any of S1–S6 cannot be observed. | **Do not run this matrix unattended.** Every run in this matrix is supervised for at least the first 15 minutes and checked at least every 30 minutes thereafter. |
| S8 | The one factor under test can no longer be held (spool ran out mid-pair, Orca auto-updated, machine moved). | Mark the run **VOID** and re-run **both** halves of the pair (§1.3). |

---

## 8. The eight controlled prints

Each test below states: hypothesis · model requirements · filaments & drying · toolheads ·
Orca settings to record (beyond §5) · tower settings · evidence · pass/fail · safety ·
one-factor rule (§1).

---

### T1 — PLA + TPU 95A, **flat interface**

- **Hypothesis.** **PLA + TPU is officially classified "–" (Bondable)** — Snapmaker's own
  definition being materials that "show weaker chemical adhesion" (Research §3.2.0, §3.1.2).
  A flat, non-interlocked PLA↔TPU 95A interface is therefore expected to be the weaker of
  the two rigid-flexible interfaces in this matrix. **How that weakness actually presents at
  a flat interface is physically unmeasured** — no force, no separation mode, no published
  figure. This run establishes the **baseline** T2 is measured against. *We predict no
  specific force; we record what happens.*
  > Secondary context only, **C**: community and third-party sources describe PLA and TPU as
  > not forming a permanent chemical bond (Research §3.2.3). That is colour, not the basis
  > of this test — the official classification is.
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

- **Hypothesis (revised after re-verification).** **PLA + TPU is now officially named by
  Snapmaker as one of "two common and practical combinations" of low-adhesion materials for
  easy-removal supports** (Research §3.5.0) — so the *pairing* is no longer speculative.
  What remains genuinely unestablished is the **direction and the settings**: the guide does
  not say which material is the part and which is the support, and every numeric value it
  publishes is for **PLA/PETG** (Research §3.5.0b, §3.5.2). The hypothesis under test is
  therefore narrower and more honest than the first pass's: *with TPU as the support
  interface under a PLA part, at Orca's shipped support defaults, the interface releases
  cleanly and leaves an acceptable downward surface.* The opposite direction (PLA supporting
  TPU) is the one with vendor evidence behind it (Research §3.5.4, **C**); if T5/T6 shows
  our direction behaves poorly, that is a publishable result, not a failed test.
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
- **One-factor rule — declared bundle comparison.** T5/T6 is **not** a single-setting test
  and is not presented as one. It is a **pre-registered intervention-bundle comparison**:
  **Arm A (T5) = Orca's shipped support defaults**, **Arm B (T6) = the complete published
  PLA/PETG support recipe extrapolated to a TPU interface**, applied whole. See the boxed
  design statement under T6. Same model, same spools, same toolheads, same tower, same part
  temperatures.

---

### T6 — PLA part with **TPU support interface**, optimized

- **Hypothesis.** Applying Snapmaker's published dissimilar-material support recipe — top Z
  distance **0**, top interface layers **3**, interface pattern **Rectilinear Interlaced**,
  top and bottom interface spacing **0**, support base pattern **Rectilinear**
  (Research §3.5.2) — improves both release and downward-surface quality versus the T5
  defaults.
  > **Evidence label, stated precisely.** That recipe is **published for PLA/PETG only**.
  > Snapmaker names PLA+TPU as a valid low-adhesion *pairing* but publishes **no** TPU
  > interface settings, temperatures, Z-distance or spacing (Research §3.5.0b). Applying the
  > PLA/PETG numbers to a TPU interface is a **declared extrapolation by us**, tagged **T**.
  > **Nothing in T6 may be written up as "Snapmaker's recommended TPU support settings."**
  > If the recipe does not transfer, that is a publishable finding in its own right.
- **Temperature caveat.** The guide's PLA 230 °C / PETG 265 °C / bed 65 °C values are
  PLA/PETG-specific and are **not** carried over. TPU temperatures follow that spool's own
  manufacturer spec, held identical to T5.

> ### T5/T6 experimental classification — read before running either arm
>
> **T5/T6 is a pre-registered intervention-bundle comparison, not a one-setting test.**
>
> - **Arm A (T5)** — *Orca shipped support defaults*, with only the interface **material**
>   assigned to TPU.
> - **Arm B (T6)** — *the complete published PLA/PETG support recipe, extrapolated to a TPU
>   interface*: Top Z distance **0**, support base pattern **Rectilinear**, **Top interface
>   layers 3**, interface pattern **Rectilinear Interlaced**, top and bottom interface
>   spacing **0** — applied **whole**, nothing added, nothing omitted.
>
> **Pre-registration.** The exact contents of Arm B are frozen and written down before T5 is
> sliced (§1 rule 8). Changing any member of the bundle after that point voids the pair.
>
> **What this design can conclude:** whether *the bundle as a whole* changed release effort
> or downward-surface quality versus shipped defaults, on this model and this machine.
>
> **What it can never conclude:** that Top Z distance 0, or 3 interface layers, or
> Rectilinear Interlaced, or zero spacing, or the Rectilinear base pattern **individually**
> caused anything. **No individual support setting may be described as independently
> proven, validated, or recommended for TPU on the basis of T5/T6.** Any per-setting claim
> requires its own pre-registered single-setting pair (T5a/T6a, T5b/T6b, …), which this
> phase does not schedule.
>
> **Why the bundle rather than a split.** Splitting Arm B into five single-setting pairs
> would cost ten prints on its own and push the matrix past what one supervised session can
> hold. The bundle keeps the matrix at eight prints and tests the thing a reader would
> actually do — apply the published recipe as published. The cost of that choice is stated
> above and must be repeated wherever the result is reported.
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

- **Hypothesis — deliberately makes no prediction about the bond.**
  - Snapmaker states that TPU 90A **co-prints with TPU 95A** (Research §3.6.1), so the
    combination is supported.
  - **No official conclusion about interfacial strength between the two grades was found.**
    The adhesion table's diagonal is "/" (same material) and says nothing about grade-to-grade
    bonding (Research §3.6.2b). Any statement that two TPU grades "bond well to each other"
    is unsupported and has been removed.
  - T7 therefore **observes three things and predicts none of them**: (a) interface
    behaviour at the 95A↔90A boundary, (b) tower behaviour on an all-flexible job — where
    Snapmaker does document that "TPU wipe towers have weak layer-to-layer support and low
    rigidity" (Research §4.6.6), and (c) toolchange behaviour with two flexibles loaded.
  - Baseline at **shipped Orca defaults** for both TPU profiles.
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
  **Evidence status, corrected:** Snapmaker **officially recommends lowering the toolchange
  retraction length** — under the filament profile's *Setting Overrides* — as a **remedial
  response** to TPU building up inside the print head or squeezing out through small gaps
  (Research §4.4.0). The **direction is official**. Snapmaker publishes **no number and no
  range** (Research §4.4.0b), and the circulated 0–4 mm figure remains a vendor claim
  (Research §4.4.1). **The experimental magnitude is therefore untested and must be
  pre-registered** — see the gate below.
- **Model requirements.** **Identical file to T7.**
- **Filaments & drying.** Same spools as T7, same drying state, same session where possible.
- **Toolheads.** Identical to T7.
- **Orca settings to record.** All of §5, with **exactly one factor changed from T7**: the
  **toolchange retraction length** (filament profile → **Setting Overrides**) for the TPU
  filaments, moved from the shipped defaults to the **pre-registered** value or rule below.
  Do not also change retraction length, retraction speed, purge volumes, temperatures, or
  speeds. Beam Interlocking stays OFF. Dynamic Flow Calibration stays OFF (P3).

#### T8 pre-registration gate — complete and sign **before T7 is sliced**

No value may be selected during a print session, and none is invented in this
documentation phase. The gate below is filled in once, on paper, and frozen.

```
T8 PRE-REGISTRATION  (complete BEFORE slicing T7 — not after seeing T7's result)

  Step 1 — Read the shipped values (pre-condition P5). Transcribe from Orca:
    Toolchange retraction length, Snapmaker TPU 95A HF profile:  ______ mm
    Toolchange retraction length, Snapmaker TPU 90A profile:     ______ mm
    Orca version these were read from:                           ______
    Read on (date):                                              ______
    Are the two shipped values equal?                            yes / no

  Step 2 — Fix the experimental factor. Choose EXACTLY ONE form:
    [ ] Form A — absolute value:   set BOTH TPU profiles to ______ mm
    [ ] Form B — reduction rule:   set each TPU profile to its shipped value
                                   reduced by ______ mm  (or × ______)
    Chosen form and exact numbers:  ______________________________________

  Step 3 — Rationale (why this value/rule, in one paragraph, citing sources):
    ______________________________________________________________________
    Note: Snapmaker publishes the DIRECTION only ("lower the toolchange
    retraction length"), no value (Research §4.4.0b). The circulated 0–4 mm
    range is a VENDOR figure (Research §4.4.1). State plainly which of these
    informed the choice — and that neither makes the number official.

  Step 4 — Freeze.
    Value fixed on (date):        ______
    Fixed by:                     ______
    T7 sliced on (date):          ______   (must be AFTER the date above)
    Confirmed unchanged at T8 slicing?   yes / no
```

**If the pre-registered value is changed after T7 has been sliced or run, the T7/T8 pair is
VOID.** Re-register and re-run both halves.

#### Does changing two profile values break the one-factor rule?

**Examined explicitly, because it is a real threat to the design.**

- If Step 1 finds the **two shipped values are equal**, then Form A sets one number in two
  places. That is **one factor**, and the pair is clean.
- If the shipped values **differ**, then Form A (one absolute value for both) changes the
  two profiles by **different amounts** — two different numeric deltas. Calling that "one
  measurement" would be dishonest.

**Resolution — and it is a choice, not a fudge:**

- **Preferred: Form B, a proportional or fixed-offset reduction rule** applied identically
  to both profiles. This is a genuine **single policy-level factor** — "toolchange
  retraction, reduced by the same rule for every flexible filament in the job" — and it is
  described that way in the write-up. It is explicitly **not** claimed to be a measurement
  of one number.
- **Alternative, if a specific absolute value is what matters:** split the experiment.
  **T8a** changes the TPU 95A profile only; **T8b** changes the TPU 90A profile only; each
  is its own pair against T7. This costs two extra prints and buys per-filament
  attribution.
- **Not permitted:** setting two different numbers and reporting the result as though a
  single variable had moved.

Whichever route is taken, the write-up must state: *"the factor under test was
[absolute value X applied to both profiles / reduction rule R applied to both profiles /
a single profile], pre-registered on [date]."*
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
- **One-variable rule.** The pre-registered toolchange-retraction factor is the only
  difference from T7. Any further tuning is a **new pre-registered pair**, never an edit to
  T8.
- **Hypothesis status.** T8 tests *a pre-registered magnitude of an officially endorsed
  direction*. It cannot establish that any number is "correct".

#### T7/T8 interpretation rule — decide the reading from T7's incident count

A **toolchange incident** is defined before the runs, and only these count: a stalled or
repeated toolchange · audible gear slip · visible filament deformation at the gears on
unload · filament buckling or bird-nesting · an S2 abort. Each is logged with a timestamp
and the toolchange number.

| T7 result | What T8 may conclude |
|---|---|
| **T7 records ≥ 1 incident** | T8 **may compare incident behaviour** against T7 — count, type, and timing. Still a single paired run: report it as *"with the pre-registered value, incidents went from N to M in one run"*, never as a reliability rate or a percentage. |
| **T7 records 0 incidents** | **T8 cannot claim improved reliability — there was nothing to improve on.** T8 may only record whether the changed value **caused adverse effects** (oozing, tower or part contamination, stringing, extrusion gaps, surface defects) or was **behaviourally neutral**. |

**A clean T7 plus a clean T8 is not evidence that the lower value is better.** It is
evidence that neither configuration produced an incident in one run each. Any write-up must
say exactly that. If a reliability question needs answering properly, it needs repeat runs
at both levels — which this eight-print matrix does not provide.

This rule is fixed **now**, before any run, so the reading of the result cannot be chosen
after seeing it.

---

## 9. Matrix summary

| ID | Pair | Rigid / flexible A | Flexible B | The one factor | Primary question |
|---|---|---|---|---|---|
| T1 | A | PLA | TPU 95A | *(baseline)* | Flat rigid–flexible interface behaviour |
| T2 | A | PLA | TPU 95A | Beam Interlocking ON (defaults) | Does interlocking change a weak-bond pair? |
| T3 | B | PETG | TPU 95A | *(baseline)* | Is the officially "strong" pair strong here? |
| T4 | B | PETG | TPU 95A | Beam Interlocking ON (defaults) | Does interlocking help a strong pair, or just cost? |
| T5 | C | PLA part | TPU 95A interface | *(baseline, Orca defaults)* | Does TPU release cleanly as a support interface? |
| T6 | C | PLA part | TPU 95A interface | **Bundle**: published PLA/PETG support recipe applied whole | Does the recipe **as a bundle** transfer to a TPU interface? (no per-setting attribution) |
| T7 | D | TPU 95A | TPU 90A | *(baseline)* | Does an all-flexible job hold — especially the tower? |
| T8 | D | TPU 95A | TPU 90A | Toolchange retraction lowered (**pre-registered**) | Is toolchange retraction the real flexible failure mode? |

**Held constant across all eight tests (never variables):** Dynamic Flow Calibration **OFF**
(P3) · wipe-tower shell = Orca default, all involved materials (§5) · `no_sparse_layers` OFF
· max purge speed ≤ 90 mm/s · Rib wall type · fixed toolhead↔material assignment (§2) ·
manual load/unload for every TPU toolhead with Auto Loading disabled.

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
that a configuration "will print" for a reader. **Nor can it attribute a T5/T6 outcome to
any individual support setting** (bundle design, §T6), or claim a reliability improvement
from T8 when T7 recorded no incidents (T7/T8 interpretation rule). Eight prints are a
starting point, not a dataset.

**Anything published from these results must carry that limitation in the same breath as
the result.**
