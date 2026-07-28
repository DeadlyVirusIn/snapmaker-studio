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

### 1.1 Source-access note (verification debt — read before publishing anything)

Two official domains could not be fetched directly during this research pass:

- `wiki.snapmaker.com` renders client-side; a direct fetch returns only the page title.
- `support.snapmaker.com` returned **HTTP 403** to a direct fetch.

Their content was obtained through **search-engine extraction of those same official
pages**. The findings are therefore attributed to the official source, but the exact
wording has **not** been re-read on the live page by this pass.

**Before any of this is published externally or wired into product copy, every O-tagged
item below must be re-opened in a browser on the cited URL and confirmed verbatim.**
Items whose exact wording matters most are marked **⚠ re-verify**. This debt is tracked in
§8.

---

## 2. Machine and material baseline

| # | Finding | Level | Source |
|---|---|---|---|
| 2.1 | The U1 has **4 independent toolheads** (true multi-toolhead, not a single-nozzle MMU). Tool changes do not cause in-nozzle cross-contamination. | **O** | Already established in [`U1_PRINT_PROFILE_RESEARCH.md`](U1_PRINT_PROFILE_RESEARCH.md) |
| 2.2 | Base material support: **PLA, PETG, TPU, PVA, PCTG**. | **O** ⚠ re-verify | [Snapmaker U1 specs](https://www.snapmaker.com/snapmaker-u1/specs) |
| 2.3 | **With the top cover**: adds PET, ABS, ASA, PA, PC. | **O** ⚠ re-verify | [Snapmaker U1 specs](https://www.snapmaker.com/snapmaker-u1/specs) |
| 2.4 | **With top cover + hardened-steel hot ends**: adds carbon-fibre and glass-fibre reinforced polymers. | **O** ⚠ re-verify | [Snapmaker U1 specs](https://www.snapmaker.com/snapmaker-u1/specs) |
| 2.5 | The U1 is **"currently compatible with TPU ≥ 90A Shore hardness, while softer grades (< 90A) are under active testing and validation."** | **O** ⚠ re-verify | [U1 FAQ (Snapmaker Wiki)](https://wiki.snapmaker.com/en/FAQ/u1) |
| 2.6 | Snapmaker's own multi-material lab testing covers **PLA, PETG, TPU, PVA, ABS, ASA**. | **O** ⚠ re-verify | [U1 Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |

**Consequence for the tutorial:** TPU **below 90A** is officially *not yet validated*. Any
tutorial content must say exactly that and must not present a working sub-90A recipe as
supported. If we test 85A, it is reported as **our observation on our machine**, tagged **T→C**,
never as a Snapmaker-supported configuration.

---

## 3. Material-pair findings

### 3.1 Snapmaker's own adhesion framing

| # | Finding | Level | Source |
|---|---|---|---|
| 3.1.1 | Snapmaker groups multi-material pairs by **interfacial adhesion**. Naturally compatible pairs show high interfacial adhesion and "can be printed as load-bearing or structural parts without any additional bonding settings or process optimization." | **O** ⚠ re-verify | [Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |
| 3.1.2 | Weak-adhesion pairs are framed as **useful two ways**: (a) as supports, removed cleanly using a **zero Z-distance**; (b) as functional joins, mechanically stitched with **Beam Interlocking**. | **O** ⚠ re-verify | same |
| 3.1.3 | For weak-adhesion pairs, the interfacial bond "can be significantly strengthened using Snapmaker Orca's **Beam Interlocking** feature, making them suitable for **rigid–flexible material combinations**." | **O** ⚠ re-verify | same |
| 3.1.4 | Snapmaker also states that blending materials with significantly different properties, **such as PLA with PVA or PETG**, is "generally not recommended, as final print behavior and visual results may vary." | **O** ⚠ re-verify | [U1 FAQ](https://wiki.snapmaker.com/en/FAQ/u1) |

> **Apparent tension worth naming in the article.** 3.1.4 discourages PLA+PETG blending,
> while Snapmaker separately publishes a **PLA-and-PETG support guide** (§3.5). Read
> together, the consistent reading is: *weak adhesion is a defect when you want a
> structural join, and a feature when you want a support that releases.* That reframe is
> genuinely useful to a novice and is defensible from official sources alone. It is a
> **reading**, not a Snapmaker quote — present it as our interpretation.

### 3.2 PLA + TPU

| # | Finding | Level | Source |
|---|---|---|---|
| 3.2.1 | **TPU + PLA** is listed among the combinations for which Beam Interlocking is offered "for stronger bonds". | **O** ⚠ re-verify | [Snapmaker TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) |
| 3.2.2 | Snapmaker TPU 90A supports "seamless multi-filament co-printing with **PLA, PETG, and TPU 95A**". | **O** ⚠ re-verify | same |
| 3.2.3 | PLA and TPU do not form a permanent chemical bond — which is precisely why PLA works well as a *support* for TPU and separates cleanly. | **C** | [omni3d guide](https://omni3d.com/how-to-print-tpu-with-support-guide-for-easy-removal/); [Bambu forum thread](https://forum.bambulab.com/t/supporting-tpu-prints-with-pla-how-to-do-it/29300) |
| 3.2.4 | A Snapmaker blog reports combining TPU with PLA and with PETG in single U1 jobs, including one job with **"92 toolhead swaps without a single jam."** | **C** (Snapmaker marketing blog, not documentation) | [Snapmaker blog — TPU print ideas](https://www.snapmaker.com/blog/tpu-3d-print-ideas/) |
| 3.2.5 | Flat PLA/TPU interface peel strength, and the delta from Beam Interlocking, on a U1. | **T** | **No published figure found. Test T1/T2.** |

### 3.3 PETG + TPU

| # | Finding | Level | Source |
|---|---|---|---|
| 3.3.1 | **PETG + TPU** is described as a strongly-bonding pair that fuses chemically and can be printed as structural parts without special bonding settings. | **O** ⚠ re-verify | [Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |
| 3.3.2 | **TPU + PETG** is nonetheless also listed among the Beam-Interlocking-capable combinations. | **O** ⚠ re-verify | [TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) |
| 3.3.3 | Whether Beam Interlocking measurably *adds* strength to an already-strong PETG/TPU bond, or only adds print time and risk. | **T** | **Unresolved in official sources. Test T3/T4 — this is the most interesting single question in the matrix.** |
| 3.3.4 | PETG and TPU print at very different bed temperatures (§4), which constrains the shared first layer. | **T** | Deduced from official per-material ranges; not stated as a combined constraint anywhere we found. |

### 3.4 ABS/ASA + TPU

| # | Finding | Level | Source |
|---|---|---|---|
| 3.4.1 | ABS and ASA require the **top cover** on the U1. | **O** ⚠ re-verify | [U1 specs](https://www.snapmaker.com/snapmaker-u1/specs) |
| 3.4.2 | Snapmaker's multi-material lab trials include ABS and ASA among the materials tested. | **O** ⚠ re-verify | [Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |
| 3.4.3 | **No official ABS/ASA + TPU guidance was found.** Snapmaker's published TPU co-printing list (PLA, PETG, PA, PET, TPU 95A) does **not** include ABS or ASA. | **O (absence)** | [TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) |
| 3.4.4 | ABS/ASA want a hot, enclosed, draught-free environment; Snapmaker TPU 90A specifies a **25–60 °C bed** and **cooling fan ON**. These are opposing process requirements in one enclosed job. | **T** | Deduced from §4.1 and 3.4.1. **Not tested by us.** |

> **Decision for this phase: ABS/ASA + TPU is explicitly OUT of the eight-print matrix.**
> Reasons: no official pairing guidance, an unresolved thermal conflict, and enclosure
> hardware not assumed present. Documenting the gap honestly is more valuable than
> guessing a recipe. If Snapmaker wants it covered, it becomes a separate, separately
> resourced phase with the top cover fitted.

### 3.5 TPU as / with support interfaces

| # | Finding | Level | Source |
|---|---|---|---|
| 3.5.1 | Snapmaker publishes an official **different-filament-support** recipe using PLA and PETG: print the support **base** in the same material as the model, and use the dissimilar material **only for the support interface**, because the two need different bed temperatures. | **O** ⚠ re-verify | [Using a Different Filament for Support (PLA and PETG)](https://wiki.snapmaker.com/en/snapmaker_u1/printing_guides/pla_and_petg) |
| 3.5.2 | That same guide specifies: **Top Z distance = 0**; support base pattern **Rectilinear**; **Top interface layers = 3**; interface pattern **Rectilinear Interlaced**; **top and bottom interface spacing = 0**. Test values it cites: PLA **230 °C**; PETG **265 °C** with bed **65 °C** and **max volumetric speed 10 mm³/s**. | **O** ⚠ re-verify | same |
| 3.5.3 | Weak-adhesion pairs are officially framed as good supports precisely because of **zero Z-distance** clean release. | **O** ⚠ re-verify | [Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |
| 3.5.4 | A filament vendor reports **PLA supports break away cleanly from a TPU surface**, whereas **TPU-on-TPU supports can fuse together**. | **C** (vendor testing) | [Siraya Tech — Fixing TPU jams on Snapmaker U1](https://siraya.tech/blogs/news/fixing-tpu-jams-on-snapmaker-u1-professional-settings-for-stable-24h-flexible-printing) |
| 3.5.5 | Whether **TPU as the support interface under PLA** (the inverse of 3.5.4) releases cleanly, and what Z-distance/interface spacing it needs on a U1. | **T** | **No source found either way. Tests T5/T6.** |
| 3.5.6 | Reported Snapmaker Orca **Beta 2.3.0** behaviour: the support-interface material is applied only to supports touching the build plate; supports growing **from the model** print their interface in the base support material instead. | **C** (single user report, version-specific, no staff reply in the excerpt read) | [Snapmaker forum thread 41686](https://forum.snapmaker.com/t/u1-multi-material-support-interface-layer/41686) |

> 3.5.6 matters more than its evidence level suggests: if it reproduces on the Orca build
> we test with, **every model-borne support in tests T5/T6 is invalid** unless the model is
> designed so all supports start on the plate. The matrix builds that in as a
> pre-condition check.

### 3.6 TPU 95A + TPU 90A

| # | Finding | Level | Source |
|---|---|---|---|
| 3.6.1 | Snapmaker TPU 90A is stated to co-print with **TPU 95A**. | **O** ⚠ re-verify | [TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) |
| 3.6.2 | TPU 90A is described as "noticeably softer, silkier, and more skin-friendly" than TPU 95A. | **O** (marketing copy) ⚠ re-verify | same |
| 3.6.3 | A user reports running Bambu High-Flow TPU 95A on the U1 with better-than-expected results. | **C** (single report) | [Snapmaker forum thread 40540](https://forum.snapmaker.com/t/first-u1-tpu-95hf-multicolor-print/40540) |
| 3.6.4 | Two TPU grades bond to each other well (same polymer family) but a **soft prime/wipe tower may not be self-supporting**, and toolchange behaviour with two flexibles loaded is unknown to us. | **T** | Tests T7/T8. |

---

## 4. Flexible-material process findings

### 4.1 Official TPU 90A parameters (Snapmaker)

All from the [Snapmaker TPU 90A product page](https://us.snapmaker.com/products/tpu-90a-filament-1kg) — **O** ⚠ re-verify:

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
| 4.2.1 | "For flexible filaments such as TPU, please follow the instructions for **Manual Loading**." | **O** ⚠ re-verify | [Manual Loading (Wiki)](https://wiki.snapmaker.com/en/snapmaker_u1/manual_loading) |
| 4.2.2 | Trim the filament end at **~45°** with diagonal cutters — this "reduces feeding resistance, thus enhancing the success rate." | **O** ⚠ re-verify | same |
| 4.2.3 | Auto Loading must be **disabled per toolhead**: Settings → Print Preferences → Auto Loading. | **O** ⚠ re-verify | same |
| 4.2.4 | Press the circular latch at the end of the corresponding feeder and unplug the tube connected to the target toolhead. Then: Loading Mode → Filament Loading Guide → Switch to Manual Loading. | **O** ⚠ re-verify | same |
| 4.2.5 | "It is recommended to unplug the tube from the top of the toolhead, expose part of filament, and push it downward manually to ensure proper contact with the extrusion gears." | **O** ⚠ re-verify | same |
| 4.2.6 | Flexible filaments also require **Manual Unloading**: Filament page → Unloading Mode → select toolheads → Unload. | **O** ⚠ re-verify | [Manual Unloading (Wiki)](https://wiki.snapmaker.com/en/snapmaker_u1/flexible_filament_unloading) |
| 4.2.7 | 85A TPU reportedly loads but "may need manual help during loading by feeding into the toolhead by hand". | **C** (third-party review) | [fauxhammer U1 review](https://www.fauxhammer.com/reviews/snapmaker-u1-review-the-multi-colour-printer-that-actually-moves-the-market-forward/) |

> **The single most under-communicated official fact we found:** flexible filament on the U1
> is a **manual load and manual unload**, per-toolhead, with Auto Loading switched off. A
> novice who leaves Auto Loading on and walks away is the archetypal first TPU failure. This
> should open the tutorial.

### 4.3 Filament-path resistance

| # | Finding | Level | Source |
|---|---|---|---|
| 4.3.1 | The 45° cut is officially justified as **reducing feeding resistance** (4.2.2) — Snapmaker names path resistance as the failure mechanism. | **O** ⚠ re-verify | [Manual Loading](https://wiki.snapmaker.com/en/snapmaker_u1/manual_loading) |
| 4.3.2 | A vendor states the U1's PTFE tubing has a larger-than-standard internal diameter, "which significantly reduces friction", letting flexibles slide from the back of the machine to the extruder "without binding". | **C** (vendor claim, no dimension given) | [Siraya Tech](https://siraya.tech/blogs/news/fixing-tpu-jams-on-snapmaker-u1-professional-settings-for-stable-24h-flexible-printing) |
| 4.3.3 | A vendor reports **excessive extruder gear pressure** as a jam cause, fixed by loosening the side screw on the printhead. | **C** (vendor claim) | same |
| 4.3.4 | Spool drag, dry-box path length, and tube routing measurably change load success on TPU. | **T** | Not measured. The matrix records the path setup per test so the variable is at least *controlled*, even though we do not attempt to quantify it. |

> **Safety note on 4.3.3:** loosening an extruder tension screw is a **hardware modification**.
> This project does **not** recommend it, does not include it in any test, and the tutorial
> must not repeat it as advice. Recorded here only because it circulates widely.

### 4.4 Toolchange retraction

| # | Finding | Level | Source |
|---|---|---|---|
| 4.4.1 | A vendor states the U1/Orca default **"Retraction at Switch"** is **10 mm** and calls it the most common cause of toolchanger jams with soft filament, because TPU buckles and "bird-nest[s]" around the extruder gears during a swap. Recommended **0–4 mm**. | **C** (vendor testing; **default value not verified by us against the shipped Orca profile**) | [Siraya Tech](https://siraya.tech/blogs/news/fixing-tpu-jams-on-snapmaker-u1-professional-settings-for-stable-24h-flexible-printing) |
| 4.4.2 | A Snapmaker blog suggests keeping retraction distance low, "around **0.8 – 2.0 mm** for direct drive", to avoid stretching filament inside the extruder. | **C** (Snapmaker blog, not documentation) | [Snapmaker blog](https://www.snapmaker.com/blog/tpu-3d-print-ideas/) |
| 4.4.3 | The actual shipped value of retraction-at-toolchange in the Snapmaker Orca U1 TPU profile. | **T** | **Must be read out of Orca and recorded verbatim before any test runs.** The matrix makes this a pre-condition, not an assumption. |

> This is the clearest example of the C→O trap. "Set retraction at switch to 0–4 mm" is
> currently a **vendor recommendation**, full stop. It may not even be describing the
> current profile. Nothing in Studio or the tutorial states it as a setting until the
> shipped default is read and a test measures the difference.

### 4.5 Dynamic Flow Calibration

| # | Finding | Level | Source |
|---|---|---|---|
| 4.5.1 | Dynamic Flow Calibration "compensates for extrusion pressure lag during acceleration and deceleration. By adjusting flow in real time, it helps prevent blobbing, gaps, and inconsistencies." | **O** ⚠ re-verify | [Dynamic Flow Calibration (Snapmaker support)](https://support.snapmaker.com/hc/en-us/articles/36143463233815-Dynamic-Flow-Calibration) |
| 4.5.2 | Requires **Snapmaker Orca V2.3.1 or higher**. Run from the touchscreen: Start → Next → Dynamic Flow Calibration, then start the print. | **O** ⚠ re-verify | same |
| 4.5.3 | **"Run Dynamic Flow Calibration after every filament change."** Automatic, no manual intervention, a couple of minutes. | **O** ⚠ re-verify | same |
| 4.5.4 | **Not recommended for 0.2 mm hot ends** — dynamic flow compensation is unreliable at that nozzle size. | **O** ⚠ re-verify | same |
| 4.5.5 | Whether DFC materially changes TPU surface quality or interface bond on a rigid-flexible job. | **T** | Held **constant** (always run) across the whole matrix rather than tested, so it never becomes a hidden variable. |

### 4.6 Prime / wipe tower with flexibles

| # | Finding | Level | Source |
|---|---|---|---|
| 4.6.1 | Wall type **Rib** "significantly improve[s] the tall tower's resistance to tipping and reduce[s] the risk of collapse caused by nozzle collisions". | **O** | [U1 Prime Tower Collapse](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/prime_tower_collapse) (already cited by Studio) |
| 4.6.2 | Increasing rib length gives the tower a larger footprint and a more stable base; rib width should not be set small — ensure enough contact between the outer wall and internal infill. | **O** ⚠ re-verify | same |
| 4.6.3 | **When adhesion between the two materials is poor (the guide names PLA + PETG), the tower itself is prone to delamination or breakage at the material interface.** | **O** ⚠ re-verify | same |
| 4.6.4 | A user reports PLA printed above PETG on a prime tower had no adhesion and "just turn[ed] into spaghetti". | **C** | [Snapmaker forum thread 40432](https://forum.snapmaker.com/t/multimaterial-prime-tower-failed/40432) |
| 4.6.5 | Studio's existing tower safety rails: never auto-enable `wipe_tower_no_sparse_layers`; never auto-raise `wipe_tower_max_purge_speed` above **90 mm/s**. | **O** (verified in-repo + U1 doc) | [`U1_PRINT_PROFILE_RESEARCH.md`](U1_PRINT_PROFILE_RESEARCH.md), `backend/snapstudio_core/strategies.py` |
| 4.6.6 | Tower behaviour when one or both materials is **TPU**: a soft tower may deform under nozzle contact rather than snap, and a rigid/flexible tower has exactly the "poor adhesion between layers of different material" condition 4.6.3 warns about. | **T** | Every test in the matrix records tower outcome as a first-class result, not an afterthought. |

> 4.6.3 is the bridge between "material choice" and "tower collapse": the tower is a
> miniature version of the same bonded interface as the part. That is a genuinely
> explanatory idea for the tutorial, and it is officially sourced.

### 4.7 Beam Interlocking

| # | Finding | Level | Source |
|---|---|---|---|
| 4.7.1 | Beam Interlocking is available in Snapmaker Orca and mechanically stitches two materials at their boundary, strengthening weak chemical adhesion — explicitly named for **rigid–flexible** combinations. | **O** ⚠ re-verify | [Multi-material printing performance](https://support.snapmaker.com/hc/en-us/articles/34287488318615-Snapmaker-U1-Multi-material-printing-performance) |
| 4.7.2 | Parameter set (upstream OrcaSlicer documentation): **interlocking beam width**, **interlocking direction**, **interlocking beam layers**, **interlocking depth** (in cells), **interlocking boundary avoidance** (in cells). | **O** (OrcaSlicer docs — upstream, not Snapmaker) | [OrcaSlicer — multimaterial advanced](https://www.orcaslicer.com/wiki/print_settings/multimaterial/multimaterial_settings_advanced) |
| 4.7.3 | Interlocking depth is "the distance from the boundary between filaments to generate interlocking structure, measured in cells"; **"too few cells will result in poor adhesion."** Boundary avoidance is the distance from the model's outside where interlocking is not generated. | **O** (OrcaSlicer docs) | same |
| 4.7.4 | **Recommended Beam Interlocking values for PLA/TPU or PETG/TPU on a U1.** | **T** | **No published values found from Snapmaker or upstream.** Tests T2/T4 use the shipped Orca defaults **unchanged** and record them verbatim. We do not invent a tuned recipe. |
| 4.7.5 | Bambu publishes a soft-and-hard multi-material guide that may contain adjacent-ecosystem guidance. | **unread** | [Bambu H2 soft/hard guide](https://wiki.bambulab.com/en/h2/manual/soft-and-hard-filament-multi-material-printing-guide) — fetch returned HTTP 402; **not read**, listed for completeness only. |

### 4.8 Nozzle contamination and cold pulls

| # | Finding | Level | Source |
|---|---|---|---|
| 4.8.1 | Official U1 unclogging: heat the nozzle **10–20 °C above the filament's normal printing temperature** (examples given: PLA 200 → 210–220 °C; PETG 240 → 250–260 °C; ABS 240 → 250–260 °C), then use the supplied cleaning needle up and down several times. Avoid excessive force. | **O** ⚠ re-verify | [U1 filament not extruding](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/filament_not_extruding) |
| 4.8.2 | **Safety-critical:** because the U1's integrated hot end uses an **interference-fit assembly**, applying intense flame (thermal burnout) is **prohibited** — it can cause hot-end components to detach and fail. | **O** ⚠ re-verify | same |
| 4.8.3 | After cleaning, reload filament to confirm the nozzle is unobstructed; repeat the needle/push cycle until extrusion is straight and stable. | **O** ⚠ re-verify | same |
| 4.8.4 | TPU→rigid or rigid→TPU residue in a shared toolhead is not a U1 concern in the MMU sense (each toolhead keeps its own filament), but **a toolhead reused across materials between tests** can carry residue. | **T** | Handled procedurally: the matrix assigns materials to fixed toolheads and forbids mid-matrix reassignment (§ one-variable rule). |

> "Cold pull" as a generic technique is widely used in the hobby. **Snapmaker's own
> published U1 procedure is the needle method**, and it explicitly prohibits flame. The
> tutorial should teach the official procedure and name the prohibition, not a generic
> cold-pull recipe.

### 4.9 Toolhead offset / calibration failures

| # | Finding | Level | Source |
|---|---|---|---|
| 4.9.1 | Multi-toolhead offset calibration takes about **15–20 minutes**; once done it does not need repeating before every print. | **O** ⚠ re-verify | [Snapmaker support — U1](https://support.snapmaker.com/hc/en-us/categories/36087874981527-Snapmaker-U1) |
| 4.9.2 | Recalibrate whenever you **move the printer, replace a toolhead or hot end, or perform major maintenance**. Insufficient lubrication of the steel balls increases running resistance and causes positioning errors. | **O** ⚠ re-verify | [U1 multi-color misalignment](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/multi-color_misalignment) |
| 4.9.3 | Misalignment procedure: the gap between the hot-end copper plate and the calibration sensor should be **0.1–0.4 mm** (adjust with an H2.0 hex key by loosening the two hot-end screws, pushing the hot end up, re-tightening); clean pogo pins and steel balls with alcohol; apply an even layer of white lithium grease to the steel balls; then run multi-toolhead offset calibration. | **O** ⚠ re-verify | same |
| 4.9.4 | If one toolhead prints a correct first layer while two or more fail, run **Multi-toolhead Offset Calibration**. | **O** ⚠ re-verify | [U1 known issues and quick fixes](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/known_issues_and_quick_fixes) |
| 4.9.5 | Excessive force when installing the filament holder can pop the left/right inner panel and obstruct the toolhead returning home. | **O** ⚠ re-verify | [U1 toolhead swapping anomaly, first setup](https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/toolhead_swapping_anomaly_first_setup) |
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
- Dynamic Flow Calibration or toolhead-offset calibration state as an input to advice.
- TPU-specific entries in the Community Knowledge base (none of the six mention TPU).

**Therefore Studio cannot today claim any rigid-flexible capability.** It can claim, truthfully:
*"Studio checks whether your colours fit your toolheads, whether the file's filament metadata
is consistent, whether the model fits the plate with tower clearance, and recommends a
prime/wipe-tower strategy for review in Orca."* Nothing about material compatibility.

---

## 6. Top community pain points (ranked by how often they recur and how badly they bite)

1. **Flexible filament auto-load failure / gear bird-nesting on toolchange.** Officially the answer is manual load + manual unload (§4.2); the community's answer is retraction-at-switch (§4.4). Users hit this on their very first TPU job.
2. **Prime/wipe tower failure on dissimilar materials.** Officially acknowledged: poor inter-material adhesion delaminates the tower itself (§4.6.3), plus the general tall-tower collapse mode Studio already covers.
3. **Support interface printed in the wrong material** (reported Orca Beta 2.3.0 behaviour for supports growing from the model, §3.5.6) — the print looks like a settings mistake when it may be a slicer behaviour.
4. **Multi-colour misalignment blamed on the model.** Offset calibration drift from moving the machine, swapping a hot end, or unlubricated steel balls (§4.9) presents as "my multi-material seam is bad".
5. **Conflicting speed/drying advice for TPU** between Snapmaker's own product page and its own blog (§4.1) — a novice cannot tell which to follow.
6. **Nozzle clogs "fixed" with a torch.** Widely-repeated generic advice that is **explicitly prohibited** on the U1's interference-fit hot end (§4.8.2).
7. **Sub-90A TPU treated as supported.** It is officially still under validation (§2.5); community posts about 85A blur that line.

---

## 7. What must NOT be claimed

- ❌ Any statement that a material pair "will print" or "will hold". Adhesion is advisory.
- ❌ Beam Interlocking values for TPU pairs — none are published; defaults only, recorded verbatim.
- ❌ The 0–4 mm retraction-at-switch figure as a Snapmaker setting. It is a vendor recommendation (§4.4.1) and the shipped default has not been read.
- ❌ Blog-sourced TPU speeds (270/200/500 mm/s) as recommended settings — the product page's 30–50 mm/s is the documented figure (§4.1).
- ❌ TPU below 90A as supported.
- ❌ ABS/ASA + TPU guidance of any kind.
- ❌ That Studio's structural/metadata validation predicts physical success. It does not, and this document does not change that.
- ❌ Loosening the extruder tension screw (§4.3.3).

---

## 8. Verification debt (must clear before external publication)

| Item | Action | Blocks |
|---|---|---|
| All **⚠ re-verify** rows | Re-open each cited URL in a browser; confirm wording verbatim; record retrieval date. | Any external article; any product copy. |
| §4.4.3 shipped retraction-at-toolchange default | Read out of Snapmaker Orca's U1 TPU profile; record verbatim. | Tests T1–T8. |
| §4.7.4 Beam Interlocking defaults | Read out of Snapmaker Orca; record verbatim. | Tests T2, T4. |
| §3.5.6 support-interface behaviour | Reproduce (or fail to reproduce) on the Orca build under test. | Tests T5, T6. |
| §4.7.5 Bambu soft/hard guide | Fetch by other means and read, or drop the reference entirely. | Nothing — optional. |
| Snapmaker U1 multi-material performance article | Obtain the actual adhesion table (categories and member materials), which we have only in summarised form. | Any per-pair claim stronger than "Snapmaker groups pairs by adhesion strength". |

---

## 9. Related documents

- [`U1_RIGID_FLEXIBLE_TEST_MATRIX.md`](../testing/U1_RIGID_FLEXIBLE_TEST_MATRIX.md) — the eight controlled prints that convert **T** findings into evidence.
- [`U1_RIGID_FLEXIBLE_TOPIC_FRAMEWORK.md`](../tutorials/U1_RIGID_FLEXIBLE_TOPIC_FRAMEWORK.md) — proposed article structure and positioning.
- [`FLEXIBLE_MATERIAL_DOCTOR_PROPOSAL.md`](../product/FLEXIBLE_MATERIAL_DOCTOR_PROPOSAL.md) — whether and how this becomes a product surface without becoming a slicer.
- [`U1_PRINT_PROFILE_RESEARCH.md`](U1_PRINT_PROFILE_RESEARCH.md) — the prime/wipe-tower research this builds on.
