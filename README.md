# Snapmaker Studio

**The compatibility layer for Snapmaker U1.**

Convert, repair, validate, and optimize 3D print projects for the Snapmaker U1 —
with your geometry, painting, and colours kept intact.

Runs entirely on your machine. No cloud, no account, no upload, no browser
extension, no Docker — just a command-line tool (and a Python library you can
build on).

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
- Preserve painted and multi-colour models
- Validate that a project is well-formed before you print
- Optional, reversible print-optimization profiles

## Quick start

Install from source (a published `pip install snapmaker-studio` is on the roadmap):

```bash
pip install -e backend
```

Then:

```bash
# Make an existing 3MF U1-ready
u1convert repair model.3mf --mode u1 -o model_U1.3mf

# Convert an STL into a native U1 project
u1convert repair part.stl -o part_U1.3mf

# Validate a project
u1convert validate part_U1.3mf
```

Open the result in **Snapmaker Orca** and slice. A ready-made example lives in
[`examples/`](examples/).

## Roadmap

- OBJ and GLB conversion
- Batch processing (folders / many files)
- Desktop / GUI application
- A stable API for integration
- Automatic compatibility analysis
- Optional cloud conversion service

See [CHANGELOG.md](CHANGELOG.md) for release history.

## License

[MIT](LICENSE)
