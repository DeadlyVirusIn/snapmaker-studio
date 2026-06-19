# Design Intelligence — Gap Analysis + v0.5 Plan

> Planning only — nothing here is implemented. Scope: expand Studio's **read-only,
> local-first, pre-slice** Design Intelligence. Studio does not slice (Snapmaker Orca
> slices) and does not control printers. No GPL/AGPL code copied — concepts only.
> Snapmaker U1 is the first printer target. Effort: **S** ≈ 1–2 dev-days · **M** ≈ 3–5 ·
> **L** ≈ 1–2 weeks. Value 1–5 (novice + Fund differentiation weighted).

## 1. Current capabilities (audit)

| Area | Today | Where |
|---|---|---|
| Dimensions | Bounding-box X/Y/Z (mm) | `intelligence._bbox_and_triangles` / `_stl_bbox_and_triangles` |
| Complexity | Triangle **count** + low/med/high tier | `intelligence._complexity` |
| Materials | Colors + types, painted flag, object/plate/color counts | `intelligence` + `doctor`/`fingerprint` |
| Source/ecosystem | bambu-family / prusa / stl / generic | `detect` / `canonical` |
| Readiness | Verdict + score; Validation Center checks (prints-on-U1, **bed-fit vs 270³**, colours) + preserved/changes/at-risk | `doctor`, `validation_report` |
| Strategy input | Recommendation uses colors, dims, complexity, issues | `strategies.recommend` |
| Mesh access | **STL → indexed mesh** (deduped verts + tri indices) via `parse_stl`; binary-STL facet normals parsed but **discarded** | `stl_io.parse_stl` |

**Key limitation:** there is **no geometry diagnosis** — only counts and a bounding box.
And the **3MF geometry path is regex-only** (`_VERT_RE`/`_TRI_RE`): we get a bbox + a
triangle count, **not** an indexed mesh, so any per-face analysis is STL-only today.

## 2. Gap analysis

Missing, all **slice-free** (computable from mesh + printer profile, no slicer engine):

| Gap | What it predicts | Slice-free? |
|---|---|---|
| Mesh integrity — manifold, watertight, consistent normals, degenerate/duplicate faces, holes, self-intersections | Cryptic slicer failures, missing/garbled walls, "fix needed" | ✅ pure topology |
| Volume / surface area / rough material estimate | Filament/cost ballpark (must be framed "estimate", not slice-accurate) | ✅ |
| Overhang / steep-face distribution (face normal vs +Z) | Supports likely; bridging risk | ✅ needs per-face normals |
| Stability / footprint / tall-narrow tip risk | First-layer knock-off, tall-print + tower tip-over (U1) | ✅ |
| Min feature size vs nozzle (≈thin walls) | Walls/text that won't print at 0.4 mm | ⚠️ approx slice-free; exact = harder |
| Bed-fit nuance + orientation hint | Fits if rotated; tallest-axis advice | ✅ |
| First-layer footprint / contact area | Adhesion/warp risk | ✅ approx |

Needs slicing (OUT of scope — Orca's job): exact print time, exact filament/purge grams,
toolpath/seam placement, layer preview, true wall-thickness from toolpaths.

## 3. Differentiation thesis (vs slicers)

Slicers analyze **at slice time**, in **slicer jargon**, **per-ecosystem**, for **their own
printer**. Studio's edge is the opposite on every axis:
- **Pre-slice + plain-language** — "this model will likely need supports," not a toolpath.
- **Cross-ecosystem** — one read for Bambu/Orca/Prusa/STL (built on the canonical model).
- **Local-first + read-only** — no upload, no account, never mutates the file.
- **U1-aware printability** — bed, 4 toolheads, tower/tip-over, feeds the print-strategy pick.
- **"Will it print + why + what to do"** rather than raw stats.

**Strongest differentiators** (do these): plain-language **overhang/supports prediction**,
**mesh-integrity "will this fail" warnings**, and **U1 stability/tip-risk** — none need a
slicer, all are novice-first, all are cross-ecosystem.

## 4. Proposed v0.5 roadmap (phased)

**Phase A — Mesh foundation (dependency for B/C).** A shared, pure-Python indexed-mesh
loader for **both** STL and 3MF (replace the 3MF regex with a real `.model` vertex/triangle
parse; keep binary-STL facet normals instead of discarding them). Perf guards: triangle cap
+ the existing 80 MB byte guard; degrade to "geometry too large to analyze" rather than
stall. No heavy deps (no trimesh/Open3D) — keeps the bundle light and license-clean.
*Effort M · risk M (perf on big meshes) · value 2 (enabler).*

**Phase B — Mesh integrity.** Manifold edges, watertightness, consistent/flipped normals,
degenerate + duplicate faces, hole count, basic self-intersection heuristic. Surface as
Validation Center checks + plain-language ("3 holes detected — may print with gaps").
*Effort M · risk L · value 4.*

**Phase C — Printability heuristics.** Overhang % (faces past a threshold angle from +Z) →
"supports likely"; volume + surface area + **honest** material estimate; stability/footprint
+ tall-narrow tip-risk (ties to the Max-Reliability strategy); bed-fit orientation hint.
*Effort M–L · risk M · value 5.*

**Phase D — Surfacing + wiring.** Show results in Design Insights + Validation Center; feed
signals into `strategies.recommend` (e.g. high overhangs/holes → nudge Reliability; supports
→ note). Advanced Mode shows raw metrics. *Effort S–M · risk L · value 4.*

Deferred to ≥v0.6: true wall-thickness (SDF/ray — heavy), auto-orientation suggestion
(compute-heavy), self-intersection at full rigor.

## 5. Prioritized implementation plan

| # | Feature | Phase | Effort | Value | Risk | Depends on |
|---|---|---|---|---|---|---|
| 1 | Indexed-mesh loader (STL+3MF, normals, guards) | A | M | 2 (enabler) | M perf | — |
| 2 | Mesh integrity (manifold/watertight/normals/degenerate/holes) | B | M | 4 | L | #1 |
| 3 | Volume + surface area + material **estimate** | C | S | 3 | L (must label "estimate") | #1 |
| 4 | Overhang % + "supports likely" | C | M | 5 | M (threshold tuning) | #1 |
| 5 | Stability / tip-risk — volumetric center-of-mass vs base **support polygon** (convex hull of footprint); margin to nearest edge | C | S–M | 4 | L | #1 |
| 6 | Bed-fit orientation hint | C | S | 3 | L | existing dims |
| 7 | Surface in Insights/Validation + feed strategy | D | M | 4 | L | #2–#6 |
| 8 | Min-feature vs nozzle (approx thin-wall) | ≥v0.6 | M–L | 4 | H (accuracy) | #1 |

## 6. Low-risk features that can ship incrementally

Independently shippable, each a self-contained read-only add (no conversion change):
- **#6 bed-fit orientation hint** — uses existing bbox; no mesh loader needed. Ship first (S).
- **#3 volume/surface/material estimate** — once #1 lands; clearly labeled estimate.
- **#5 stability/tip-risk** — bbox aspect + base footprint; pairs with the reliability strategy.
- **#2 integrity checks** — additive Validation Center rows; never blocks conversion.

Each adds one Validation Center check / Insights row behind a try/except (best-effort, like
today's geometry reads) so a failure degrades gracefully and never breaks `/insights`.

## 7. Risks + mitigations

- **Perf on large meshes** → triangle cap + byte guard + "too large to analyze" state.
- **Overclaiming** → material/time are **estimates**, labeled; never present as slice-accurate
  (consistent with the no-fake-data rule). Overhang = "likely needs supports," not a guarantee.
- **3MF parser correctness** → reuse the hardened XML parser (`config_io`), unit-test against
  real Bambu/Orca/Prusa `.model` parts before trusting per-face output.
- **Dependency / license** → license facts (from the research catalog): **trimesh = MIT**,
  **Open3D = MIT**, **manifold (elalish) = Apache-2.0** — all license-safe. **ADMesh = GPLv2+**
  and **CGAL-backed libigl modules = GPL** → must NOT be linked. Recommendation: prefer
  **pure-Python** for the simple metrics (overhang dot-product, bbox, volume via signed
  tetrahedra, winding checks), and if a library is justified use **trimesh** (MIT, light,
  numpy-only — bundles cleanly in PyInstaller). **Avoid Open3D** despite its MIT license
  purely on **bundle weight** (large native binary), and avoid ADMesh/CGAL on license. So the
  earlier "no trimesh" stance is relaxed: trimesh is acceptable; the real constraints are
  bundle weight (Open3D) and GPL (ADMesh/CGAL).
- **Scope drift into slicing** → hard line: no toolpaths, no exact time/filament, no auto-orient
  in v0.5.

## 8. Recommendation

Ship in this order for fastest novice value with lowest risk: **#6 → #1 → #2 → #5 → #4 → #3 → #7**.
That front-loads a no-dependency win (orientation hint), then the mesh foundation, then the
two strongest differentiators (integrity warnings, supports prediction) — all slice-free,
cross-ecosystem, U1-aware, and additive to the existing read-only pipeline.

## 9. Research corroboration + sources

A web-research pass (OrcaSlicer / PrusaSlicer / Bambu Studio analysis features, FDM failure
causes, printability tools, mesh-diagnostic libraries) confirms the slice-free shortlist and
the slicing boundary. Headlines:

- **Detection + intent-capture are read-only; realization needs slicing.** Overhang maps,
  paint-on support/seam/color tags, mesh diagnostics, bed-fit, and stability are all
  computable without a slice engine. Toolpaths, structures, MMU segmentation, and exact
  time/filament/cost are slice-time only. Studio can replicate every *diagnostic* (and the
  painting UX) without a slicer.
- **All three slicers warn "non-manifold on import"** — a cheap topology check Studio can do
  too, in plain language, pre-slice.
- **Overhang threshold** convention: <45° clean, 45–60° marginal, >60° support likely (per
  Prusa/Orca defaults) — use as the heuristic's bands.
- **Stability** = gravity-projected center-of-mass exiting the base support polygon (convex
  hull of the footprint); margin = distance to nearest hull edge.
- **Heavy (opt-in only, still slice-free):** auto-orient, auto-arrange/nesting, exact
  medial-axis wall thickness, large-mesh self-intersection.

Primary sources (catalog):
- OrcaSlicer wiki — auto-orient, overhangs, supports, calibration:
  `orcaslicer.com/wiki/print_prepare/prepare_auto_orient`,
  `.../print_settings/quality/quality_settings_overhangs`,
  `github.com/SoftFever/OrcaSlicer` (issues #1188 mesh fix), `.../wiki/Calibration`
- PrusaSlicer — overhang/supports, repair, object info, MMU paint-on:
  `help.prusa3d.com/article/support-material_1698`,
  `.../paint-on-supports_168584`, `.../corrupted-3d-models-for-printing_2205`,
  `.../arachne-perimeter-generator_352769`
- Bambu Studio — plate/object stats, flushing/waste, out-of-bed, non-manifold:
  `wiki.bambulab.com/en/software/bambu-studio/view-slicing-information`,
  `.../reduce-wasting-during-filament-change`
- FDM failure causes: `simplify3d.com/resources/print-quality-troubleshooting/`,
  `help.prusa3d.com/article/layers-and-perimeters_1748`,
  `snapmaker.com/blog/3d-print-warping-cause-and-solution`,
  `3dprinterly.com/how-to-fix-3d-prints-that-keep-falling-over`
- Printability / mesh libs + algorithms: `github.com/mikedh/trimesh` (MIT),
  `open3d.org` (MIT), `github.com/elalish/manifold` (Apache-2.0),
  `admesh.readthedocs.io` (GPL — avoid), `igl.ethz.ch/projects/winding-number`,
  `analysissitus.org/features/features_thickness.html`,
  `en.wikipedia.org/wiki/Support_polygon`

Caveat: a few Simplify3D / Bambu wiki page bodies returned 402/permission during fetch, so
those items are sourced from official URLs + search summaries rather than full-page reads;
classifications there are engineering judgment grounded in those sources.

> No implementation until the plan is approved.
