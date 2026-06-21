"""Scale Doctor — analysis-only resize preview (read-only).

Uniform scaling only. This module loads a mesh, computes its bounding box and
solid volume, and reports what a uniform scale would do: new size, U1 build-volume
fit, and material/cost deltas. It NEVER writes a file, mutates the source, or
exports — it is preview/advice only and uses hedged language ("likely safe",
"caution", "not recommended"), never guarantees.
"""
from __future__ import annotations

from .geometry import load_mesh
from .bed_fit import U1_BED
from .cost_estimate import estimate as cost_estimate

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
    if not scale_percent or scale_percent <= 0:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "scale_percent must be a positive number"}

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
