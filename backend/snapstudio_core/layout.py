"""Layout / plate-readiness checks for a 3MF (beta.18.4).

Profile compatibility is NOT the same as print readiness: a file can carry clean U1
settings yet still have objects placed outside the build plate (Orca's "out of bounds").
This module reads each placed object's *real* transformed bounding box (via
geometry.build_item_dims) and reports whether the arrangement is plate-ready.

Honest by construction: it only claims `pass` when it can actually verify the layout.
Multi-plate projects can't be fully verified from world-space bounds alone (per-plate
local coordinates aren't reconstructed here), so they return `warn`, never a false pass.
"""
from __future__ import annotations

from .geometry import build_item_dims
from .intelligence import project_info

# Snapmaker U1 printable area (mm). Square bed; the same value guards X and Y.
U1_PLATE_MM = 270.0


def plate_window(items: list) -> tuple:
    """Pick ONE plate coordinate window for a file, from all objects' collective bounds.

    3MF origin conventions differ — corner-origin (0..270) or centred (-135..135). We must
    NOT accept "either" per object: an object off-plate in the corner system would falsely
    pass via the centred window (and vice-versa). Decide once for the whole file: if any
    object's min X/Y is meaningfully negative, the file is centred; otherwise corner-origin.
    Returns (low, high) for both axes (square bed).
    """
    min_xy = min(min(it["bounds"]["min"][0], it["bounds"]["min"][1]) for it in items)
    if min_xy < -1.0:                      # centred convention
        return (-U1_PLATE_MM / 2.0, U1_PLATE_MM / 2.0)
    return (0.0, U1_PLATE_MM)              # corner-origin convention


def assess_layout(path: str) -> dict:
    """Return {status, plates, object_count, messages}.

    status: "pass" | "warn" | "fail" | "unknown"
      - fail    : an object is larger than the plate, or the single-plate arrangement
                  spans wider than the plate (objects sit outside the build area).
      - warn    : multi-plate project — can't fully verify each plate from the file.
      - unknown : no placement data could be read.
      - pass    : every object read fits within one plate.
    """
    items = build_item_dims(path)
    info = project_info(path)
    plates = int(info.get("plates") or 1)

    if not items:
        return {
            "status": "unknown",
            "plates": plates,
            "object_count": 0,
            "messages": [
                "Studio couldn't read object placement from this file — open it in "
                "Snapmaker Orca and use Arrange all plates to check the layout before slicing."
            ],
        }

    messages: list[str] = []
    status = "pass"

    oversized = [
        it for it in items
        if it["dimensions"]["x"] > U1_PLATE_MM or it["dimensions"]["y"] > U1_PLATE_MM
    ]

    if plates > 1:
        # World-space bounds across many plates don't tell us per-plate placement, so we
        # can't certify it — but we won't pretend it's clean either.
        status = "warn"
        messages.append(
            f"Multi-plate project ({plates} plates) — Studio can't fully verify each plate's "
            "object positions from the file. Open in Snapmaker Orca and use Arrange all plates "
            "before slicing; objects may sit outside a plate."
        )
    else:
        wlo, whi = plate_window(items)
        m = 1.0  # mm tolerance
        off = [
            it for it in items
            if it["bounds"]["min"][0] < wlo - m or it["bounds"]["max"][0] > whi + m
            or it["bounds"]["min"][1] < wlo - m or it["bounds"]["max"][1] > whi + m
        ]
        if off:
            status = "fail"
            messages.append(
                f"{len(off)} object(s) sit outside the U1 build plate ({int(U1_PLATE_MM)} mm). "
                "Open in Snapmaker Orca and use Arrange all plates before slicing."
            )

    if oversized:
        status = "fail"
        messages.append(
            f"{len(oversized)} object(s) are larger than the U1 build plate ({int(U1_PLATE_MM)} mm) "
            "— scale down or split before printing."
        )

    if status == "pass":
        messages.append(f"All {len(items)} object(s) fit within the U1 build plate.")

    return {"status": status, "plates": plates, "object_count": len(items), "messages": messages}
