# U1 Rigid–Flexible & Flexible-Material Research

> **Research only. No settings are invented.** Every number in this document carries a
> source and an evidence level. Nothing here is a claim that a print will succeed.
> **Snapmaker Orca remains the slicer** — Snapmaker Studio reads a design, explains risk,
> and prepares a U1 profile copy for review in Orca. Studio does not slice and does not
> command the printer.
>
> Scope: preparation research for a rigid-flexible / flexible-material tutorial. This
> phase changes **no** conversion or validation behaviour.

---

## 1. Evidence levels used throughout

| Tag | Meaning | Allowed use |
|---|---|---|
| **O** | **Officially verified** — stated by Snapmaker in product documentation, the Snapmaker Wiki, the Snapmaker support centre, or a Snapmaker product page. | May be quoted as fact, with the source link. |
| **C** | **Community-reported** — user forums, third-party reviews, filament-vendor blogs, adjacent-ecosystem docs (Bambu/Prusa/OrcaSlicer upstream). | May be reported **as a report**, never as a setting Studio recommends. |
| **T** | **Inferred / requires physical testing** — a reasonable deduction from O/C evidence that has **not** been measured on a U1 by us. | May only appear as a hypothesis in the test matrix. Never as guidance. |

**Hard rule for this project:** a **C** finding never becomes an **O** setting. It becomes a
**T** hypothesis, and only physical evidence recorded in the test matrix can move it.

### 1.1 Source-access note — verification pass completed 2026-07-28

The first research pass could not fetch `wiki.snapmaker.com` (client-side rendered) or
`support.snapmaker.com` (HTTP 403) directly, and relied on search-engine extraction. **Those
sources were re-opened in a real browser on 2026-07-28 and read on the live page**; rows
confirmed that way are tagged **[verified 2026-07-28]**.

**Exactly one source in this document has not been re-opened: the Snapmaker U1 specs page**,
which is the sole basis for rows **2.2** and **2.4**. Those two rows carry an explicit
not-re-opened marker instead of a verification date and remain listed in §8.2. **§1.1 and §8
agree: everything else cited here was read live.** Nothing is marked verified to tidy up a
flag.

Four outcomes from the verification work changed the evidence base materially:

1. **The adhesion classification table was read visually and transcribed** (§3.1.5).
2. **A newer, TPU-specific Snapmaker guide was found** that overrides generic guidance on
   Dynamic Flow Calibration (§4.5) and supplies official answers to several questions the
   first pass had left as inferred.
3. **One safety claim could not be substantiated and has been removed** (§4.8.2).
4. **The Top Cover note settles ABS/ASA + TPU** — the pairs are classified, but
   high- and low-temperature filaments cannot be printed in the same job (§3.4.3).

### 1.2 Conflict rule — newest and most material-specific wins

Where two official Snapmaker sources disagree, this project resolves as follows, and
**always records both**:

1. **Material-specific guidance beats generic guidance** for jobs using that material.
2. **Newer publication beats older** where both are equally specific.
3. **Documentation beats marketing/blog copy.**
4. The conflict is written down with both quotes and both dates. **Instructions are never
   silently merged**, and generic advice is never restated as if it were material-specific
   advice.

---

## 2. Machine and material baseline

| # | Finding | Level | Source |
|---|---|---|---|
| 2.1 | The U1 has **4 independent toolheads** (true multi-toolhead, not a single-nozzle MMU). Tool changes do not cause in-nozzle cross-contamination. | **O** | Already established in [`U1_PRINT_PROFILE_RESEARCH.md`](U1_PRINT_PROFILE_RESEARCH.md) |
| 2.2 | Base material support: **PLA, PETG, TPU, PVA, PCTG**. | **O — specs page not re-opened in the 2026-07-28 pass; still outstanding (§8.2)** | [Snapmaker U1 specs](https://www.snapmaker.com/snapmaker-u1/specs) |
| 2.3 | **With the top cover**, supported materials are **PLA, PETG, TPU, PVA, PET, ABS, ASA, PA, PC** — confirmed from a second official source. | **O** [verified 2026-07-28] | [Top Cover for Snapmaker U1](https://us.snapmaker.com/products/top-cover-for-snapmaker-u1), Specifications table |
| 2.4 | **With top cover + hardened-steel hot ends**: adds carbon-fibre and glass-fibre reinforced polymers. | **O — specs page not re-opened in the 2026-07-28 pass; still outstanding (§8.2)** | [Snapmaker U1 specs](https://www.snapmaker.com/snapmaker-u1/specs) |
| 2.5 | Verbatim: **"Currently compatible with TPU ≥ 90A Shore hardness."** / **"Softer grades (< 90A) are under active testing and validation."** | **O** [verified 2026-07-28] | [U1 Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) (article dated 2025-12-16) |
| 2.6 | The multi-material article's classification table covers **PLA, PETG, TPU, PET, ABS, ASA, PC, PA** (see §3.1.5). | **O** [verified 2026-07-28] | same |
| 2.7 | Snapmaker sells **two** TPU filaments for the U1: **95A HF** and **90A**. "The 95A HF is stiffer, supports higher print speeds and is generally easier to work with. The 90A version is softer and more elastic, making it more challenging to print." Both are "thoroughly tested and tuned" with built-in Snapmaker Orca profiles. | **O** [verified 2026-07-28] | [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) (video transcript, 00:44–01:09) |
| 2.8 | TPU profiles require **Snapmaker Orca 2.3.4 or later**; if the filament type is missing, import the latest "Snapmaker TPU 90A" and "Snapmaker TPU 95A HF" profiles via Filament Management. Current shipping Orca at time of writing: **V2.3.5** (2026-07-15). | **O** [verified 2026-07-28] | same (02:11–02:33); [U1 support category](https://support.snapmaker.com/hc/en-us/categories/36087874981527-Snapmaker-U1) |

**Consequence for the tutorial:** TPU **below 90A** is officially *not yet validated*. Any
tutorial content must say exactly that and must not present a working sub-90A recipe as
supported. If we test 85A, it is reported as **our observation on our machine**, tagged **T→C**,
never as a Snapmaker-supported configuration.

---

## 3. Material-pair findings

### 3.1 Snapmaker's own adhesion framing

| # | Finding | Level | Source |
|---|---|---|---|
| 3.1.1 | **Strong Bonding (+)**, verbatim: "Materials are naturally compatible, exhibiting **high interfacial adhesion**." / "They can be printed as **load-bearing or structural parts** without any additional bonding settings or process optimization." | **O** [verified 2026-07-28] | [Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |
| 3.1.2 | **Bondable (–)**, verbatim: "Materials show **weaker chemical adhesion**, but the interfacial bond can be significantly strengthened using **Snapmaker Orca's Beam Interlocking feature**… This makes them suitable for **rigid–flexible material combinations** and other functional multi-material structures. At the same time, weak-bonding materials are **ideal for dissimilar-material supports**: Their inherently low adhesion allows for **easy and clean support removal**; Cleaner interfaces result in **higher-quality bottom surfaces and finer detail**." | **O** [verified 2026-07-28] | same |
| 3.1.3 | Application scenarios named: **Rigid + Flexible Materials** ("articulated parts, overmolded designs, and soft-touch handles"), **Water-Soluble Supports (PVA)**, **Dissimilar-Material Supports (Easy-Remove)**. | **O** [verified 2026-07-28] | same |
| 3.1.4 | The article states further combinations are **"Under Testing: We are actively optimizing more material combinations."** | **O** [verified 2026-07-28] | same |

#### 3.1.5 Adhesion classification table — transcribed from the live page

Transcribed by visual inspection of the article's table on **2026-07-28** (the table is not
present in the page's extractable text, so it was read from the rendered page and zoomed to
confirm each cell). **No image from the page is stored in this repository** — only the
factual classifications, with the official page cited.

Legend as defined by the article itself (§3.1.1–3.1.2): **+ = Strong Bonding**,
**– = Bondable** (weaker chemical adhesion), **/ = same material (not applicable)**.

|        | PLA | PETG | TPU | PET | ABS | ASA | PC | PA |
|--------|:---:|:----:|:---:|:---:|:---:|:---:|:--:|:--:|
| **PLA**  | /  | –  | –  | –  | –  | –  | +  | –  |
| **PETG** | –  | /  | **+** | +  | +  | +  | +  | –  |
| **TPU**  | –  | **+** | /  | +  | –  | –  | –  | –  |
| **PET**  | –  | +  | +  | /  | +  | +  | +  | –  |
| **ABS**  | –  | +  | –  | +  | /  | +  | +  | +  |
| **ASA**  | –  | +  | –  | +  | +  | /  | +  | +  |
| **PC**   | +  | +  | –  | +  | +  | +  | /  | +  |
| **PA**   | –  | –  | –  | –  | +  | +  | +  | /  |

The matrix is fully symmetric, which was used as a read-back check on the transcription.

**What this settles for this project:**

- **PETG + TPU = "+" Strong Bonding.** Previously carried as a summarised claim; now
  **confirmed from the table itself**.
- **PLA + TPU = "–" Bondable.** Officially a weak-adhesion pair — which is exactly why it
  is both a Beam Interlocking candidate and a support candidate.
- **ABS + TPU = "–"** and **ASA + TPU = "–"**. These pairs **are** officially classified —
  correcting the first pass, which recorded them as entirely absent from official material.
  What remains absent is any **process guidance** for them (see §3.4).
- **PLA + PETG = "–"**, consistent with the published PLA/PETG support guide (§3.5).

> **The reframe worth naming in the article.** Snapmaker's own scheme says weak adhesion is
> **a defect when you want a structural join and a feature when you want a support that
> releases** — both readings appear in 3.1.2 verbatim. That is Snapmaker's framing, not
> ours; our contribution is only stating it plainly for a novice.

### 3.2 PLA + TPU

| # | Finding | Level | Source |
|---|---|---|---|
| 3.2.0 | **PLA + TPU is officially classified "–" (Bondable / weaker chemical adhesion)** in the adhesion table. | **O** [verified 2026-07-28] | §3.1.5 |
| 3.2.1 | **TPU + PLA** is listed among the combinations for which Beam Interlocking is offered "for stronger bonds". | **O** [verified 2026-07-28] | [Snapmaker TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) |
| 3.2.2 | Snapmaker TPU 90A supports "seamless multi-filament co-printing with **PLA, PETG, and TPU 95A**". | **O** [verified 2026-07-28] | same |
| 3.2.2b | Snapmaker names **TPU & PLA** as its own worked example of materials that "don't adhere well to each other", in the context of wipe-tower stability. | **O** [verified 2026-07-28] | [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) (06:35–06:46) |
| 3.2.3 | **Secondary context only.** Community/third-party sources describe PLA and TPU as not forming a permanent chemical bond, and use that to explain why PLA separates cleanly from TPU. **The official classification in 3.2.0 is the primary basis for this project**; this row adds colour, not evidence, and its mechanism claim is not officially corroborated. | **C** | [omni3d guide](https://omni3d.com/how-to-print-tpu-with-support-guide-for-easy-removal/); [Bambu forum thread](https://forum.bambulab.com/t/supporting-tpu-prints-with-pla-how-to-do-it/29300) |
| 3.2.4 | A Snapmaker blog reports combining TPU with PLA and with PETG in single U1 jobs, including one job with **"92 toolhead swaps without a single jam."** | **C** (Snapmaker marketing blog, not documentation) | [Snapmaker blog — TPU print ideas](https://www.snapmaker.com/blog/tpu-3d-print-ideas/) |
| 3.2.5 | Flat PLA/TPU interface peel strength, and the delta from Beam Interlocking, on a U1. | **T** | **No published figure found. Test T1/T2.** |

### 3.3 PETG + TPU

| # | Finding | Level | Source |
|---|---|---|---|
| 3.3.1 | **PETG + TPU is classified "+" (Strong Bonding)** in the official table — i.e. "naturally compatible, exhibiting high interfacial adhesion", printable "as load-bearing or structural parts without any additional bonding settings or process optimization". **Confirmed by direct visual transcription**, upgrading this from a summarised claim. | **O** [verified 2026-07-28] | §3.1.5 / [Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |
| 3.3.2 | **TPU + PETG** is nonetheless also listed among the Beam-Interlocking-capable combinations on the filament product page — an apparent redundancy, since the table already calls the pair strong. | **O** [verified 2026-07-28] | [TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) |
| 3.3.3 | Whether Beam Interlocking measurably *adds* strength to an already-strong PETG/TPU bond, or only adds print time and risk. | **T** | **Unresolved in official sources. Test T3/T4 — this is the most interesting single question in the matrix.** |
| 3.3.4 | PETG and TPU print at very different bed temperatures (§4), which constrains the shared first layer. | **T** | Deduced from official per-material ranges; not stated as a combined constraint anywhere we found. |
| 3.3.5 | **PETG + TPU is explicitly co-printable**, verbatim from the Top Cover note: *"**PETG can be printed together with PLA or TPU**; in these cases, external circulation mode will be enabled to exhaust heat from the chamber."* This is stated for the top-cover configuration; it is the only official statement found that names a rigid+TPU pair as printable **in the same job**. | **O** [verified 2026-07-28] | [Top Cover for Snapmaker U1](https://us.snapmaker.com/products/top-cover-for-snapmaker-u1), Note [1] |

### 3.4 ABS/ASA + TPU

| # | Finding | Level | Source |
|---|---|---|---|
| 3.4.1 | ABS and ASA require the **top cover** on the U1. | **O** [verified 2026-07-28] | [U1 specs](https://www.snapmaker.com/snapmaker-u1/specs) |
| 3.4.2 | **Correction to the first pass.** ABS + TPU and ASA + TPU **are** officially classified — both **"–" (Bondable)** in the adhesion table. The first pass recorded them as absent from official material; that was wrong and is retracted. | **O** [verified 2026-07-28] | §3.1.5 |
| 3.4.3 | **They cannot be printed in the same job — officially, verbatim:** *"**High-temperature filaments, such as ABS, ASA, PC, and PA, cannot be printed at the same time as low-temperature filaments, such as PLA, TPU, and PVA.** PETG can be printed together with PLA or TPU; in these cases, external circulation mode will be enabled to exhaust heat from the chamber."* | **O** [verified 2026-07-28] | [Top Cover for Snapmaker U1](https://us.snapmaker.com/products/top-cover-for-snapmaker-u1), Note [1] |
| 3.4.3b | The mechanism is the top cover's two mutually-exclusive thermal-management modes: **internal circulation** retains heat (chamber up to 50 °C) for ABS/ASA/PA/PC; **external circulation** actively exhausts heat for PLA/TPU/PVA. Snapmaker Orca matches each filament to a mode automatically. One print cannot run both modes. | **O** [verified 2026-07-28] | same, "Filament-Adaptive Thermal Management" / "Passive Heat Retention" / "Efficient Heat Exhaust Cooling" |
| 3.4.4 | What genuinely remains absent is a **tested combined process workflow** — no ABS/ASA-with-TPU recipe, temperatures, or interface settings exist, and Snapmaker's TPU co-printing list (PLA, PETG, PA, PET, TPU 95A) does not include ABS or ASA. | **O (absence of a process recipe)** [checked 2026-07-28] | [TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) |
| 3.4.5 | Consistent with 3.4.3b, the prime-tower guide advises an **enclosure and reduced cooling** for ABS/ASA/PA — the opposite of TPU's documented cooling-fan-ON requirement. | **O** [verified 2026-07-28] | [U1 Prime Tower Collapse](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/prime_tower_collapse), Strategy 3 Step 3 |

> **Decision: ABS/ASA + TPU stays OUT of the eight-print matrix. The accurate reasons are:**
>
> 1. **The pairs ARE officially classified — both "–" (Bondable)** in the adhesion table.
>    Any claim that they lack an official pairing classification is wrong and is retracted.
> 2. **No published combined process recipe** exists for printing them together (3.4.4).
> 3. **Their documented thermal/cooling requirements are incompatible**, and Snapmaker states
>    plainly that high-temperature and low-temperature filaments **cannot be printed at the
>    same time** (3.4.3, 3.4.3b).
> 4. Covering them would require a **separately resourced top-cover phase** with the hardware
>    fitted, which this project does not assume.
>
> Point 3 is not a scheduling inconvenience — it means an ABS/ASA + TPU job is outside the
> machine's documented operating envelope, whatever the adhesion table says about the
> interface.

### 3.5 TPU as / with support interfaces

| # | Finding | Level | Source |
|---|---|---|---|
| 3.5.0 | **Upgraded on re-verification.** The guide now states verbatim: *"We'll use two materials with low adhesion to each other, one for the model and the other for the support or support interface. Choose materials that do not bond strongly with each other. It makes the supports easier to remove while giving you a cleaner, smoother supported surface.* **PLA with PETG and PLA with TPU are two common and practical combinations.**" **PLA + TPU as an easy-removal support pairing is therefore officially acknowledged**, not merely community-reported. | **O** [verified 2026-07-28] | [Using a Different Filament for Support (PLA and PETG)](https://wiki.snapmaker.com/en/snapmaker_u1/printing_guides/pla_and_petg) (wiki page last edited 2026-07-01) |
| 3.5.0b | **What 3.5.0 does NOT establish.** The guide names PLA+TPU as a pairing only. It does not state **which material is the model and which is the support**, and every numeric value in the guide is given for **PLA/PETG**. Direction, temperatures, Z-distance, interface spacing, interface layers, pattern, and resulting surface quality **for a TPU interface are unstated**. | **O (absence)** [checked 2026-07-28] | same |
| 3.5.1 | The guide's structural advice: a support has a **base** and an **interface**, each printable in a different filament; because PETG and PLA need different bed temperatures, print the support **base** in the same material as the model and use the dissimilar material **only for the support interface**. | **O** [verified 2026-07-28] | same |
| 3.5.2 | **PLA/PETG numeric recipe — explicitly scoped to PLA/PETG:** Top Z distance **0**; support base pattern **Rectilinear**; **Top interface layers = 3**; interface pattern **Rectilinear Interlaced**; **top and bottom interface spacing = 0**. Filament values: PLA **230 °C**; PETG **265 °C**, bed **65 °C**, **max volumetric speed 10 mm³/s**. **These values are not validated for TPU and must not be presented as a TPU recipe.** | **O** [verified 2026-07-28] | same |
| 3.5.2b | The guide warns that moisture in the **support** material causes the two materials to "bond either too tightly or not enough, causing issues like support marks or sagging", and singles out **PETG and TPU** as absorbing moisture more easily. | **O** [verified 2026-07-28] | same |
| 3.5.3 | Weak-adhesion pairs are officially framed as good supports because low adhesion allows "easy and clean support removal" and "higher-quality bottom surfaces and finer detail". | **O** [verified 2026-07-28] | [Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |
| 3.5.4 | A filament vendor reports **PLA supports break away cleanly from a TPU surface**, whereas **TPU-on-TPU supports can fuse together**. Directionally consistent with 3.5.0, but the *direction* claim is still only the vendor's. | **C** (vendor testing) | [Siraya Tech — Fixing TPU jams on Snapmaker U1](https://siraya.tech/blogs/news/fixing-tpu-jams-on-snapmaker-u1-professional-settings-for-stable-24h-flexible-printing) |
| 3.5.5 | Whether **TPU as the support interface under a PLA part** releases cleanly, and what Z-distance / interface spacing / interface layers it needs on a U1. | **T** | The pairing is official (3.5.0); **this direction and its settings are not**. Tests T5/T6. |
| 3.5.7 | Snapmaker has also published a video guide, "Using a Different Filament for Support" (Snapmaker channel, ~3 weeks before 2026-07-28). Its transcript was **not** read in this pass. | **unread** | Listed so the gap is visible; may contain TPU-direction guidance. |
| 3.5.6 | Reported Snapmaker Orca **Beta 2.3.0** behaviour: the support-interface material is applied only to supports touching the build plate; supports growing **from the model** print their interface in the base support material instead. | **C** (single user report, version-specific, no staff reply in the excerpt read) | [Snapmaker forum thread 41686](https://forum.snapmaker.com/t/u1-multi-material-support-interface-layer/41686) |

> 3.5.6 matters more than its evidence level suggests: if it reproduces on the Orca build
> we test with, **every model-borne support in tests T5/T6 is invalid** unless the model is
> designed so all supports start on the plate. The matrix builds that in as a
> pre-condition check.

### 3.6 TPU 95A + TPU 90A

| # | Finding | Level | Source |
|---|---|---|---|
| 3.6.1 | Snapmaker TPU 90A is stated to co-print with **TPU 95A**. | **O** [verified 2026-07-28] | [TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) |
| 3.6.2 | Documentation framing (stronger than the marketing copy): **95A HF** is "stiffer, supports higher print speeds and is generally easier to work with"; **90A** is "softer and more elastic, making it more challenging to print". | **O** [verified 2026-07-28] | [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) (00:44–01:00) |
| 3.6.2b | The adhesion table's diagonal is "/" (same material), so it says **nothing** about TPU-grade-to-TPU-grade bonding. No official statement on 95A↔90A interfacial strength was found. | **O (absence)** [checked 2026-07-28] | §3.1.5 |
| 3.6.3 | A user reports running Bambu High-Flow TPU 95A on the U1 with better-than-expected results. | **C** (single report) | [Snapmaker forum thread 40540](https://forum.snapmaker.com/t/first-u1-tpu-95hf-multicolor-print/40540) |
| 3.6.4 | Two TPU grades bond to each other well (same polymer family) but a **soft prime/wipe tower may not be self-supporting**, and toolchange behaviour with two flexibles loaded is unknown to us. | **T** | Tests T7/T8. |

---

## 4. Flexible-material process findings

### 4.1 Official TPU 90A parameters (Snapmaker)

All from the [Snapmaker TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) — **O** [verified 2026-07-28]:

| Parameter | Official value |
|---|---|
| Shore hardness | 90A |
| Nozzle temperature | **210–240 °C** |
| Bed temperature | **25–60 °C** |
| Print speed | **30–50 mm/s** |
| Drying | **70 °C for 6 hours** ("TPU is extremely hygroscopic and must be dried before use") |
| Cooling fan | **ON** |
| 0.2 mm nozzle | **Not recommended** |
| Loading | **"The filament must be loaded and unloaded manually. Do not use the automatic filament feeder."** |
| U1 profiles | "Optimized profiles built into Snapmaker Orca" |

**Corroborated on re-verification (2026-07-28).** The TPU-specific guide independently
states that TPU "is highly hygroscopic and must be stored in a sealed container… you should
dry it before use and keep it sealed throughout the entire print", and points at the
SnapDryer workflow. It also gives symptom-directed quality fixes, all **O**:

- **Stringing / colour bleeding** — "often caused by moisture in the filament which creates
  bubbles when heated in the hotend", so replace or thoroughly dry the filament first; if
  the filament is fine, lower the printing temperature in the filament profile; optionally
  optimise small or isolated model features to reduce travel moves.
- **Obvious layer lines** — reduce the **outer wall printing speed** to minimise extrusion
  fluctuations, and/or increase **part cooling fan speed** so outer walls solidify faster,
  "reducing deformation caused by nozzle drag".

> **⚠ Direct conflict between two Snapmaker surfaces.** The product page says **30–50 mm/s**;
> the Snapmaker *blog* (§3.2.4) reports a successful U1 TPU print at **270 mm/s infill /
> 200 mm/s walls / 500 mm/s travel**, with drying at **~55 °C for 4–6 h** rather than 70 °C
> for 6 h. These cannot both be "the recommendation".
> **Resolution rule for this project:** the **product page / documentation wins**; the blog is
> treated as **C**. The tutorial must not present blog speeds as recommended settings.
> This conflict is itself a strong article beat — see the topic framework.

### 4.2 Manual vs automatic TPU loading

| # | Finding | Level | Source |
|---|---|---|---|
| 4.2.1 | "For flexible filaments such as TPU, please follow the instructions for **Manual Loading**." | **O** [verified 2026-07-28] | [Manual Loading (Wiki)](https://wiki.snapmaker.com/en/snapmaker_u1/manual_loading) |
| 4.2.2 | Trim the filament end at **~45°** with diagonal cutters — this "reduces feeding resistance, thus enhancing the success rate." | **O** [verified 2026-07-28] | same |
| 4.2.3 | Auto Loading must be **disabled per toolhead**: Settings → Print Preferences → Auto Loading. | **O** [verified 2026-07-28] | same |
| 4.2.4 | Press the circular latch at the end of the corresponding feeder and unplug the tube connected to the target toolhead. Then: Loading Mode → Filament Loading Guide → Switch to Manual Loading. | **O** [verified 2026-07-28] | same |
| 4.2.5 | "It is recommended to unplug the tube from the top of the toolhead, expose part of filament, and push it downward manually to ensure proper contact with the extrusion gears." | **O** [verified 2026-07-28] | same |
| 4.2.6 | Flexible filaments also require **Manual Unloading**: Filament page → Unloading Mode → select toolheads → Unload → Confirm; once at temperature, "manually pull the filament outward to assist with unloading". | **O** [verified 2026-07-28] | [Manual Unloading (Wiki)](https://wiki.snapmaker.com/en/snapmaker_u1/flexible_filament_unloading) (last edited 2026-07-27) |
| 4.2.6b | **New on re-verification, and unambiguous:** "**TPU filament cannot be used with the filament feeder. Please pull the filament out directly from the filament tube.**" The on-screen unloading guide is noted as "for illustrative purposes only". | **O** [verified 2026-07-28] | same |
| 4.2.6c | Filament identity: Snapmaker filament with RFID is recognised automatically; **third-party filament or Snapmaker filament without RFID must be entered manually**. When feeding from the SnapDryer the filament information is likewise "won't be detected automatically so you'll need to enter it manually". | **O** [verified 2026-07-28] | [Manual Loading](https://wiki.snapmaker.com/en/snapmaker_u1/manual_loading); [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) (01:50) |
| 4.2.7 | 85A TPU reportedly loads but "may need manual help during loading by feeding into the toolhead by hand". | **C** (third-party review) | [fauxhammer U1 review](https://www.fauxhammer.com/reviews/snapmaker-u1-review-the-multi-colour-printer-that-actually-moves-the-market-forward/) |

> **The single most under-communicated official fact we found:** flexible filament on the U1
> is a **manual load and manual unload**, per-toolhead, with Auto Loading switched off. A
> novice who leaves Auto Loading on and walks away is the archetypal first TPU failure. This
> should open the tutorial.

### 4.3 Filament-path resistance

| # | Finding | Level | Source |
|---|---|---|---|
| 4.3.1 | The 45° cut is officially justified as **reducing feeding resistance** (4.2.2) — Snapmaker names path resistance as the failure mechanism. | **O** [verified 2026-07-28] | [Manual Loading](https://wiki.snapmaker.com/en/snapmaker_u1/manual_loading) |
| 4.3.2 | A vendor states the U1's PTFE tubing has a larger-than-standard internal diameter, "which significantly reduces friction", letting flexibles slide from the back of the machine to the extruder "without binding". | **C** (vendor claim, no dimension given) | [Siraya Tech](https://siraya.tech/blogs/news/fixing-tpu-jams-on-snapmaker-u1-professional-settings-for-stable-24h-flexible-printing) |
| 4.3.3 | **Upgraded C → O.** Snapmaker's own TPU guide instructs: "slightly loosen the screws on the side of the toolhead to reduce feeding resistance", alongside reducing print speed and lowering toolchange retraction length. The first pass carried this as a vendor-only claim and advised against repeating it — **that framing is retracted**; it is official Snapmaker guidance. | **O** [verified 2026-07-28] | [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) (05:11–05:17) |
| 4.3.4 | **Upgraded T → O.** "TPU is highly sensitive to resistance along the extrusion path and even small changes can cause pressure fluctuations inside the nozzle. When the resistance becomes too high and extrusion drops you may see gaps or dents. Once the pressure builds up the filament may suddenly surge out creating bumps on the surface." Named checks: "whether the filament tube is bent or loose, whether the outlet of the dryer box is too tight, and whether the spool holder rotates smoothly." | **O** [verified 2026-07-28] | same (07:06–07:39) |
| 4.3.5 | "TPU tends to build up inside the nozzle causing partial clogs that further reduce extrusion stability." Official mitigations once the external path is confirmed clear: increase the **purge volume** under Multimaterial > Prime Tower, and increase **skirt loops** under Other > Skirt "so the nozzle performs continuous extrusion before printing the model". | **O** [verified 2026-07-28] | same (07:39–08:03) |
| 4.3.6 | How much any of these changes measurably alter load success or extrusion stability on a given machine. | **T** | Not quantified anywhere. The matrix records the path setup per test so the variable is *controlled*, not measured. |

> **Note on 4.3.3.** Loosening the toolhead side screws is now known to be **Snapmaker's own
> instruction**, not folklore. This project still keeps it **out of the eight-print matrix**
> — it is a hardware adjustment that would confound every subsequent run and cannot be
> reverted precisely. That is a protocol choice, not a safety objection.

### 4.4 Toolchange retraction

| # | Finding | Level | Source |
|---|---|---|---|
| 4.4.0 | **The direction is now official.** "Because TPU is difficult to control during feeding and retraction, excessive resistance can cause the filament to build up inside the print head or even squeeze out through small gaps. If this happens you can reduce the print speed under 'Speed' in Orca and **lower the toolchange retraction length under 'Setting Overrides' in the filament profile**." | **O** [verified 2026-07-28] | [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) (04:36–05:11) |
| 4.4.0b | **No value is published.** Snapmaker gives the direction ("lower it") and the exact UI location (filament profile → Setting Overrides), but **states no number, no range, and no default**. It is also framed as a **remedial** step for a specific symptom, not a routine pre-emptive change. | **O (absence)** [checked 2026-07-28] | same |
| 4.4.1 | A vendor states the U1/Orca default "Retraction at Switch" is **10 mm** and recommends **0–4 mm**, because TPU buckles and "bird-nest[s]" around the extruder gears during a swap. **The 10 mm default and the 0–4 mm range remain vendor claims — neither is corroborated by any Snapmaker source, and the shipped value has still not been read by us.** | **C** (vendor testing) | [Siraya Tech](https://siraya.tech/blogs/news/fixing-tpu-jams-on-snapmaker-u1-professional-settings-for-stable-24h-flexible-printing) |
| 4.4.2 | A Snapmaker blog suggests keeping retraction distance low, "around **0.8 – 2.0 mm** for direct drive". Note this is *retraction distance*, a different setting from *toolchange retraction length*. | **C** (Snapmaker blog, not documentation) | [Snapmaker blog](https://www.snapmaker.com/blog/tpu-3d-print-ideas/) |
| 4.4.3 | The actual shipped toolchange-retraction values in the Snapmaker Orca **TPU 95A HF** and **TPU 90A** profiles. | **T** | **Must be read out of Orca and recorded verbatim before any test runs** — pre-condition P5, and now also the input to the T8 pre-registration gate. |

> **What changed and what did not.** The *direction* (lower toolchange retraction for TPU)
> moved **C → O**. Every *number* is still **C** or unknown. "Set it to 0–4 mm" remains a
> vendor recommendation and must never be printed as a Snapmaker setting. Snapmaker frames
> the change as a fix for an observed symptom; presenting it as a default would misrepresent
> the source.

### 4.5 Dynamic Flow Calibration — **CORRECTED. Conflicting official guidance.**

> **This section replaces the first pass entirely.** The first pass treated Dynamic Flow
> Calibration (DFC) as mandatory after every filament change, **including for TPU**. That is
> **wrong for TPU jobs** and is retracted here.

#### 4.5.A The generic guidance (still current, still correct for rigid materials)

| # | Finding | Level | Source |
|---|---|---|---|
| 4.5.A1 | What it does: "Dynamic Flow Calibration… compensates for extrusion pressure lag during acceleration and deceleration. By adjusting flow in real time, it helps prevent blobbing, gaps, and inconsistencies, especially in prints with frequent speed changes or sharp details." | **O** [verified 2026-07-28] | [U1 FAQ — Flow Rate vs Dynamic Flow Calibration](https://wiki.snapmaker.com/en/FAQ/u1) |
| 4.5.A2 | Verbatim: "The results of dynamic flow calibration are stored in the firmware for the currently loaded filament. However, once the filament is unloaded, the calibration value will reset to the default K value. While the firmware includes pre-tested default K values for different filaments, **it is recommended to run a new dynamic flow calibration after changing filaments to ensure optimal print quality.** The process is fully automatic and very simple, so there's no need to worry." | **O** [verified 2026-07-28] | same |
| 4.5.A3 | "Dynamic Flow Calibration is recommended when: You switch to a different brand or type of filament · You print for the first time · The hot end has been replaced · The material has absorbed moisture, or its viscosity has changed · Issues such as over-extrusion, under-extrusion, or stringing occur." | **O** [verified 2026-07-28] | same |
| 4.5.A4 | **It is a per-job tick-box, not a separate wizard:** "On the main touchscreen, tap 'Start' to begin your print → tap 'Next' → In the 'Print Preferences' menu, **tick 'Dynamic Flow Calibration'** → tap 'Print'". | **O** [verified 2026-07-28] | same |
| 4.5.A5 | The generic guidance is **material-agnostic**: it names brand/type changes, moisture, and extrusion symptoms, but says nothing about flexibles. | **O (absence)** [checked 2026-07-28] | same |

#### 4.5.B The TPU-specific guidance — **controlling for any job involving TPU**

| # | Finding | Level | Source |
|---|---|---|---|
| 4.5.B1 | Verbatim, from Snapmaker's TPU-specific guide: **"Because TPU is soft and compressible it tends to expand and contract during extrusion. This makes dynamic flow calibration unreliable and can negatively affect print quality. Make sure this feature is turned off when starting a print job."** | **O** [verified 2026-07-28] | [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) — support article dated **2026-07-19**; embedded Snapmaker video published **2026-07-09**; quote at **03:40–03:56** of the official transcript |
| 4.5.B2 | Mechanically, "turned off" means **leaving the 'Dynamic Flow Calibration' box unticked in Print Preferences** when starting the job (4.5.A4). | **O (composition of two verified statements)** | 4.5.A4 + 4.5.B1 |

#### 4.5.C The conflict, stated plainly

| | Generic (4.5.A) | TPU-specific (4.5.B) |
|---|---|---|
| Instruction | Run DFC after changing filament | Turn DFC **off** before starting the job |
| Scope | All filaments, material-agnostic | TPU explicitly |
| Publication | U1 FAQ (undated section; DFC support article dated **2025-11-06**) | **2026-07-09 / 2026-07-19** |
| Stated reason | Restores per-filament K value after unload | TPU is soft and compressible; calibration is unreliable and can hurt quality |

**These two instructions are contradictory for a TPU job and are not merged here.**

#### 4.5.D Resolution rule adopted by this project

Applying §1.2 (newest + most material-specific wins):

- **Any job with TPU loaded in any toolhead → Dynamic Flow Calibration OFF.** The
  TPU-specific guide is controlling. This includes **every rigid-flexible job in this
  research**, because every one of them has TPU in at least one toolhead.
- **No TPU in the job → the generic guidance stands unchanged** (run DFC after a filament
  change, per 4.5.A2–A3).
- **Never restate the generic rule as if it covered TPU**, and never present the TPU rule as
  general calibration advice.
- **Unresolved and not guessed:** the guides do not say what to do on a **mixed** job where
  only some toolheads carry TPU. DFC is a single per-print tick-box (4.5.A4), so it cannot
  be enabled per toolhead. This project takes the conservative reading — **TPU anywhere in
  the job means the box stays unticked** — and labels that as **our policy choice**, not a
  Snapmaker instruction. Flag it to Snapmaker as an open documentation question.

| # | Finding | Level | Source |
|---|---|---|---|
| 4.5.D1 | Whether DFC-off measurably changes TPU surface quality versus DFC-on. | **T — and deliberately not tested.** | DFC is held **constant OFF** across all eight tests so it never becomes a hidden variable. Testing it would mean deliberately printing against current official TPU guidance. |
| 4.5.D2 | Older U1 material still lists DFC among routine per-filament steps. | **O (conflict recorded, not hidden)** | §4.5.C |

### 4.6 Prime / wipe tower with flexibles

| # | Finding | Level | Source |
|---|---|---|---|
| 4.6.1 | Wall type **Rib** "significantly improve[s] the tall tower's resistance to tipping and reduce[s] the risk of collapse caused by nozzle collisions". | **O** | [U1 Prime Tower Collapse](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/prime_tower_collapse) (already cited by Studio) |
| 4.6.2 | "**Rib Length:** Appropriately increasing this allows the tower to occupy a larger footprint on the build plate, making the base more stable." / "**Rib Width:** Do not use small values; ensure there is sufficient contact area between the outer wall and the internal infill to enhance overall strength." Also: adjust **Width** to keep the tower square, increase **Brim Width** for bed adhesion, increase **Purge Line Spacing** to add tower volume. | **O** [verified 2026-07-28] | same |
| 4.6.3 | **"When adhesion between different materials is poor (e.g., PLA + PETG), the entire tower is prone to layer separation (delamination) or breakage at the material interface. You can specify the filament used for the wipe tower shell."** | **O** [verified 2026-07-28] | same (Strategy 2) |
| 4.6.3b | The same guide instructs: **"Apply one corrective action at a time to accurately identify the root cause"**, and recommends timelapse for diagnosing tower failures. Snapmaker's own protocol advice matches this project's one-variable rule. | **O** [verified 2026-07-28] | same (Important Notes) |
| 4.6.4 | A user reports PLA printed above PETG on a prime tower had no adhesion and "just turn[ed] into spaghetti". | **C** | [Snapmaker forum thread 40432](https://forum.snapmaker.com/t/multimaterial-prime-tower-failed/40432) |
| 4.6.5 | Studio's existing tower safety rails: never auto-enable `wipe_tower_no_sparse_layers`; never auto-raise `wipe_tower_max_purge_speed` above **90 mm/s**. | **O** (verified in-repo + U1 doc) | [`U1_PRINT_PROFILE_RESEARCH.md`](U1_PRINT_PROFILE_RESEARCH.md), `backend/snapstudio_core/strategies.py` |
| 4.6.6 | **Upgraded T → O, and this is the single most useful new finding for the tower.** "**TPU wipe towers have weak layer-to-layer support and low rigidity, making them more likely to collapse when pulled or bumped.** If a collapse occurs you can increase the width and length of the tower ribs under 'Multimaterial'." | **O** [verified 2026-07-28] | [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) (06:13–06:28) |
| 4.6.7 | **Official single-spool tower shell technique, with TPU & PLA as the worked example:** "when printing with multiple materials the wipe tower is printed with **all involved materials by default**. If these materials don't adhere well to each other (**for example, TPU & PLA**) the vertical stability of the tower will be further reduced. In this case go to '**Filament for Features**' and **assign any single spool to the wipe tower**. This ensures the outer walls of the tower are always printed with the same material improving its structural stability." | **O** [verified 2026-07-28] | same (06:28–07:06) |
| 4.6.8 | Whether the single-spool tower shell is *necessary* for our specific coupons at our tower height, or merely available. | **T** | The matrix keeps the Orca default (tower printed with all involved materials) as the baseline and treats the single-spool shell as a documented **mitigation available only as a new test pair** — never applied mid-pair. |

> 4.6.3 is the bridge between "material choice" and "tower collapse": the tower is a
> miniature version of the same bonded interface as the part. That is a genuinely
> explanatory idea for the tutorial, and it is officially sourced.

### 4.7 Beam Interlocking

| # | Finding | Level | Source |
|---|---|---|---|
| 4.7.1 | Beam Interlocking is available in Snapmaker Orca and mechanically stitches two materials at their boundary, strengthening weak chemical adhesion — explicitly named for **rigid–flexible** combinations. | **O** [verified 2026-07-28] | [Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |
| 4.7.2 | Parameter set (upstream OrcaSlicer documentation): **interlocking beam width**, **interlocking direction**, **interlocking beam layers**, **interlocking depth** (in cells), **interlocking boundary avoidance** (in cells). | **O** (OrcaSlicer docs — upstream, not Snapmaker) | [OrcaSlicer — multimaterial advanced](https://www.orcaslicer.com/wiki/print_settings/multimaterial/multimaterial_settings_advanced) |
| 4.7.3 | Interlocking depth is "the distance from the boundary between filaments to generate interlocking structure, measured in cells"; **"too few cells will result in poor adhesion."** Boundary avoidance is the distance from the model's outside where interlocking is not generated. | **O** (OrcaSlicer docs) | same |
| 4.7.4 | **Recommended Beam Interlocking values for PLA/TPU or PETG/TPU on a U1.** | **T** | **No published values found from Snapmaker or upstream.** Tests T2/T4 use the shipped Orca defaults **unchanged** and record them verbatim. We do not invent a tuned recipe. |
| 4.7.5 | Bambu publishes a soft-and-hard multi-material guide that may contain adjacent-ecosystem guidance. | **unread** | [Bambu H2 soft/hard guide](https://wiki.bambulab.com/en/h2/manual/soft-and-hard-filament-multi-material-printing-guide) — fetch returned HTTP 402; **not read**, listed for completeness only. |

### 4.8 Nozzle contamination and cold pulls

| # | Finding | Level | Source |
|---|---|---|---|
| 4.8.1 | Official U1 partial-clog options, verbatim: "**Heat Creep/Flow Check** — Use the touchscreen controls to raise the nozzle temperature slightly above the filament's standard print temp. Load/extrude filament. The purge line should fall straight and consistent. If it has curls, inconsistency or it comes out thin, use next step." | **O** [verified 2026-07-28] | [U1 filament not extruding](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/filament_not_extruding) |
| 4.8.2 | **RETRACTED — claim removed.** The first pass stated that flame / thermal burnout is *prohibited* on the U1 because the hot end is an interference-fit assembly, attributed to this page. On re-verification **that statement could not be found** on the U1 "filament not extruding" page (whose only Important Note concerns delicate extruder wiring) **nor on the U1 hot end replacement guide**. The claim is **withdrawn as an official U1 statement** and must not be republished as one. | **removed** [checked 2026-07-28] | — |
| 4.8.2b | Our own protocol position, stated as ours: **this project uses no flame or torch method on any hot end**, and the tutorial will not describe one. That is a protocol choice, not a quoted Snapmaker prohibition. | **project policy** | — |
| 4.8.3 | The official second option is named "**Needle/Cold Pull**": "Use a nozzle cleaning needle (acupuncture needle) to break up the blockage inside the nozzle, then manually push filament through. Repeat this process until the extrusion comes out straight and stable. Please reach out to support if you need additional information about Cold Pull method." Snapmaker therefore **does** name cold pull — while referring users to support for its detail rather than publishing the procedure. | **O** [verified 2026-07-28] | same |
| 4.8.4 | For a **full clog**, the page routes users to its Scenario 1 troubleshooting flow rather than a standalone recipe. | **O** [verified 2026-07-28] | same |
| 4.8.5 | TPU residue is an official concern in its own right — see §4.3.5 (TPU builds up inside the nozzle; purge volume and skirt loops are the published mitigations). | **O** [verified 2026-07-28] | [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) |
| 4.8.6 | Cross-material residue from **reusing one toolhead for different materials between tests**. | **T** | Handled procedurally: fixed toolhead↔material assignment, no mid-matrix reassignment. |

### 4.9 Toolhead offset / calibration failures

| # | Finding | Level | Source |
|---|---|---|---|
| 4.9.1 | Verbatim: "The calibration will take about **15 to 20 minutes**. Once calibration is done, there's no need to repeat it before every print." | **O** [verified 2026-07-28] | [U1 FAQ](https://wiki.snapmaker.com/en/FAQ/u1) |
| 4.9.2 | Triggers listed for multi-toolhead offset calibration include: **the hot end has been replaced**; **the nozzle scrapes or collides with components such as the heated bed**; **layer shifting occurs during multi-toolhead printing**. | **O** [verified 2026-07-28] | same |
| 4.9.3 | Misalignment guide steps: **Step 1** check nozzles for residual filament; **Step 2** check whether the hotend is loose; **Step 3** check the copper-plate ↔ sensor gap; **Step 4** check steel-ball lubrication — "take the white lithium grease from the included tool kit and apply an even layer of appropriate amount onto the steel balls". | **O** [verified 2026-07-28] | [U1 multi-color misalignment](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/multi-color_misalignment) (last edited 2026-02-25) |
| 4.9.3b | **Numeric value now confirmed verbatim**, closing the outstanding item: "Under normal conditions, the distance between the hotend copper plate and the calibration sensor **should be within 0.1–0.4 mm**. You can use a sheet of standard A4 paper for a quick approximation. If the gap is too large, use a **H2.0 hex key** to loosen the two screws securing the hotend, push the hotend upwards, and then re-tighten the screws." | **O** [verified 2026-07-28] | same |
| 4.9.3c | Recalibration cadence, verbatim: "Perform calibration whenever you **move the printer, replace the toolhead or hotend, or carry out major maintenance**." Guide also advises cleaning nozzles before calibration and lubricating moving parts quarterly. | **O** [verified 2026-07-28] | same |
| 4.9.4 | Snapmaker's TPU guide routes layer shifting to the same place: "If layer shifting occurs, follow the multi-toolhead offset calibration tutorial to recalibrate." | **O** [verified 2026-07-28] | [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) (08:18) |
| 4.9.5 | If the first layer is rough or material builds up and automatic levelling does not help, run **manual levelling**. | **O** [verified 2026-07-28] | same (08:26) |
| 4.9.6 | Offset error appears **differently on a soft material**: a misaligned rigid/flexible seam may look like "bad adhesion" rather than "misalignment", because TPU deforms instead of showing a crisp step. | **T** | Untested hypothesis. Matrix requires a calibration-state record per test precisely so this cannot silently contaminate a result. |

---

## 5. What Snapmaker Studio can truthfully claim today

Audited directly from the source on branch `research/u1-rigid-flexible-tutorial`.

### 5.1 Present and real

| Capability | Where | What it actually does |
|---|---|---|
| **Multi-Material Doctor** | `backend/snapstudio_core/mm_doctor.py` | Compares the design's **colour/filament count** against the U1's toolhead count (real count when a printer is connected, else 4); flags painted regions with a single filament; folds in filament-array/purge inconsistencies; emits plain-language findings + fixes. |
| **Toolhead-Fit Intelligence** | `toolhead_fit.py` | Same colours-vs-toolheads question fused with a connected printer's real toolhead count. Never fabricates swap counts or times. |
| **Project Doctor** | `doctor.py`, `bed_fit.py` | 3MF/STL verdict (READY / REPAIRABLE / HIGH_RISK / CONVERTIBLE) + 0–100 score; bed fit and out-of-bounds; reserves prime/wipe-tower clearance when the job is multi-material. |
| **Print Strategies** | `strategies.py`, [`docs/PRINT_STRATEGIES.md`](../PRINT_STRATEGIES.md) | Five intent-based prime/wipe-tower recommendation bundles with the U1 safety rails baked in (never auto-enable no-sparse-layers; never auto-exceed 90 mm/s). Recommendation only — Orca slices. |
| **Filament metadata handling** | `filaments.py`, `preserve.py`, `profile.py` | Conforms per-filament arrays and purge structures to the filament count (the Orca "Customized Preset" trap); protects `filament_colour`, `filament_type`, `filament_settings_id` from being overwritten. |
| **Material type is parsed** | `canonical.py`, `intelligence.py`, `source_compatibility.py`, `print_failure.py` | `filament_type` is read and surfaced (e.g. `["PLA","PETG"]`). |
| **One material-aware hint exists** | `quality_evidence.py` | If the symptom is stringing/oozing/temperature-related and the file contains PETG or TPU, it notes those "string more; tune retraction/temperature." |
| **Community Knowledge** | `community_knowledge.py` | Six curated recurring U1 issues (out-of-bounds, prime tower, >4 colours, first-layer adhesion, Klipper errors, Customized Preset) matched to symptom text. |

### 5.2 Honestly absent (the gap this research defines)

Studio today has **no** notion of:

- Shore hardness, or flexible vs rigid as a **material property**.
- **Material-pair** compatibility or interfacial adhesion (it counts colours; it does not know PLA-next-to-TPU is a different problem from PLA-next-to-PLA).
- Beam Interlocking — the word does not appear anywhere in the codebase.
- Support-**interface material** assignment, or the official PLA/PETG support recipe.
- Manual vs automatic **loading mode** for flexibles.
- **Drying** state or requirements.
- Dynamic Flow Calibration or toolhead-offset calibration state as an input to advice —
  and in particular **no notion that DFC must be OFF for TPU jobs** (§4.5).
- Wipe-tower **shell filament assignment** (the official single-spool technique, §4.6.7).
- TPU-specific entries in the Community Knowledge base (none of the six mention TPU).

**Therefore Studio cannot today claim any rigid-flexible capability.** It can claim, truthfully:
*"Studio checks whether your colours fit your toolheads, whether the file's filament metadata
is consistent, whether the model fits the plate with tower clearance, and recommends a
prime/wipe-tower strategy for review in Orca."* Nothing about material compatibility.

---

## 6. Top community pain points (ranked by how often they recur and how badly they bite)

0. **Dynamic Flow Calibration left ON for a TPU job.** The generic U1 guidance says run it
   after a filament change; the TPU-specific guide says turn it off. A user following the
   older, more prominent advice is calibrating against official TPU guidance without knowing
   it (§4.5). This is now the **top** pain point, and it is the reason this corrective pass
   exists.
1. **Flexible filament auto-load failure / gear bird-nesting on toolchange.** Officially the answer is manual load + manual unload, and TPU "cannot be used with the filament feeder" (§4.2); lowering toolchange retraction length is the official remedial step, with no published value (§4.4). Users hit this on their very first TPU job.
2. **Prime/wipe tower failure on dissimilar materials — and specifically on TPU.** Officially acknowledged twice over: poor inter-material adhesion delaminates the tower at the material interface (§4.6.3), and "TPU wipe towers have weak layer-to-layer support and low rigidity" (§4.6.6). Snapmaker's own example of a badly-adhering tower pair is **TPU & PLA** (§4.6.7).
3. **Support interface printed in the wrong material** (reported Orca Beta 2.3.0 behaviour for supports growing from the model, §3.5.6) — the print looks like a settings mistake when it may be a slicer behaviour.
4. **Multi-colour misalignment blamed on the model.** Offset calibration drift from moving the machine, swapping a hot end, or unlubricated steel balls (§4.9) presents as "my multi-material seam is bad".
5. **Conflicting speed/drying advice for TPU** between Snapmaker's own product page and its own blog (§4.1) — a novice cannot tell which to follow.
6. **Nozzle clogs and TPU residue.** Snapmaker publishes a Heat-Creep/Flow-Check step and a "Needle/Cold Pull" step, and separately warns that TPU builds up inside the nozzle (§4.3.5, §4.8). Torch/flame methods circulate widely in the hobby; this project does not use or describe them (§4.8.2b).
7. **Sub-90A TPU treated as supported.** It is officially still under validation (§2.5); community posts about 85A blur that line.

---

## 7. What must NOT be claimed

- ❌ Any statement that a material pair "will print" or "will hold". The official table
  classifies **bonding tendency**, not outcome. "+" is not a guarantee and "–" is not a
  failure prediction.
- ❌ **Running Dynamic Flow Calibration on a TPU job**, or repeating the generic "run it
  after every filament change" line in any TPU context (§4.5).
- ❌ Presenting the TPU DFC-off rule as **general** calibration advice for rigid materials.
- ❌ Beam Interlocking values for TPU pairs — none are published; defaults only, recorded verbatim.
- ❌ The 0–4 mm toolchange-retraction figure as a Snapmaker setting. Snapmaker gives the
  **direction only** (§4.4.0); the number is a vendor claim and the shipped default is still unread.
- ❌ The PLA/PETG numeric support recipe (Top Z 0, 3 interface layers, spacing 0, 230/265 °C,
  10 mm³/s) as **validated for TPU**. It is published for PLA/PETG (§3.5.2).
- ❌ Blog-sourced TPU speeds (270/200/500 mm/s) as recommended settings — the product page's 30–50 mm/s is the documented figure (§4.1).
- ❌ TPU below 90A as supported.
- ❌ ABS/ASA + TPU **process** recommendations. Their adhesion classification "–" *is*
  official (§3.4.2), and Snapmaker states high-temperature filaments **cannot be printed at
  the same time** as TPU (§3.4.3). Never write that the pairing is unclassified, and never
  infer a workflow for it.
- ❌ **That flame/thermal burnout is officially prohibited on the U1** — that claim was
  withdrawn on re-verification (§4.8.2). Do not republish it as a Snapmaker statement.
- ❌ That Studio's structural/metadata validation predicts physical success. It does not, and this document does not change that.

---

## 8. Verification status

### 8.1 Cleared on 2026-07-28 (re-opened in a browser, read on the live page)

| Source | Outcome |
|---|---|
| [U1 Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) | **Confirmed + adhesion table transcribed visually** (§3.1.5). PETG+TPU "+" confirmed; ABS/ASA+TPU found to be classified after all. |
| [Tips for Reliable TPU Printing](https://support.snapmaker.com/hc/en-us/articles/42075056736023-Tips-for-Reliable-TPU-Printing) | **Newly found.** Support page is a video embed with no text body; the official transcript was read in full. Source of §4.5.B, §4.3.3–4.3.5, §4.4.0, §4.6.6–4.6.7. |
| [Using a Different Filament for Support (PLA and PETG)](https://wiki.snapmaker.com/en/snapmaker_u1/printing_guides/pla_and_petg) | **Confirmed, and now names PLA+TPU** as a common practical low-adhesion combination (§3.5.0). |
| [Manual Loading](https://wiki.snapmaker.com/en/snapmaker_u1/manual_loading) | Confirmed verbatim. |
| [Manual Unloading](https://wiki.snapmaker.com/en/snapmaker_u1/flexible_filament_unloading) | Confirmed + new: TPU cannot use the filament feeder (§4.2.6b). |
| [U1 Prime Tower Collapse](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/prime_tower_collapse) | Confirmed verbatim, incl. the one-change-at-a-time instruction (§4.6.3b). |
| [U1 FAQ](https://wiki.snapmaker.com/en/FAQ/u1) | Confirmed the generic DFC guidance verbatim (§4.5.A) and offset-calibration timing (§4.9.1–4.9.2). |
| [U1 filament not extruding](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/filament_not_extruding) | Confirmed Heat-Creep/Flow-Check and Needle/Cold Pull. **Flame-prohibition claim not found → withdrawn** (§4.8.2). |
| [U1 hot end replacement guide](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/hot_end_replacement_guide) | Checked as a second location for the flame claim — **not present**. |
| [U1 multi-color misalignment](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/multi-color_misalignment) | **Fully confirmed, including the 0.1–0.4 mm gap and H2.0 procedure verbatim** (§4.9.3–4.9.3c). Previously outstanding — now closed. |
| [Top Cover for Snapmaker U1](https://us.snapmaker.com/products/top-cover-for-snapmaker-u1) | **Newly read.** Source of the high/low-temperature simultaneous-printing rule (§3.4.3), the two circulation modes (§3.4.3b), the PETG-with-PLA-or-TPU allowance (§3.3.5), and the with-cover material list (§2.3). |
| [TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) | Confirmed (§4.1). |

### 8.2 Still outstanding

| Item | Action | Blocks |
|---|---|---|
| §2.2 and §2.4 — base and hardened-steel material lists | **The Snapmaker U1 specs page was not re-opened.** Re-read it and date both rows, or re-source them. §2.3 is already independently confirmed from the Top Cover page. | Publishing the base / CF-GF material lists. |
| §4.4.3 — shipped toolchange-retraction values for **TPU 95A HF** and **TPU 90A** | Read out of Snapmaker Orca; record verbatim per filament. | Tests T7/T8 **and** the T8 pre-registration gate. |
| §4.7.4 — Beam Interlocking defaults | Read out of Snapmaker Orca; record verbatim. | Tests T2, T4. |
| §3.5.6 — support-interface behaviour on the Orca build under test | Reproduce or fail to reproduce. | Tests T5, T6. |
| §3.5.7 — Snapmaker video "Using a Different Filament for Support" | Read its transcript; it may state the PLA/TPU **direction** we currently lack. | Sharpening T5/T6 hypotheses (does not block). |
| §4.7.5 — Bambu soft/hard guide | Fetch by other means, or drop the reference. | Nothing — optional. |
| DFC on **mixed** jobs (some toolheads TPU, some not) | Ask Snapmaker; currently resolved by our own conservative policy (§4.5.D). | Nothing — but must stay labelled as our policy. |

---

## 9. Related documents

- [`U1_RIGID_FLEXIBLE_TEST_MATRIX.md`](../testing/U1_RIGID_FLEXIBLE_TEST_MATRIX.md) — the eight controlled prints that convert **T** findings into evidence.
- [`U1_RIGID_FLEXIBLE_TOPIC_FRAMEWORK.md`](../tutorials/U1_RIGID_FLEXIBLE_TOPIC_FRAMEWORK.md) — proposed article structure and positioning.
- [`FLEXIBLE_MATERIAL_DOCTOR_PROPOSAL.md`](../product/FLEXIBLE_MATERIAL_DOCTOR_PROPOSAL.md) — whether and how this becomes a product surface without becoming a slicer.
- [`U1_PRINT_PROFILE_RESEARCH.md`](U1_PRINT_PROFILE_RESEARCH.md) — the prime/wipe-tower research this builds on.
