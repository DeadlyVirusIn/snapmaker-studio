"""Scale Doctor — analysis-only resize preview (read-only).

Uniform scaling only. This module loads a mesh, computes its bounding box and
solid volume, and reports what a uniform scale would do: new size, U1 build-volume
fit, and material/cost deltas. It NEVER writes a file, mutates the source, or
exports — it is preview/advice only and uses hedged language ("likely safe",
"caution", "not recommended"), never guarantees.
"""
from __future__ import annotations

import math
import re

from .geometry import load_mesh, build_item_dims
from .bed_fit import U1_BED
from .cost_estimate import estimate as cost_estimate
from .container import ThreeMF

_MODEL_SETTINGS = "Metadata/model_settings.config"

SCHEMA_VERSION = 1
# Solid-volume material model (no infill modelled): PLA ~1.24 g/cm^3.
_PLA_DENSITY = 1.24


def _bbox_dims(verts) -> dict | None:
    if not verts:
        return None
    xs = [v[0] for v in verts]; ys = [v[1] for v in verts]; zs = [v[2] for v in verts]
    return {"x": max(xs) - min(xs), "y": max(ys) - min(ys), "z": max(zs) - min(zs)}


def _solid_volume_mm3(verts, faces) -> float:
    """Signed-tetrahedron volume (absolute), in mm^3."""
    total = 0.0
    for a, b, c in faces:
        ax, ay, az = verts[a]; bx, by, bz = verts[b]; cx, cy, cz = verts[c]
        # (a) . (b x c) / 6
        cross_x = by * cz - bz * cy
        cross_y = bz * cx - bx * cz
        cross_z = bx * cy - by * cx
        total += (ax * cross_x + ay * cross_y + az * cross_z)
    return abs(total) / 6.0


def _fits(dims: dict, bed: dict) -> bool:
    return dims["x"] <= bed["x"] and dims["y"] <= bed["y"] and dims["z"] <= bed["z"]


def preview(path: str, scale_percent: float) -> dict:
    """Read-only uniform-scale preview. Returns analysis, writes nothing."""
    if not isinstance(scale_percent, (int, float)) or not math.isfinite(scale_percent) or scale_percent <= 0:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "scale_percent must be a positive, finite number"}

    mesh = load_mesh(path)
    if mesh is None:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "could not read mesh geometry from this file"}

    dims = _bbox_dims(mesh.verts)
    if not dims:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "no geometry found"}

    s = scale_percent / 100.0
    scaled = {k: round(v * s, 2) for k, v in dims.items()}
    original = {k: round(v, 2) for k, v in dims.items()}

    vol = _solid_volume_mm3(mesh.verts, mesh.faces)              # mm^3
    grams_orig = (vol / 1000.0) * _PLA_DENSITY                   # cm^3 * density
    grams_scaled = grams_orig * (s ** 3)
    delta_grams = round(grams_scaled - grams_orig, 1)

    co = cost_estimate(abs(delta_grams))
    cost_amt = co.get("cost") if co.get("available") else None
    cost_delta = None if cost_amt is None else round(cost_amt * (1 if delta_grams >= 0 else -1), 2)

    fits = _fits(scaled, U1_BED)

    risks = [
        "Holes, threads, snap-fits, joints and tolerances may not scale correctly — "
        "check fit-critical features after scaling.",
        "Thin-wall safety check is not available here — verify wall thickness after scaling (approximate).",
    ]
    if not fits:
        risks.insert(0, f"Scaled size exceeds the U1 build volume "
                        f"({U1_BED['x']:.0f}x{U1_BED['y']:.0f}x{U1_BED['z']:.0f} mm).")
    if s < 1.0:
        risks.append("Scaling down can make small text/details too fine to print cleanly.")

    if not fits:
        recommendation = "not recommended"
    elif abs(s - 1.0) > 1e-9:
        recommendation = "caution"
    else:
        recommendation = "likely safe"

    explanation = (
        f"At {scale_percent:.0f}% the model is about "
        f"{scaled['x']:.1f}x{scaled['y']:.1f}x{scaled['z']:.1f} mm. Material scales with "
        f"volume (~{s ** 3:.2f}x). This is a uniform-scale preview only — Studio does not "
        f"resize or export your file."
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "scale_percent": scale_percent,
        "original_dimensions": original,
        "scaled_dimensions": scaled,
        "fits_build_volume": fits,
        "estimated_material_delta": {"grams": delta_grams, "basis": "solid volume, PLA ~1.24 g/cm^3 (no infill)"},
        "estimated_cost_delta": {"amount": cost_delta, "basis": "material-only, from material delta"},
        "risks": risks,
        "recommendation": recommendation,
        "explanation": explanation,
    }


def _plate_map(path: str) -> dict:
    """object_id (str) -> {"plate_index": int, "name": str} from model_settings."""
    out = {}
    try:
        tm = ThreeMF.open(path)
        if not tm.has_part(_MODEL_SETTINGS):
            return out
        ms = tm.read_part(_MODEL_SETTINGS).decode("utf-8", "replace")
    except Exception:
        return out
    for pl in re.finditer(r"<plate>(.*?)</plate>", ms, re.S):
        body = pl.group(1)
        pid = re.search(r'key="plater_id"\s+value="(\d+)"', body)
        pname = (re.search(r'key="plater_name"\s+value="([^"]*)"', body) or [None, ""])[1]
        idx = int(pid.group(1)) if pid else None
        for m in re.finditer(r'key="object_id"\s+value="(\d+)"', body):
            out[m.group(1)] = {"plate_index": idx, "name": pname or None}
    return out


_PRINTER_BEDS = {"snapmaker_u1": U1_BED}


def scale_options(path: str, printer: str = "snapmaker_u1", margin_mm: float = 5.0) -> dict:
    """Beginner-friendly 'size options ladder': several uniform-scale choices (safe,
    tight, theoretical, absolute) for fitting the model on the printer, with per-part
    dimensions. Read-only — never scales, exports, or writes anything."""
    bv = _PRINTER_BEDS.get(printer, U1_BED)
    try:
        margin = float(margin_mm)
    except (TypeError, ValueError):
        margin = 5.0
    if not math.isfinite(margin) or margin < 0 or margin * 2 >= min(bv["x"], bv["y"]):
        margin = 5.0

    raw = build_item_dims(path)
    if not raw:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "could not read placed object dimensions from this file"}

    pmap = _plate_map(path)
    current_parts = []
    for i, p in enumerate(raw):
        meta = pmap.get(p["object_id"], {})
        current_parts.append({
            "plate_index": meta.get("plate_index") or (i + 1),
            "name": meta.get("name") or f"Object {p['object_id']}",
            "dimensions": p["dimensions"],
        })

    def fit(d, ux, uy, uz):
        facs = ([ux / d["x"]] if d["x"] > 0 else []) + \
               ([uy / d["y"]] if d["y"] > 0 else []) + \
               ([uz / d["z"]] if d["z"] > 0 else [])
        return min(facs) if facs else None

    usable_xy = bv["x"] - 2 * margin
    safe = [(fit(p["dimensions"], usable_xy, usable_xy, bv["z"]), p) for p in current_parts]
    safe = [(f, p) for f, p in safe if f is not None and f > 0]
    absf = [(fit(p["dimensions"], bv["x"], bv["y"], bv["z"]), p) for p in current_parts]
    absf = [(f, p) for f, p in absf if f is not None and f > 0]
    if not safe or not absf:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "degenerate or zero-size geometry — cannot compute scale options"}

    group_safe, lim_safe = min(safe, key=lambda t: t[0])
    group_abs, lim_abs = min(absf, key=lambda t: t[0])
    d = lim_abs["dimensions"]
    axis_fit = {a: bv[a] / d[a] for a in ("x", "y", "z") if d[a] > 0}
    limiting_axis = min(axis_fit, key=axis_fit.get)

    absolute_pct = math.floor(group_abs * 1000) / 10.0           # e.g. 134.4
    theoretical_pct = float(math.floor(absolute_pct))            # 134
    safe_raw = math.floor(group_safe * 100)                      # 129
    safe_pct = float(max(2, safe_raw - (safe_raw % 2)))          # 128 (friendly, rounded down)
    tight_pct = float(min(safe_pct + 2, math.floor(group_abs * 100)))  # 130, still inside bed
    # keep a sensible non-decreasing ladder even for small/edge models
    tight_pct = max(tight_pct, safe_pct)
    theoretical_pct = max(theoretical_pct, tight_pct)
    absolute_pct = max(absolute_pct, theoretical_pct)

    def by_part(pct):
        s = pct / 100.0
        rows = []
        for p in current_parts:
            dd = p["dimensions"]
            rows.append({
                "plate_index": p["plate_index"], "name": p["name"],
                "dimensions": {k: round(v * s, 1) for k, v in dd.items()},
                "fits_build_volume": all(dd[a] * s <= bv[a] + 1e-6 for a in ("x", "y", "z")),
            })
        return rows

    options = [
        {"label": "Safest novice max", "scale_percent": safe_pct, "risk_level": "low",
         "recommendation": "Recommended starting point",
         "dimensions_by_part": by_part(safe_pct),
         "explanation": f"Largest size that keeps about a {margin:.0f} mm safety margin "
                        f"on each side for brim, bed adhesion and placement. A good place to start."},
        {"label": "Still reasonable, tight margin", "scale_percent": tight_pct, "risk_level": "medium",
         "recommendation": "Usable, but leaves little room",
         "dimensions_by_part": by_part(tight_pct),
         "explanation": "Fits the bed but with a tight margin — check placement and skip a wide brim."},
        {"label": "Theoretical max, too close", "scale_percent": theoretical_pct, "risk_level": "high",
         "recommendation": "Not recommended",
         "dimensions_by_part": by_part(theoretical_pct),
         "explanation": "Right at the edge of the bed. Almost no room for brim, adhesion or placement error."},
        {"label": "Absolute limit, not recommended", "scale_percent": absolute_pct, "risk_level": "high",
         "recommendation": "Not recommended",
         "dimensions_by_part": by_part(absolute_pct),
         "explanation": "The mathematical maximum that touches the build-volume edge. Not a safe choice."},
    ]

    multi = len(current_parts) > 1
    warnings = [
        "This is a readiness estimate, not a guarantee of print success.",
        "Brim or raft needs extra space beyond these sizes.",
    ]
    if multi:
        warnings.append("Use the same scale on all related parts — do not scale plates "
                        "differently if they need to fit together.")
    next_steps = [
        f"Studio recommends starting with {safe_pct:.0f}%.",
        "Apply the same scale to all related parts in your slicer.",
        "Confirm placement and slicing in Snapmaker Orca before printing.",
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "printer": printer,
        "margin_mm": margin,
        "build_volume": {"x": bv["x"], "y": bv["y"], "z": bv["z"]},
        "current_parts": current_parts,
        "group_scaling_recommended": multi,
        "limiting_part": lim_safe["name"],
        "limiting_axis": limiting_axis,
        "recommended_scale_percent": safe_pct,
        "options": options,
        "warnings": warnings,
        "next_steps": next_steps,
    }
