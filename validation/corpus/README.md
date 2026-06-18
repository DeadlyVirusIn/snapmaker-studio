# Validation corpus

This folder defines the **classification scheme** for the conversion test corpus.
The actual `.3mf` / `.stl` files are **not committed** — they are large (tens to
hundreds of MB) and frequently personal. The validator
(`validation/validate_corpus.py`) is pointed at a local directory of real files
and references them by path; it converts a temp copy of each (never touching the
source) and writes `validation/report.md`.

## Classes the validator auto-detects per file
| Class | How it's detected |
|---|---|
| **Bambu/Orca** | `project_settings.config` `printer_model` is non-empty and not "Snapmaker U1" |
| **Snapmaker U1** | `printer_model == "Snapmaker U1"` (already-U1 input) |
| **STL** | `.stl` extension (wrapped, not repaired) |
| **Single-color** | `len(filament_colour) <= 1` |
| **Multi-color** | `len(filament_colour) > 1` |
| **Large** | file size (reported in MB in the report) |
| **Custom preset** | non-empty `different_settings_to_system` |

## Running
```
python validation/validate_corpus.py --input "D:/STL Files" --report validation/report.md
```
Already-converted artifacts (`*_SnapmakerU1`, `*_FIXED`, `*.orig`, stock/sample,
`*_U1.`) are skipped so only genuine source inputs are measured.

## Failure categories
`Identity`, `Filament`, `Preset`, `Geometry`, `Thumbnail`, `Slice metadata`, `Unknown`
— see `validation/report.md` for the latest run, success rate, and top patterns.
