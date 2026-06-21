# Snapmaker Studio — Publication Plan (privacy-first, v1)

> Planning artifact. No files moved, nothing committed. Drafts are proposals for review.

## Guiding principle
Public v1 is a **polished product**, not an engineering notebook. Ship the tool and a
clean README — withhold all design narrative, reverse-engineering history, and the
internal rationale behind the U1 project format. Implementation docs stay private.

## Important caveat (read first)
Open-sourcing `src/` makes the **engine code and its bundled data visible** — that is
inherent to an OSS release. "Hiding implementation details" therefore means:
1. **Do not publish the narrative** (design docs, forensic notes, milestone/experiment history).
2. **Scrub code comments** before release so the source reads as a clean product — remove any
   comment that explains *why* in terms of the import dialog, the discovery process, experiment
   names, competitor tools, or personal sample files. Keep comments purely functional.
3. Accept that the bundled U1 profile data ships with the engine (it is needed at runtime).
   If that data must stay secret, the engine cannot be open-sourced as-is — flag for a decision.

If full trade-secret protection of the format knowledge is required, the alternative is to
publish only a CLI/wrapper and keep the engine private. Current plan assumes OSS engine + scrubbed narrative.

---

## 1. Public repository (v1) — minimal & polished

```
snapmaker-studio/
├── README.md            # value, features, usage, roadmap — NO implementation details
├── LICENSE              # MIT
├── CHANGELOG.md         # starts at 0.1.0
├── pyproject.toml       # packaging (root)
├── src/
│   ├── snapstudio_core/ # engine (comments scrubbed to functional-only)
│   └── u1convert/       # CLI
└── examples/            # ONLY synthetic / public-domain assets
    ├── sample_cube.stl          # generated unit cube, no provenance
    └── sample_cube_U1.3mf       # its converted output
```

NOT in public v1:
- `tests/` — excluded until fully sanitised (no personal paths/model names) and reviewed
- any `docs/` engineering content (architecture, compatibility, stl-conversion, repair-engine, faq)
- `docs/plans/`, `docs/validation/`, `docs/research/`, `docs/specs/`
- this publication plan
- `.code-review-graph/`, empty placeholder dirs

A short user-facing CONTRIBUTING/SECURITY may be added later; v1 keeps the root lean.

---

## 2. Private / internal repository — full working record

Keep the current repository private and complete:

```
snapmaker-studio-internal/        (private)
├── src/  (or backend/)           # mirror of the public engine + CLI
├── tests/                        # full suite incl. env-gated real-sample fixtures
├── docs/
│   ├── architecture.md           # internal design
│   ├── compatibility.md
│   ├── stl-conversion.md         # format internals
│   ├── repair-engine.md
│   ├── faq.md
│   ├── plans/                    # milestone roadmaps
│   ├── validation/               # Orca-validation + format investigation notes
│   ├── research/                 # ecosystem / competitive analysis
│   ├── specs/                    # kernel/architecture specs
│   └── publication-plan.md
├── internal-notes/               # reverse-engineering record, format findings
└── .code-review-graph/
```

Publishing model: the public repo is a **curated subset** of the private one (manual export
of the scrubbed `src/` + product files), not a history-preserving fork — so the public git
history never contains the internal docs or investigation commits.

---

## 3. README.md (public draft) — implementation-free

# Snapmaker Studio

**The compatibility layer for Snapmaker U1.**

Convert, repair, and validate 3D print projects for the Snapmaker U1 — with your
geometry, painting, and colours kept intact.

## Why
Files exported from popular slicers don't always open cleanly on the Snapmaker U1.
Snapmaker Studio bridges that gap: drop in a model and get a project that loads and
slices on the U1, without losing detail, painted regions, or multi-colour assignments.

## Features
- Repair incompatible 3MF projects so they open on the U1
- Convert projects into native Snapmaker U1 format
- Generate ready-to-slice U1 projects directly from STL
- Keep painted models intact
- Keep multi-colour projects intact
- Validate that a project is well-formed before you print

## Install
    pip install snapmaker-studio

## Usage
    # Make an existing 3MF U1-ready
    u1convert repair model.3mf --mode u1 -o model_U1.3mf

    # Convert an STL into a U1 project
    u1convert repair part.stl -o part_U1.3mf

    # Validate a project
    u1convert validate part_U1.3mf

Open the result in Snapmaker Orca and slice.

## Roadmap
- OBJ and GLB conversion
- Batch processing
- Desktop / GUI application
- Automatic compatibility analysis
- Optional cloud conversion service

## License
MIT

(README contains zero internal terms — no filament-schema, flush, project-settings,
object-mapping, milestone, experiment, or sample-file references.)

---

## 4. Pre-release scrub checklist (must pass before any public push)
Remove every occurrence of the following from public files (code + README + examples):
- minimum-filament / slot-count schema rules
- flush matrices / purge tables
- `project_settings` internal field names and structure
- object-mapping / model-structure internals
- experiment names (expG / expH / expI and similar)
- personal / commercial validation model names and any paid-fixture filenames
- reverse-engineering / forensic / investigation history
- milestone tags (M1, M1.1f, …)
- competitor tool names used as references
- any local absolute paths or usernames

Verification: grep the public subset for each term; manual review of every code comment in
`src/`; confirm `examples/` assets are synthetic/public-domain with no provenance metadata.

---

## 5. Suggested phases (after approval)
1. Phase 1 (this doc): privacy-first plan + README. DONE
2. Phase 2: scrub `src/` code comments to functional-only; add root `README.md`, `LICENSE` (MIT), `CHANGELOG.md`, `pyproject.toml`.
3. Phase 3: generate synthetic `examples/`; run the scrub checklist grep + manual review.
4. Phase 4 (optional): sanitise `tests/` (env-var samples + synthetic fixtures) and add them.
5. Phase 5: create the public GitHub repo and push the curated subset (explicit user action).
