from __future__ import annotations
from dataclasses import dataclass, field, asdict
from pathlib import Path
from .container import ThreeMF
from .config_io import load_project_settings
from .detect import detect_source
from .fingerprint import compute_fingerprint
from .validate import validate
from .rules import load_rules
from .filaments import PER_FILAMENT_KEYS

SETTINGS = "Metadata/project_settings.config"
SCHEMA_VERSION = "doctor/1"

# verdicts
READY = "READY"               # loads cleanly on the U1 as-is
REPAIRABLE = "REPAIRABLE"      # well-formed project, fixable with `repair`
HIGH_RISK = "HIGH_RISK"        # not a usable project (broken / not a 3MF)
CONVERTIBLE = "CONVERTIBLE"    # an STL - convert it with `repair`


@dataclass
class Diagnosis:
    verdict: str
    score: int | None
    family: str
    printer_model: str | None
    is_u1: bool
    object_count: int
    plate_count: int
    filament_count: int
    painted: bool
    input_type: str = "3mf"
    validation_issues: list = field(default_factory=list)
    compatibility_issues: list = field(default_factory=list)
    recommended_action: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["schema_version"] = SCHEMA_VERSION
        d["is_compatible"] = self.verdict == READY
        return d


def _bad_slicer_values(cfg: dict) -> list[str]:
    """Read-only: list known-incompatible values without mutating (mirrors apply_clamps)."""
    out = []
    for c in load_rules()["clamps"]:
        k = c["key"]
        if k in cfg and str(cfg[k]) == c["bad"]:
            out.append(f"{k}={c['bad']}")
    return out


def _filament_inconsistencies(cfg: dict) -> list[str]:
    """Per-filament arrays must all match the filament count; purge structures must be N*N / N*2."""
    out = []
    n = len(cfg.get("filament_colour", []))
    if not n:
        return out
    for k in PER_FILAMENT_KEYS:
        v = cfg.get(k)
        if isinstance(v, list) and len(v) != n:
            out.append(f"{k} length {len(v)} != filament count {n}")
    m = cfg.get("flush_volumes_matrix")
    if isinstance(m, list) and len(m) != n * n:
        out.append(f"flush_volumes_matrix length {len(m)} != {n * n}")
    return out


def diagnose(tm: ThreeMF) -> Diagnosis:
    """Diagnose a 3MF project (in-memory). Read-only. Score calculation unchanged."""
    src = detect_source(tm)
    fp = compute_fingerprint(tm)
    res = validate(tm, against=None)
    cfg = load_project_settings(tm.read_part(SETTINGS)) if tm.has_part(SETTINGS) else {}

    validation_issues = [e for e in res.errors if e.startswith("missing required part")]
    compatibility_issues: list[str] = []
    score = 100

    if not res.structural_ok:
        score -= 50

    if src.family != "bambu-family":
        compatibility_issues.append(f"source family is {src.family}, not bambu-family")
        score -= 15

    if not src.is_u1:
        compatibility_issues.append(
            f"printer identity is {src.printer_model!r}, not Snapmaker U1")
        score -= 20

    for bad in _bad_slicer_values(cfg):
        compatibility_issues.append(f"incompatible slicer value: {bad}")
        score -= 10

    fil = _filament_inconsistencies(cfg)
    if fil:
        compatibility_issues.append("filament metadata inconsistent: " + "; ".join(fil))
        score -= 15

    score = max(0, min(100, score))
    painted = sum(fp.painted_triangles.values()) > 0

    if not res.structural_ok:
        verdict = HIGH_RISK
        action = "This file is not a usable U1 project (missing required parts); repair may not recover it."
    elif score == 100 and not compatibility_issues:
        verdict = READY
        action = "Ready for Snapmaker U1 - open it in Snapmaker Orca and slice."
    else:
        verdict = REPAIRABLE
        action = "Prepare a U1 profile copy, then review it in Snapmaker Orca before slicing."

    return Diagnosis(
        verdict=verdict, score=score, family=src.family, printer_model=src.printer_model,
        is_u1=src.is_u1, object_count=fp.object_count, plate_count=fp.plate_count,
        filament_count=fp.filament_count, painted=painted, input_type="3mf",
        validation_issues=validation_issues, compatibility_issues=compatibility_issues,
        recommended_action=action,
    )


def diagnose_path(path) -> Diagnosis:
    """Entry point: classify by file type, then diagnose. Read-only."""
    p = Path(path)
    if p.suffix.lower() == ".stl":
        return Diagnosis(
            verdict=CONVERTIBLE, score=None, family="stl", printer_model=None, is_u1=False,
            object_count=0, plate_count=0, filament_count=0, painted=False, input_type="stl",
            recommended_action=f"Run `u1convert repair {p.name}` to generate a U1 project.")
    try:
        tm = ThreeMF.open(path)
    except Exception:
        return Diagnosis(
            verdict=HIGH_RISK, score=0, family="unknown", printer_model=None, is_u1=False,
            object_count=0, plate_count=0, filament_count=0, painted=False, input_type="unknown",
            validation_issues=["not a valid 3MF/ZIP archive"],
            recommended_action="This file is not a 3MF project and cannot be diagnosed.")
    return diagnose(tm)
