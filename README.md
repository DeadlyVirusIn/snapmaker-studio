<p align="center"><img src="docs/brand/hero.svg" alt="Snapmaker Studio" width="100%"></p>

# Snapmaker Studio

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)
![Release](https://img.shields.io/github/v/release/DeadlyVirusIn/snapmaker-studio?display_name=tag)
![Status: beta](https://img.shields.io/badge/status-beta-orange.svg)

**The Operating System for Multi-Material 3D Printing.**

_One place. Any file. Any printer. Perfect prints._

Drop in a model from any ecosystem — Bambu, OrcaSlicer, PrusaSlicer, or raw STL —
and get a clean, **validated** Snapmaker U1 project. A polished desktop app (and a
scriptable engine + CLI) that keep your geometry, painting, and colours intact.

**Input → Diagnose → Transform → Validate → Output.** Validation is always on:
every conversion is proven clean before you print (real-world corpus: 112 files,
100%).

Runs entirely on your machine. No cloud, no account, no upload — local-first and
open source.

## Why

Models and projects from popular slicers and model sites don't always open cleanly
on the Snapmaker U1. Snapmaker Studio closes that gap: point it at a file and get a
project that loads and slices on the U1 — without losing detail, painted regions, or
multi-colour assignments.

## What makes it different

- **Local-first.** A single CLI and a reusable engine. Script it, automate it, or
  build it into your own tools — nothing leaves your computer.
- **STL → native U1.** Not just project repair: turn a plain `.stl` straight into a
  ready-to-slice native U1 project.
- **Preservation-first.** Geometry, painting, and colour are kept faithfully.
  Snapmaker Studio never silently drops colours or detail — and when it can't
  guarantee a faithful result, it stops and tells you why.
- **Validates and reports.** Every output can be checked for integrity, and repairs
  record exactly what changed.

## Features

- Repair incompatible 3MF projects so they open on the U1
- Convert projects into native Snapmaker U1 format
- Generate ready-to-slice U1 projects directly from STL
- Diagnose any file with `doctor` — will it load on the U1, and if not, why
- Compare two projects with `diff` — see exactly what changed
- Preserve painted and multi-colour models
- Validate that a project is well-formed before you print
- Optional, reversible print-optimization profiles

## Compatibility

| Input | Status | Result |
|---|---|---|
| Bambu / Orca `.3mf` project | ✅ supported | repaired → Snapmaker U1 `.3mf` |
| `.stl` model | ✅ supported | native Snapmaker U1 `.3mf` |
| `.obj` / `.glb` | 🚧 planned | — |

Output target: **Snapmaker U1**. Open the result in Snapmaker Orca to slice.

## Quick start (30 seconds)

Install from source (PyPI package coming later):

```bash
pip install -e backend
```

Then, using the bundled example:

```bash
# Convert the example STL into a native U1 project
u1convert repair examples/sample_cube.stl -o my_part_U1.3mf

# Check any file's U1 compatibility first
u1convert doctor examples/sample_cube_U1.3mf
```

Open the result in **Snapmaker Orca** and slice. More samples live in
[`examples/`](examples/).

Everyday commands:

```bash
u1convert repair model.3mf --mode u1 -o model_U1.3mf   # make a 3MF U1-ready
u1convert validate model_U1.3mf                        # check integrity
```

## Will my file work on the U1?

`doctor` is a read-only check — it never modifies your file:

```text
$ u1convert doctor model.3mf

  Verdict : REPAIRABLE
  Score   : 90/100
  Project type            : Bambu/Orca project
  Snapmaker U1 compatible : yes
  U1 compatibility        :
    - incompatible slicer value: wall_filament=0

Recommended action: Run `u1convert repair <file> --mode u1` to make this U1-ready.
Read-only check - no files were modified.
```

Verdicts: **READY** (loads as-is) · **REPAIRABLE** (run `repair`) · **CONVERTIBLE** (an STL — run `repair`) · **HIGH_RISK** (not a usable project). Add `--json` for machine-readable output.

## What changed between two projects?

`diff` is a read-only comparison — handy to see what a repair or conversion actually changed:

```text
$ u1convert diff original.3mf converted.3mf

  Structure : +2 parts / -0
  Geometry  : unchanged
  Objects 1->1  Plates 1->1  Filaments 4->5
  Painting  : 0 -> 0 painted triangles
  Settings  : 37 changed, 0 added, 0 removed
    printer_model: 'Bambu Lab P1S' -> 'Snapmaker U1'
    ... (use --json for the full list)
```

It reports structure, geometry, settings, and counts. Add `--json` for the full machine-readable diff.

## Roadmap

- OBJ and GLB conversion
- Batch processing (folders / many files)
- Desktop / GUI application
- A stable API for integration
- Automatic compatibility analysis
- Optional cloud conversion service

See [CHANGELOG.md](CHANGELOG.md) for release history.

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
