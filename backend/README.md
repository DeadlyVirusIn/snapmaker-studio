# Snapmaker Studio — backend

Python engine (`snapstudio_core`) and command-line tool (`u1convert`) for Snapmaker Studio.
For the product overview, see the [project README](../README.md).

## Install

```bash
pip install -e ".[dev]"
```

## Test

```bash
pytest
```

## CLI

```bash
# Inspect a project (source, printer, object/colour counts)
u1convert inspect model.3mf

# Repair an incompatible 3MF so it opens on the U1 (default mode)
u1convert repair model.3mf -o model_U1.3mf

# Convert an STL into a native U1 project
u1convert repair part.stl -o part_U1.3mf

# Validate a project's integrity
u1convert validate model_U1.3mf

# Check U1 compatibility (read-only diagnosis)
u1convert doctor model.3mf

# Preview without writing anything
u1convert repair model.3mf --dry-run

# Apply a reversible optimization profile
u1convert repair model.3mf --mode optimize --opt-profile u1_fast_prime_tower
```

Repairs write the output project, a backup beside the source, and a `FIX_REPORT.json`
summarising what changed, then auto-validate the result. Open the output in Snapmaker
Orca to slice.

## Layout

- `snapstudio_core/` — the engine (file handling, repair, conversion, validation, optimization). Pure Python; no network or UI dependencies.
- `u1convert/` — the command-line interface.
