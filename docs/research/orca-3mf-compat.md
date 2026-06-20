# Snapmaker Orca (OrcaSlicer) 3MF Compatibility — source-verified

Snapmaker Orca is a fork of **OrcaSlicer**. Rules below are verified against
OrcaSlicer's actual reader, `src/libslic3r/Format/bbs_3mf.cpp` (fetched from the
repo), not assumed. Conclusion: **what Studio produces, and the per-plate
remapper's edit, are compatible.**

## What the OrcaSlicer reader requires (and how Studio satisfies it)

| Rule (from bbs_3mf.cpp) | Severity | Studio status |
|---|---|---|
| `3D/3dmodel.model` is **mandatory** (`m_start_part_path.empty() -> return false`) | Hard error if missing | OK — Studio always writes it |
| `_rels/.rels` is **mandatory** (extracted with no fallback) | Hard error if missing | OK — Studio writes it |
| `Metadata/model_settings.config` **required for BBL-family 3MF** (`m_is_bbl_3mf`) | Hard error for our files | OK — Studio writes it (BambuStudio namespace = bbl-family) |
| `project_settings.config`, `slice_info.config`, `[Content_Types].xml` | Optional (no hard error if absent) | OK — Studio writes them |
| `extruder` is **1-based**, parsed as `ConfigOptionInt`; **no bounds check**; missing = silently omitted | — | OK — remapper writes 1-based; we guard range ourselves (dry_run warns if target not in palette) since Orca won't |
| `plater_id` / `object_id` parsed in `_handle_start_config_plater()` | — | OK — remapper maps UI plate by `plater_id`, never object order |
| `p:UUID`, relationships, `[Content_Types].xml` **not strictly re-validated** on load | — | OK — safe to rewrite model_settings.config |
| No whole-zip checksum | — | OK — byte-for-byte copy + single-file edit is safe |
| `slice_info.config` filament list **not cross-checked** against filaments used | — | OK — empty/partial slice_info is fine |

## The remapper edit is confirmed safe
The reader does **not** re-validate UUIDs, relationships, Content_Types, or any
zip checksum during config extraction. Rewriting **only** `model_settings.config`
`<object>` `extruder` values (zip otherwise identical, `.model` meshes and
`paint_color` untouched) therefore opens cleanly in Snapmaker Orca. Painted accents
are preserved because they live in the `.model` files, which we never touch.

## The one real "incompatibility" trap — and it's already handled
The "Customized/Modified Preset" prompt is **not** in the 3MF reader — it lives in
the preset layer (`PresetBundle.cpp` / `Config.cpp`), triggered by per-filament
array inconsistency (e.g. `filament_colour` / `filament_type` lengths and
`flush_volumes_matrix` being N x N for N filaments). Studio's converter already
conforms these on import/repair (`snapstudio_core/filaments.py`
`conform_filament_arrays`), so converted files don't trip it. The per-plate remap
does **not** change filament count or array lengths — it only reassigns an object's
extruder index — so it cannot introduce that inconsistency.

## Fixes needed
**None confirmed.** Studio's produced files and the remapper approach satisfy every
load rule in the OrcaSlicer reader, and the preset-array trap is already conformed
by the converter. The single defensive guard the source implies — Orca does **not**
bounds-check `extruder`, so an out-of-range target would silently misbehave — is
already enforced on our side (remap dry-run rejects/warns on a target filament not
in the palette).

> Verified from OrcaSlicer `main` `src/libslic3r/Format/bbs_3mf.cpp`. Preset-layer
> array rules (`PresetBundle.cpp`/`Config.cpp`) were not re-fetched here; Studio's
> existing conform logic + tests cover them.
