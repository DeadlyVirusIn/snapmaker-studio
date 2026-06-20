"""Bed-Fit / Out-of-Bounds Doctor — the #1 cryptic U1 failure, explained.

When a model is too big or badly placed, Snapmaker Orca refuses to slice with a
bare "out of bounds" and no reason — the single most common U1 friction in the
community, usually answered with "ask Facebook". This catches it BEFORE Orca, from
the model's geometry vs the U1 bed, and says exactly what's wrong and how to fix
it: the precise scale-to-fit percentage, a rotate suggestion when the diagonal
fits, a height/split warning, and — in multi-material mode — whether there's room
left for the prime/wipe tower.

Read-only and offline-capable: it uses the connected U1's REAL bed when known, else
the Snapmaker U1's published 220-class printable volume. Honest: it explains only
what the geometry proves, and returns unavailable when there are no dimensions.
"""
from __future__ import annotations

SCHEMA_VERSION = "bedfit/1"

# Snapmaker U1 printable volume, from data/profiles/snapmaker_u1.json
# (printable_area 0.5→270.5 / 1→271, printable_height 270.05).
U1_BED = {"x": 270.0, "y": 270.0, "z": 270.0}

# A typical multi-material prime/wipe tower footprint side (mm) — the clearance the
# model must leave on the plate or Orca pushes the tower out of bounds.
PRIME_TOWER_MM = 55.0

# Fraction of the bed above which a footprint is "almost the whole plate" — skirt /
# brim / tower can then spill over the edge even though the part itself fits.
EDGE_FRAC = 0.95


def _f(level: str, text: str) -> dict:
    return {"level": level, "text": text}


def assess(dims, bed=None, bed_known: bool = False, object_count: int = 1,
           multi_material: bool = False) -> dict:
    """Diagnose whether a model fits the U1 bed and explain any "out of bounds".

    dims: object bounding box {x, y, z} in mm (from geometry).
    bed:  the printer's real bed {x, y, z}; falls back to the known U1 bed.
    bed_known: True when `bed` came from a connected printer.
    object_count: parts on the plate (the whole arrangement must fit).
    multi_material: reserve prime/wipe-tower clearance when True.
    """
    if not dims or any(dims.get(k) is None for k in ("x", "y", "z")):
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "no model dimensions available to check against the bed"}

    x, y, z = float(dims["x"]), float(dims["y"]), float(dims["z"])
    b = bed if (bed and all(bed.get(k) for k in ("x", "y", "z"))) else U1_BED
    bx, by, bz = float(b["x"]), float(b["y"]), float(b["z"])
    source = "your connected U1" if bed_known else "the Snapmaker U1"

    findings: list[dict] = []
    fixes: list[str] = []
    worst = "ok"

    def bump(level: str) -> None:
        nonlocal worst
        order = {"ok": 0, "warn": 1, "risk": 2}
        if order[level] > order[worst]:
            worst = level

    over_x, over_y, over_z = x > bx, y > by, z > bz

    # Too tall — the U1 can't reach the height.
    if over_z:
        bump("risk")
        findings.append(_f("risk", f"Taller than the U1 can print: {z:.0f} mm vs the "
                                   f"{bz:.0f} mm max height — Orca reports this as out of bounds. "
                                   f"Scale to {bz / z * 100:.0f}% or split it into shorter parts."))
        fixes.append(f"Scale to {bz / z * 100:.0f}% to fit the height, or split into parts.")

    # Too big in X/Y — the actual "out of bounds" most people hit.
    if over_x or over_y:
        bump("risk")
        scale_pct = min(bx / x, by / y) * 100.0
        findings.append(_f("risk", f"Too big for the bed: {x:.0f}×{y:.0f} mm on a "
                                   f"{bx:.0f}×{by:.0f} mm bed — this is the “out of bounds” error "
                                   f"Orca shows without saying which way. Scale to {scale_pct:.0f}% to fit."))
        fixes.append(f"Scale to {scale_pct:.0f}% so it fits the {bx:.0f}×{by:.0f} mm bed.")
        diag = (x + y) / (2 ** 0.5)
        if (over_x ^ over_y) and diag <= min(bx, by):
            fixes.append(f"Or rotate it ~45° on the plate — the diagonal ({diag:.0f} mm) fits within the bed.")

    # Almost the whole plate — fits, but brim/skirt/tower can spill over.
    elif x > bx * EDGE_FRAC or y > by * EDGE_FRAC:
        bump("warn")
        findings.append(_f("warn", f"Fills almost the whole bed ({x:.0f}×{y:.0f} of "
                                   f"{bx:.0f}×{by:.0f} mm) — a skirt, brim, or prime tower can spill "
                                   f"past the edge and trigger out of bounds."))
        fixes.append("Center the model, drop the brim/skirt, or scale down slightly.")

    # Multi-material: is there room for the prime/wipe tower?
    if multi_material and not (over_x or over_y):
        mx, my = bx - x, by - y
        if mx < PRIME_TOWER_MM and my < PRIME_TOWER_MM:
            bump("warn")
            findings.append(_f("warn", f"No room for the multi-material prime/wipe tower "
                                       f"(~{PRIME_TOWER_MM:.0f} mm): only {mx:.0f}×{my:.0f} mm is free, so "
                                       f"Orca may push the tower off the bed (out of bounds)."))
            fixes.append("Shrink the model a little, or reduce the prime-tower size/brim in Orca.")

    # Multiple parts share the plate — the arrangement must fit, not just one part.
    if object_count and object_count > 1:
        findings.append(_f("ok", f"{object_count} objects share the plate — the whole "
                                 f"arrangement must fit. If Orca still says out of bounds, one object "
                                 f"is off the plate; use Arrange to re-pack them."))

    if worst == "ok" and not any(f["level"] != "ok" for f in findings):
        findings.insert(0, _f("ok", f"Fits {source}'s {bx:.0f}×{by:.0f}×{bz:.0f} mm bed "
                                     f"with room to spare ({x:.0f}×{y:.0f}×{z:.0f} mm)."))

    overall_text = {
        "ok": "This model fits the U1 bed.",
        "warn": "It fits, but the edges are tight — see below before slicing.",
        "risk": "It won't fit as-is — this is the out-of-bounds error, with the fix below.",
    }[worst]

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "bed_known": bool(bed_known),
        "bed_source": source,
        "bed_mm": {"x": bx, "y": by, "z": bz},
        "dims_mm": {"x": round(x, 1), "y": round(y, 1), "z": round(z, 1)},
        "overall_level": worst,
        "overall_text": overall_text,
        "findings": findings,
        "fixes": fixes,
    }
