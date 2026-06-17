from __future__ import annotations
from dataclasses import dataclass
from .container import ThreeMF
from .config_io import load_project_settings

@dataclass
class SourceInfo:
    family: str          # bambu-family | prusa | cura | generic
    application: str | None = None
    printer_model: str | None = None
    is_u1: bool = False

def detect_source(tm: ThreeMF) -> SourceInfo:
    parts = set(tm.list_parts())
    if "Metadata/project_settings.config" in parts:
        cfg = load_project_settings(tm.read_part("Metadata/project_settings.config"))
        pm = cfg.get("printer_model")
        return SourceInfo("bambu-family", printer_model=pm,
                          is_u1=(isinstance(pm, str) and pm.strip() == "Snapmaker U1"))
    if "Metadata/Slic3r_PE.config" in parts:
        return SourceInfo("prusa")
    if any(p.startswith("Metadata/Cura") for p in parts):
        return SourceInfo("cura")
    return SourceInfo("generic")
