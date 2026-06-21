# Snapmaker U1 Compatibility Troubleshooting

A short checklist for common errors people hit when slicing Snapmaker U1
projects in Snapmaker Orca / Snorca / OrcaSlicer-family slicers. These are
community-reported issues. The goal here is to explain what each error usually
means and the safest next step — not to auto-fix anything.

If your slice preview is missing the bottom layer or otherwise looks wrong,
stop and fix the profile/settings before printing. A bad preview is a signal,
not a cosmetic glitch.

## 1. "Invalid values found in the 3MF"

You may see one or more lines like:

```
prime_tower_brim_width: -1 not in range [0,2147483647]
raft_first_layer_expansion: -1 not in range [0,2147483647]
solid_infill_filament: 0 not in range [1,2147483647]
sparse_infill_filament: 0 not in range [1,2147483647]
tree_support_wall_count: -1 not in range [0,2]
wall_filament: 0 not in range [1,2147483647]
```

### What it usually means

This almost always means the 3MF is carrying slicer/profile settings from a
different printer or a stale profile — often a MakerWorld / Flexi Factory /
Bambu-style project file. The model geometry is frequently fine; the embedded
project settings are the problem.

### Safe steps

Make sure your active printer profile is **Snapmaker U1** before slicing.
Prefer importing or adding the model into a clean Snapmaker U1 project rather
than opening the foreign 3MF as the active project — that way you keep your own
known-good settings instead of inheriting the file's. If the error still shows
up after updating or reinstalling, back up your presets first, then carefully
reset the Snapmaker Orca / Snorca configuration. And don't dismiss the warning
if the resulting slice is missing layers or looks wrong — that means the bad
settings actually took effect.

## 2. Relative extruder addressing / "G92 E0" warning

You may see:

```
Relative extruder addressing requires resetting the extruder position at each
layer to prevent loss of floating point accuracy. Add 'G92 E0' to layer_gcode.
```

### What it usually means

The printer profile uses relative extrusion, but the layer-change g-code may
not reset the extruder position each layer. Newer Orca / Snorca versions are
stricter about flagging this.

### Safe steps

Confirm the active printer is **Snapmaker U1**. Then check Printer Settings →
Machine G-code → Layer change G-code (and Before layer change G-code). Add or
verify `G92 E0` only if the profile genuinely uses relative extrusion and you
understand the setting. The safer path for beginners is to switch back to the
official Snapmaker U1 profile, or reset the profile, rather than hand-editing
g-code.

## Where Snapmaker Studio fits

Snapmaker Studio is not a replacement for Orca / Snorca. It will not re-slice
for you and it does not auto-fix these errors today. What it can do is diagnose
the issue and explain the safest next step. A future Compatibility Doctor is
planned to detect these specific errors **read-only** and give exact guidance —
but that is not shipped yet, so for now treat the steps above as manual checks.

## Related

- [Snapmaker Orca 3MF compatibility (source-verified)](research/orca-3mf-compat.md)
- [Plate color remap](plate-color-remap.md)
