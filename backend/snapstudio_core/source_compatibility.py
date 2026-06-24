"""File/source ecosystem detection (item 7) — advisory, read-only.

Tells a beginner what kind of file/project Studio detected, what it can safely read,
what it cannot convert yet, and the recommended next step for the Snapmaker U1 /
Snapmaker Orca. Reuses detect_source() + ThreeMF; never modifies the file and never
claims a conversion that isn't actually implemented.
"""
from __future__ import annotations

from .container import ThreeMF
from .detect import detect_source
from .config_io import load_project_settings

ECOSYSTEM_LABEL = {
    "bambu-family": "Bambu-family 3MF (Snapmaker Orca / Bambu Studio)",
    "prusa": "PrusaSlicer project",
    "cura": "Cura project",
    "generic": "Generic 3MF",
    "stl": "STL mesh",
}


def _parse_ini(raw: bytes) -> dict:
    out: dict[str, str] = {}
    for line in raw.decode("utf-8", "ignore").splitlines():
        line = line.strip()
        if not line or line.startswith(("#", ";", "[")):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def detect_detailed(path: str) -> dict:
    """Return an advisory source-compatibility report. Best-effort, never raises."""
    low = (path or "").lower()
    if low.endswith(".stl"):
        return {
            "schema_version": "source/1",
            "ecosystem": "stl",
            "ecosystem_label": ECOSYSTEM_LABEL["stl"],
            "source_app": "STL mesh (no slicer data)",
            "printer_model": None,
            "is_u1": False,
            "readable_settings": {},
            "can_read": ["3D geometry"],
            "cannot_convert": ["colours, materials, and print settings — a bare STL has none"],
            "risks": [],
            "recommended_next_step": "Open it in Studio and run Project Doctor, then choose colours and settings in Snapmaker Orca.",
        }

    try:
        tm = ThreeMF.open(path)
    except Exception:
        return {
            "schema_version": "source/1",
            "ecosystem": "unknown",
            "ecosystem_label": "Unrecognized file",
            "source_app": "Unknown",
            "printer_model": None,
            "is_u1": False,
            "readable_settings": {},
            "can_read": [],
            "cannot_convert": ["this file isn't an STL or a 3MF Studio can open"],
            "risks": ["Studio could not read this file as a 3D model."],
            "recommended_next_step": "Export an STL or 3MF from your slicer, then open that in Studio.",
        }

    info = detect_source(tm)
    eco = info.family
    report = {
        "schema_version": "source/1",
        "ecosystem": eco,
        "ecosystem_label": ECOSYSTEM_LABEL.get(eco, "Generic 3MF"),
        "source_app": None,
        "printer_model": info.printer_model,
        "is_u1": info.is_u1,
        "readable_settings": {},
        "can_read": [],
        "cannot_convert": [],
        "risks": [],
        "recommended_next_step": "",
    }

    if eco == "bambu-family":
        try:
            cfg = load_project_settings(tm.read_part("Metadata/project_settings.config"))
        except Exception:
            cfg = {}
        ftypes = cfg.get("filament_type") or []
        if isinstance(ftypes, str):
            ftypes = [ftypes]
        report["source_app"] = "Snapmaker Orca / Bambu Studio (Bambu-family)"
        report["readable_settings"] = {
            "printer_model": info.printer_model,
            "filament_count": len(ftypes) or None,
            "filament_types": sorted({str(t).upper() for t in ftypes}) or None,
        }
        report["can_read"] = ["printer model", "filament colours + types", "per-plate / per-object colour assignment"]
        if info.is_u1:
            report["cannot_convert"] = []
            report["recommended_next_step"] = "This is already a Snapmaker U1 project — run Project Doctor, then Open in Snapmaker Orca to slice."
        else:
            report["cannot_convert"] = ["the source printer's profile (it targets another printer, not the U1)"]
            report["risks"] = [f"This file targets {info.printer_model or 'another printer'}, not the Snapmaker U1 — its profile settings may not suit the U1."]
            report["recommended_next_step"] = "Let Studio prepare a clean U1-ready copy (Prepare), then Open in Snapmaker Orca to slice."

    elif eco == "prusa":
        try:
            ini = _parse_ini(tm.read_part("Metadata/Slic3r_PE.config"))
        except Exception:
            ini = {}
        colours = [c for c in (ini.get("filament_colour", "").split(";")) if c]
        types = [t for t in (ini.get("filament_type", "").split(";")) if t]
        report["source_app"] = "PrusaSlicer"
        report["printer_model"] = ini.get("printer_model") or None
        report["readable_settings"] = {
            "printer_model": ini.get("printer_model") or None,
            "filament_count": len(colours) or None,
            "filament_types": sorted({t.upper() for t in types}) or None,
        }
        report["can_read"] = ["printer model", "filament colours + types", "model geometry"]
        report["cannot_convert"] = ["PrusaSlicer print settings (supports, seams, speeds) — these don't carry over to the U1"]
        report["risks"] = ["This is a PrusaSlicer project, not a U1 project — don't print its settings on the U1 as-is."]
        report["recommended_next_step"] = "Studio can read the model and materials. Open the model in Snapmaker Orca and use a U1 profile to slice."

    elif eco == "cura":
        report["source_app"] = "Cura"
        report["can_read"] = ["that this is a Cura project", "model geometry"]
        report["cannot_convert"] = ["Cura's settings and profiles — Studio detects Cura but can't read its settings yet"]
        report["risks"] = ["This is a Cura project, not a U1 project."]
        report["recommended_next_step"] = "Open the model in Snapmaker Orca with a U1 profile to slice; Studio can run Project Doctor on the geometry."

    else:  # generic 3MF (or unknown ecosystem like Creality — honestly reported as generic)
        report["source_app"] = "Generic 3MF"
        report["can_read"] = ["3D model geometry"]
        report["cannot_convert"] = ["no slicer settings are present in this file"]
        report["recommended_next_step"] = "Open it and run Project Doctor, then set up the print in Snapmaker Orca."

    return report
