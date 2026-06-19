"""Validation Center — a readiness + preservation report for a design, read-only.

Answers, in plain terms: will it print on the U1, what will be preserved, what
will change, and what (if anything) is at risk — derived from the Doctor
diagnosis, the project settings, and real geometry. No mutation, no fake data.

Note on colours: the Snapmaker U1 supports more colours than toolheads (real U1
exports carry up to 8 colours on 4 toolheads), so colour count is NOT capped on
conversion — colours are preserved, not lost.
"""
from __future__ import annotations
from pathlib import Path

from .doctor import diagnose_path, READY, CONVERTIBLE
from .intelligence import project_info
from .container import ThreeMF
from .config_io import load_project_settings

SCHEMA_VERSION = "report/1"
SETTINGS = "Metadata/project_settings.config"
# Approx U1 build volume (mm) from the U1 printable_area; used for a bed-fit check.
U1_BUILD = (270.0, 270.0, 270.0)


def _check(name, ok, detail):
    return {"name": name, "status": "pass" if ok else "warn", "detail": detail}


def readiness_report(path: str) -> dict:
    info = project_info(path)
    diag = diagnose_path(path).to_dict()
    is_stl = diag.get("input_type") == "stl"
    verdict = diag.get("verdict")
    dims = info.get("dimensions_mm")
    colors = info.get("colors") or 0

    checks, preserved, changes, at_risk = [], [], [], []
    warnings = list(info.get("issues") or [])

    # --- compatibility checks -------------------------------------------------
    checks.append(_check(
        "Prints on Snapmaker U1",
        verdict in (READY, CONVERTIBLE, "REPAIRABLE"),
        "Ready after preparation" if verdict != READY else "Ready as-is"))
    if dims:
        fits = dims["x"] <= U1_BUILD[0] and dims["y"] <= U1_BUILD[1] and dims["z"] <= U1_BUILD[2]
        checks.append(_check(
            "Fits the print bed",
            fits,
            f'{dims["x"]} × {dims["y"]} × {dims["z"]} mm '
            + ("fits 270 × 270 × 270" if fits else "is larger than the U1 bed — scale or split")))
    if colors:
        checks.append(_check("Colours supported", True, f"{colors} colour(s) — U1 handles this on 4 toolheads"))

    # --- preservation ---------------------------------------------------------
    preserved.append("3D geometry (mesh) — kept exactly")
    if colors:
        preserved.append(f"{colors} material colour(s)")
    if diag.get("painted"):
        preserved.append("painted / multi-colour regions")
    if (info.get("objects") or 0) > 1 or (info.get("plates") or 0) > 1:
        preserved.append("object layout and plates")

    # --- changes + at-risk ----------------------------------------------------
    if is_stl:
        changes.append("Wrapped into a native Snapmaker U1 project")
    else:
        cfg = {}
        try:
            tm = ThreeMF.open(path)
            if tm.has_part(SETTINGS):
                cfg = load_project_settings(tm.read_part(SETTINGS))
        except Exception:
            pass
        if cfg.get("printer_model") not in (None, "Snapmaker U1"):
            changes.append(f'Printer identity → Snapmaker U1 (was {cfg.get("printer_model")})')
        dss = cfg.get("different_settings_to_system")
        if (isinstance(dss, list) and any(str(x) for x in dss)) or (isinstance(dss, str) and dss):
            changes.append("Customized-preset markers cleared so Orca opens it clean — your setting values are kept")
        if cfg.get("print_sequence") not in (None, "by layer"):
            at_risk.append('Print order changes from "by object" to "by layer" (avoids a collision warning; re-enable in Orca if you need by-object)')
        if not changes and verdict == READY:
            changes.append("Already U1-clean — no changes needed")

    # --- design (mesh) checks — best-effort, read-only; never break the report ----
    design_findings = []
    try:
        from .mesh_diagnostics import analyze as _mesh
        md = _mesh(path)
        if md.get("available"):
            integ = md["integrity"]
            if not integ["watertight"]:
                if integ["holes"]:
                    checks.append(_check("Mesh is watertight", False,
                        f"{integ['holes']} hole(s) — may print with gaps or fail; repair before printing"))
                if integ["non_manifold_edges"]:
                    checks.append(_check("Mesh is manifold", False,
                        f"{integ['non_manifold_edges']} non-manifold edge(s) — slicers may misread the surface; repair recommended"))
            else:
                checks.append(_check("Mesh is watertight", True, "Closed, manifold mesh — clean to slice"))
            if md["overhang"]["supports_likely"]:
                checks.append(_check("Overhangs", False,
                    f"{md['overhang']['overhang_pct']}% steep overhangs — supports will likely be needed (enable in Orca)"))
            if md["stability"]["tip_risk"]:
                checks.append(_check("Stability", False,
                    "Tall/narrow base — may tip or knock off the bed; add a brim or reorient"))
            design_findings = md.get("findings", [])
            warnings.extend(f["text"] for f in design_findings if f["level"] in ("warn", "risk"))
    except Exception:
        pass

    ready = verdict == READY or all(c["status"] == "pass" for c in checks)
    return {
        "schema_version": SCHEMA_VERSION,
        "name": Path(path).name,
        "verdict": verdict,
        "readiness_score": diag.get("score"),
        "ready": bool(ready),
        "checks": checks,
        "preserved": preserved,
        "changes": changes,
        "at_risk": at_risk,
        "warnings": warnings,
    }
