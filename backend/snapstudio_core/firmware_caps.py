"""Firmware Capability Intelligence — read what THIS U1's firmware can actually do.

The U1 is open Klipper/Moonraker, so its loaded object list is a truthful manifest
of real features: mesh levelling, input shaping, eddy-current probing, runout
sensing, object exclusion, pause/resume, multi-toolhead, and any custom macros the
owner (or extended/community firmware) has added. This turns that raw list into a
plain-language capability set, and flags when the firmware looks extended beyond
stock.

Read-only and honest: it reports only what the object list proves is present, and
never claims a capability it can't see.
"""
from __future__ import annotations

SCHEMA_VERSION = "firmwarecaps/1"

# Stock U1 firmware exposes a handful of gcode_macros; well beyond that suggests
# the owner or a community/extended firmware has added their own.
_EXTENDED_MACRO_THRESHOLD = 15


def _prefix(obj: str) -> str:
    """Klipper objects are 'kind' or 'kind name' — return the kind."""
    return obj.split(" ", 1)[0].strip().lower()


def interpret(objects, toolhead_count=None, bed_mm=None) -> dict:
    """Map a klipper object list to a plain-language capability set.

    objects: the GET /printer/objects/list result (a list of strings).
    toolhead_count, bed_mm: already-derived values from capabilities(), if known.
    """
    objs = [str(o) for o in (objects or [])]
    if not objs:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "no firmware object list available from this printer"}

    kinds = [_prefix(o) for o in objs]
    kindset = set(kinds)
    has = lambda *names: any(k in kindset for k in names)
    has_prefix = lambda p: any(k.startswith(p) for k in kinds)

    features: list[dict] = []

    if has("bed_mesh"):
        features.append({"name": "Automatic bed mesh levelling",
                         "detail": "compensates for an uneven bed across the whole plate"})
    if has_prefix("probe_eddy_current") or has("eddy", "probe_eddy_current"):
        features.append({"name": "Eddy-current bed probing",
                         "detail": "the U1's contactless, fast auto-levelling probe"})
    elif has("probe", "bltouch"):
        features.append({"name": "Auto bed probing", "detail": "automatic Z/level probing"})
    if has("input_shaper"):
        features.append({"name": "Input shaping",
                         "detail": "resonance compensation for cleaner walls at speed"})
    if has("exclude_object"):
        features.append({"name": "Object exclusion",
                         "detail": "cancel one failed object mid-print without losing the rest"})
    if has("pause_resume"):
        features.append({"name": "Pause / resume", "detail": "safely pause and continue a print"})

    runout = [k for k in kinds if k in ("filament_switch_sensor", "filament_motion_sensor")]
    if runout:
        features.append({"name": "Filament runout detection",
                         "detail": "stops the print if filament runs out or jams"})

    macro_count = sum(1 for k in kinds if k == "gcode_macro")
    if macro_count:
        features.append({"name": "Custom macros",
                         "detail": f"{macro_count} gcode macro{'s' if macro_count != 1 else ''} on this printer"})

    tc = toolhead_count or sum(1 for k in kinds if k == "extruder" or
                               (k.startswith("extruder") and k[8:].isdigit()))
    if tc and tc > 1:
        features.append({"name": f"{tc}-toolhead multimaterial",
                         "detail": f"prints up to {tc} colours/materials in one job"})

    extended = macro_count >= _EXTENDED_MACRO_THRESHOLD

    bed_txt = (f"{bed_mm['x']}×{bed_mm['y']}×{bed_mm['z']} mm bed"
               if isinstance(bed_mm, dict) and bed_mm.get("x") else None)
    head_txt = f"{tc} toolhead{'s' if (tc or 0) != 1 else ''}" if tc else None
    bits = [b for b in (head_txt, bed_txt) if b]
    summary = ("Your U1 reports " + ", ".join(bits) + "; " if bits else "Your U1 reports ") + \
              f"{len(features)} capabilit{'ies' if len(features) != 1 else 'y'} detected" + \
              (" (firmware looks extended beyond stock)." if extended else ".")

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "toolhead_count": tc or None,
        "bed_mm": bed_mm,
        "macro_count": macro_count,
        "extended_firmware": extended,
        "features": features,
        "summary": summary,
    }
