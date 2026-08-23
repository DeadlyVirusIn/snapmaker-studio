# Real-world 3MF fixtures — provenance

Studio's 3MF reader was, until this point, tested entirely against archives the
test suite built itself. Those prove the logic; they do not prove the reader
survives what real slicers actually write. This file records the real files it is
now tested against, where each came from, and why some are fetched rather than
committed.

Two rules govern what is committed here:

1. **Licence.** A fixture is only committed when its licence plainly permits
   redistribution and does not impose copyleft on this repository.
2. **Privacy.** Studio's own rules forbid private paths and usernames in tracked
   files. That applies to files it inherits, not only files it writes.

Everything else is fetched from its original source at test time by
`fetch_real_world.py` and never enters the repository.

---

## Nothing is committed

No real-world fixture is checked into this repository. Permissively-licensed
conformance files were identified and would have been safe to commit —
BSD-2-Clause fixtures from [lib3mf](https://github.com/3MFConsortium/lib3mf),
[3mf-samples](https://github.com/3MFConsortium/3mf-samples) and
[go3mf](https://github.com/HPInc/go3mf), including lib3mf's known
denial-of-service regression file — but they are geometry-only conformance
archives, and Studio's synthetic suite already covers that ground thoroughly.

What the synthetic suite could not cover is *real slicer output*, and every file
that provides it is AGPL-3.0. Those are fetched instead. Adding the permissive
conformance set later is a worthwhile extension, recorded here so the option is
not lost.

## Fetched at test time — not committed

These are genuine slicer *project* files: `Metadata/project_settings.config`,
`model_settings.config`, `slice_info.config`, per-plate thumbnails, production
splits. They are what Studio actually has to read in the field.

They are **not** committed for two independent reasons:

- **Licence.** All are AGPL-3.0 (OrcaSlicer, BambuStudio and PrusaSlicer are all
  AGPL). Redistribution is permitted, but vendoring copyleft data into an MIT
  repository is an entanglement worth avoiding when a fetch costs nothing.
- **Privacy.** `auto_pa_line_dual.3mf` embeds an upstream developer's local path
  including their username. Studio's own rules forbid that in tracked files, and
  inheriting it would break the rule just as surely as writing it.

| File | Upstream | Licence | Why it matters |
|---|---|---|---|
| `orca-pa-line-dual.3mf` | OrcaSlicer `resources/calib/pressure_advance/auto_pa_line_dual.3mf` | AGPL-3.0 | A real multi-material Orca project: 8 external object parts, 64 KB of project settings, per-object extruder assignments |
| `orca-badge.3mf` | OrcaSlicer `resources/handy_models/OrcaBadge.3mf` | AGPL-3.0 | Spaces in part names, a `filament_sequence.json`, and a 6-byte `project_settings.config` — a genuine empty-settings edge case |
| `bambu-pa-pattern.3mf` | BambuStudio `resources/calib/pressure_advance/pa_pattern.3mf` | AGPL-3.0 | 90 KB of `custom_gcode_per_layer.xml` — real per-layer colour-change records, which the colour planner reads |
| `prusa-seam-test.3mf` | PrusaSlicer `tests/data/seam_test_object.3mf` | AGPL-3.0 | The other dialect: `Metadata/Slic3r_PE.config`, INI-ish rather than JSON |

## Fetching them

```bash
cd backend
python tests/fixtures/fetch_real_world.py          # downloads and verifies
python -m pytest tests/test_real_world_3mf.py -q   # skipped without them
```

The tests skip cleanly when the fixtures are absent, so a clone with no network
still has a green suite. CI does not fetch them; they are for local and
pre-release verification.

Each download is checked against a pinned SHA-256 recorded in
`fetch_real_world.py`. A mismatch fails rather than being used.

---

## Deliberately excluded

Public repositories carrying *downloaded models* — including U1 projects taken
from model sites — were found and rejected. A repository's MIT licence does not
cover the copyright of a model someone else authored, and Studio's rules forbid
private or copyrighted model names in tracked files. Fixtures here are test
resources published as test resources.
