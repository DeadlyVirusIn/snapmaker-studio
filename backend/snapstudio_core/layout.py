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
        # Absolute position: each object must lie inside the plate window. 3MF origin
        # conventions vary (corner 0..270 vs centred -135..135), so accept EITHER —
        # an object outside both windows is genuinely off the plate.
        m = 1.0  # mm tolerance
        half = U1_PLATE_MM / 2.0

        def within(lo: float, hi: float) -> bool:
            corner = lo >= -m and hi <= U1_PLATE_MM + m
            centred = lo >= -half - m and hi <= half + m
            return corner or centred

        off = [
            it for it in items
            if not (within(it["bounds"]["min"][0], it["bounds"]["max"][0])
                    and within(it["bounds"]["min"][1], it["bounds"]["max"][1]))
        ]
        xs = [it["bounds"]["min"][0] for it in items] + [it["bounds"]["max"][0] for it in items]
        ys = [it["bounds"]["min"][1] for it in items] + [it["bounds"]["max"][1] for it in items]
        span_x, span_y = max(xs) - min(xs), max(ys) - min(ys)
        if off:
            status = "fail"
            messages.append(
                f"{len(off)} object(s) sit outside the U1 build plate ({int(U1_PLATE_MM)} mm). "
                "Open in Snapmaker Orca and use Arrange all plates before slicing."
            )
        elif span_x > U1_PLATE_MM or span_y > U1_PLATE_MM:
            status = "fail"
            messages.append(
                f"Objects span {round(span_x)} × {round(span_y)} mm — wider than the U1 plate "
                f"({int(U1_PLATE_MM)} mm). One or more objects sit outside the build plate; "
                "rearrange or split in Snapmaker Orca."
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
