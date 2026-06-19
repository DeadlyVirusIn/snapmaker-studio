# U1 Print-Profile Research (Phase 1)

> Research only. Findings are grounded in the sources below — **no settings are
> guessed**, and no GPL/AGPL code is copied (concepts, documented defaults, and
> terminology only). **Snapmaker Orca still does the slicing**; Studio only *reads*
> a design and *recommends* a print strategy. These settings are slicer process
> settings — none command printer firmware.

## Sources

- Snapmaker/OrcaSlicer fork `PrintConfig.cpp` (the slicer the U1 uses) —
  https://raw.githubusercontent.com/Snapmaker/OrcaSlicer/main/src/libslic3r/PrintConfig.cpp
- SoftFever/OrcaSlicer (upstream) `PrintConfig.cpp` —
  https://raw.githubusercontent.com/SoftFever/OrcaSlicer/main/src/libslic3r/PrintConfig.cpp
- OrcaSlicer wiki — Prime Tower:
  https://github.com/OrcaSlicer/OrcaSlicer/wiki/multimaterial_settings_prime_tower
- OrcaSlicer wiki — Wipe Tower:
  https://github.com/OrcaSlicer/OrcaSlicer/wiki/printer_multimaterial_wipe_tower
- **Snapmaker U1 — Prime Tower Collapse troubleshooting (U1-authoritative):**
  https://wiki.snapmaker.com/en/snapmaker_u1/troubleshooting/prime_tower_collapse
- Bambu — Reduce Waste during Filament Change:
  https://wiki.bambulab.com/en/software/bambu-studio/reduce-wasting-during-filament-change

## Hardware framing (authoritative)

The Snapmaker U1 has **4 independent toolheads** (true multi-toolhead), not a
single-nozzle MMU. Tool changes do **not** cause in-nozzle cross-contamination, so the
large purge volumes a single-nozzle MMU needs are mostly unnecessary — but a prime/wipe
tower is still used for tip priming and ooze control. Tall towers on the U1 can **tip
over / be hit by the nozzle**; the Snapmaker U1 collapse guide is the primary source for
stability guidance below.

## Settings — verified defaults, ranges, confidence

Key: **V** = verified in official docs/source · **I** = inferred (community/reasoning).
Defaults are read directly from each repo's `PrintConfig.cpp`. Where the two repos differ,
both are shown (the U1 uses the **Snapmaker fork**).

| Setting | Key | Range/units | Default (Snapmaker fork / upstream) | Conf. |
|---|---|---|---|---|
| Prime tower width | `prime_tower_width` | mm, min 2 | 60 / 60 | V high |
| Prime volume | `prime_volume` | mm³, min 1 | 45 / 45 | V high |
| Brim width | `prime_tower_brim_width` | mm | 3 / 3 (upstream: -1=auto) | V high |
| Brim chamfer | `prime_tower_brim_chamfer` (+`_max_width` 4mm) | bool | true — **fork only**, hidden (`comDevelop`) | V (fork) high |
| Wall type | `wipe_tower_wall_type` | rectangle/cone/rib | **rectangle** / rib | V high |
| Rib width | `wipe_tower_rib_width` | mm, 0–300 | 8 / 8 | V high |
| Extra rib length | `wipe_tower_extra_rib_length` | mm, ≤300 | 0 / 0 | V high |
| Fillet wall | `wipe_tower_fillet_wall` | bool | true / true | V high |
| Max purge/tower speed | `wipe_tower_max_purge_speed` | mm/s, min 10 | 90 / 90 | V high |
| No sparse layers | `wipe_tower_no_sparse_layers` | bool | false / false | V high |
| Flush matrix (N×N) | `flush_volumes_matrix` | mm³ list | off-diag ~280, diag 0 | V high |
| Flush multiplier | `flush_multiplier` | float (fork: scalar; upstream: per-filament) | 0.3 | V high |
| Min purge on tower | `filament_minimal_purge_on_wipe_tower` | mm³, min 0 | 15 | V high |
| Flush into infill/support/objects | `flush_into_*` | bool | infill false / support true / objects false | V high |

### Directional effects (verified from tooltips + U1 collapse guide)

- **Wall type = Rib** → "significantly improve the tall tower's resistance to tipping and
  reduce the risk of collapse caused by nozzle collisions" (Snapmaker U1 doc). Rectangle =
  smallest footprint/waste, least stable.
- **Keep the tower square** via `prime_tower_width` (U1 doc). Too narrow + tall = collapse.
- **Larger brim** (`prime_tower_brim_width`) → better adhesion / less tip-over; more waste.
- **`wipe_tower_max_purge_speed` above 90 mm/s** → tooltip warns of stronger nozzle/blob
  collisions and reduced stability; confirm the printer can bridge reliably first.
- **`wipe_tower_no_sparse_layers` ON** → far less waste/time, but the nozzle plunges to a
  shorter tower on tool-change layers — **"user is responsible for ensuring there is no
  collision."** Highest print-risk toggle here.
- **Purge cleanliness** scales with `flush_volumes_matrix × flush_multiplier`; raising it
  cleans color transitions at the cost of waste/time. Auto matrix is color-distance-based;
  the exact RGB→volume formula is **not published** (inferred).

## Verified vs inferred

- **Verified (high):** every default/range/units above (read from source); the directional
  guidance from Snapmaker's U1 collapse guide (Rib, square tower, brim, ≤90 speed,
  no-sparse-layers collision warning).
- **Inferred (med):** the exact RGB→purge auto-calc formula; "recipe" combinations for
  speed/quality/reliability (directionally grounded, but the specific bundles are our
  policy, not a published Snapmaker preset).
- **Fork-specific:** `prime_tower_brim_chamfer` exists only in the Snapmaker fork and is a
  hidden developer setting — do not emit for upstream OrcaSlicer.

## Recommended safe defaults (policy, ranges not fake precision)

These are **recommendation ranges/policies**, not claimed-proven exact presets. Studio
shows them; the user applies them in Snapmaker Orca, which slices.

- **Stability-first baseline (Balanced/Reliability):** Rib wall, tower kept square, brim
  ≥ default (3 mm; more for tall jobs), max purge speed ≤ 90 mm/s, **no-sparse-layers OFF**.
- **Waste/time reduction (Fastest):** Rectangle wall acceptable for short/low towers,
  smaller brim, flush multiplier toward the low end, optionally `flush_into_infill` —
  **only** when geometry/contamination tolerance allows; never enable no-sparse-layers
  automatically.
- **Color cleanliness (Best Quality):** higher flush multiplier / purge, keep stability
  settings; accept more waste/time.

## Risks

- **Tower collapse / nozzle collision** — the dominant U1 failure mode; driven by tall+thin
  towers, rectangle wall on tall jobs, high purge speed, and no-sparse-layers.
- **Color bleed** — purge volume too low.
- **Adhesion loss** — brim too small.
- All risks are **print-outcome** risks (a failed or ugly print / wasted filament), not
  hardware-command risks: these are slicer settings, not firmware commands.

## Unknowns (do not guess)

- Exact auto purge-volume formula (color → mm³).
- Whether Snapmaker ships an official U1 "fast/quality/reliability" preset to mirror — none
  found; our strategies are policy bundles, labeled as such.
- Real per-design tool-change counts and print durations — **not computable** from Studio's
  read-only signals; must not be fabricated.

## Settings that must NOT be changed automatically

- **`wipe_tower_no_sparse_layers`** — never auto-enable (explicit collision warning).
- **`wipe_tower_max_purge_speed` above 90 mm/s** — never auto-raise past the U1-documented
  safe value.
- **Per-filament/per-design data** — `filament_colour`, `filament_type`,
  `filament_settings_id`, and the flush matrix's design-specific entries (already protected
  by `profile._PROTECTED_PREFIXES`).
- **Geometry / object layout / painting** — strategies never touch the mesh.

## How this maps into Studio (Phase 2)

Strategies are a **recommendation + explanation** layer. They are stored as inert
optimization bundles (`data/optimizations/`, only applied in opt-in `optimize` mode — the
default convert path is unchanged) plus a pure recommendation policy driven by **real
signals only** (color/material count, source ecosystem, dimensions, complexity/triangles,
existing validation issues). Studio never fabricates duration, tool-change count, or purge
volume. See `U1_ADAPTIVE_PROFILES.md` for the profile/inheritance concepts and
`../design/PRINTER_HUB.md` for the monitoring side.
