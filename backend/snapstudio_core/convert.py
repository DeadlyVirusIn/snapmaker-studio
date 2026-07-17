"""Make a file Snapmaker U1-ready and save it — the desktop 'Convert' action.

Pure engine orchestration (no network/UI): STL files are wrapped into a minimal
U1 3MF; Bambu/Orca 3MF projects are repaired into U1 form. The original is never
overwritten — output is written next to the source as `<stem>_SnapmakerU1.3mf`,
and 3MF repairs also leave a `<stem>.orig.3mf` backup.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import shutil
import copy
import hashlib
import re
from importlib.metadata import PackageNotFoundError, version

from .container import ThreeMF
from .config_io import load_project_settings
from .fingerprint import compute_fingerprint
from .repair import repair as do_repair
from .validate import validate as do_validate
from .u1_identity import is_u1_clean
from .profile import load_profile, apply_swap
from .preserve import CATEGORY_A, config_diff, display_value, machine_compat_keys

SETTINGS = "Metadata/project_settings.config"


@dataclass
class ConversionResult:
    source_type: str          # "stl" | "3mf" | "stl-scaled" | "blocked"
    output_path: str
    output_name: str
    validated_ok: bool
    errors: list
    prepare_mode: str = "preserve"  # preserve | recommended | starter
    settings_summary: dict | None = None
    schema_version: str = "convert/2"
    # Scaled-copy fields (None for a plain convert)
    scale_percent: float | None = None
    original_mm: list | None = None   # [x, y, z] before scaling
    scaled_mm: list | None = None     # [x, y, z] after scaling
    fits_u1: bool | None = None
    blocked: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def _finish(source_type: str, tm: ThreeMF, out: Path | None, res, *,
            prepare_mode: str, settings_summary: dict | None = None) -> ConversionResult:
    """Fold structural/preservation validation together with the U1-cleanliness
    gate: a project that still carries Bambu/BBL/H2D identity is NOT validated_ok,
    even if its geometry checks pass."""
    errors = list(res.errors)
    clean_ok = True
    if SETTINGS in tm.list_parts():
        cfg = load_project_settings(tm.read_part(SETTINGS))
        clean_ok, clean_issues = is_u1_clean(
            cfg, preserve_creator_settings=prepare_mode == "preserve")
        errors += [issue for issue in clean_issues if not issue.startswith("warning:")]
    return ConversionResult(source_type, str(out) if out else "", out.name if out else "",
                            bool(res.ok and clean_ok), errors, prepare_mode, settings_summary)


def _engine_version() -> str:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    try:
        match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject.read_text("utf-8"), re.M)
        if match:
            return match.group(1)
    except OSError:
        pass
    try:
        return version("snapmaker-studio")
    except PackageNotFoundError:
        return "unknown"


def _starter_summary(*, geometry_only: bool) -> dict:
    subject = "This file" if geometry_only else "This STL"
    warnings = [f"{subject} does not include creator slicer settings. Studio will use a U1 starter profile unless you choose another Orca profile."]
    could_not_carry = []
    if geometry_only:
        could_not_carry.append({"key": "foreign model/slicer metadata",
                                "reason": "geometry only; foreign model/slicer metadata is not carried"})
    return {
        "summary_schema": "settings-summary/1", "engine_version": _engine_version(),
        "profile_name": "Snapmaker U1 starter profile", "source_config_sha256": None,
        "source_has_creator_settings": False, "kept_count": 0,
        "compat_changed": [], "could_not_carry": could_not_carry, "warnings": warnings,
        "recommendations_available": False, "recommended_changes": [],
    }


def _action_reasons(report: dict) -> tuple[dict[str, str], set[str]]:
    """Consume RepairOutcome detail while the independent diff remains authoritative."""
    reasons: dict[str, str] = {}
    cleared: set[str] = set()
    groups = [report.get("normalizations", []), report.get("profile_changes", []),
              report.get("value_normalizations", []), report.get("preserved_value_changes", []),
              report.get("presets_normalized", []), report.get("foreign_cleared", [])]
    identity = report.get("identity", {})
    groups.append(identity.get("changed", []) if isinstance(identity, dict) else [])
    for group in groups:
        for item in group:
            if not isinstance(item, dict) or "key" not in item:
                continue
            reasons[item["key"]] = item.get("reason", "changed only for U1 compatibility")
    for item in report.get("foreign_cleared", []):
        if isinstance(item, dict):
            cleared.add(item["key"])
    return reasons, cleared


def _settings_summary(before: dict, after: dict, raw_config: bytes, outcome,
                      prepare_mode: str, profile_name: str = "snapmaker_u1") -> dict:
    profile = load_profile(profile_name)
    diffs = config_diff(before, after)  # independent source of truth (A13)
    reasons, cleared = _action_reasons(outcome.report)
    compat, could_not_carry = [], []
    for item in diffs:
        entry = {"key": item["key"], "old": display_value(item["old"]),
                 "new": display_value(item["new"]),
                 "reason": reasons.get(item["key"], "changed only for U1 compatibility")}
        (could_not_carry if item["key"] in cleared else compat).append(entry)

    recommended_changes = []
    if prepare_mode == "preserve":
        preview = copy.deepcopy(before)
        for item in apply_swap(preview, profile):
            if item["key"] in CATEGORY_A:
                recommended_changes.append({"key": item["key"],
                                            "old": display_value(item["old"]),
                                            "new": display_value(item["new"]),
                                            "reason": "available with the recommended U1 profile"})

    summary = {
        "summary_schema": "settings-summary/1", "engine_version": _engine_version(),
        "profile_name": profile.get("name", profile_name),
        "source_config_sha256": hashlib.sha256(raw_config).hexdigest(),
        "source_has_creator_settings": True,
        "kept_count": sum(1 for key, value in before.items() if key in after and after[key] == value),
        "compat_changed": compat, "could_not_carry": could_not_carry,
        "warnings": list(outcome.report.get("warnings", [])),
        "recommendations_available": prepare_mode == "preserve",
        "recommended_changes": recommended_changes if prepare_mode == "preserve" else [],
    }
    # Preservation invariant: every source setting that changed or disappeared
    # is explicitly accounted for, unless it is in the profile-owned B allowlist.
    accounted = {x["key"] for x in compat + could_not_carry}
    allowlist = machine_compat_keys(profile)
    violations = [x["key"] for x in diffs if x["key"] in before
                  and x["key"] not in allowlist and x["key"] not in accounted]
    if prepare_mode == "preserve" and violations:
        raise ValueError("preservation invariant failed for: " + ", ".join(violations))
    return summary


def _unique_output(src: Path, out_dir: Path | None) -> Path:
    target_dir = out_dir if out_dir else src.parent
    out = target_dir / f"{src.stem}_SnapmakerU1.3mf"
    # Never collide with the source, and never silently overwrite a previous
    # conversion: bump a numeric suffix until the path is free.
    n = 2
    while out.resolve() == src.resolve() or out.exists():
        out = target_dir / f"{src.stem}_SnapmakerU1_{n}.3mf"
        n += 1
    return out


def convert_to_u1(path: str, out_dir: str | None = None, prepare_mode: str = "preserve",
                  dry_run: bool = False) -> ConversionResult:
    """Convert a single STL or 3MF into a saved U1-ready 3MF. Returns the result."""
    src = Path(path)
    if prepare_mode == "u1":
        prepare_mode = "recommended"
    if prepare_mode not in ("preserve", "recommended"):
        raise ValueError("prepare_mode must be 'preserve' or 'recommended'")
    out_parent = Path(out_dir) if out_dir else None
    if out_parent and not dry_run:
        out_parent.mkdir(parents=True, exist_ok=True)
    out = _unique_output(src, out_parent) if not dry_run else None

    if src.suffix.lower() == ".stl":
        from .stl_wrap import wrap_stl

        tm = wrap_stl(str(src))
        if out:
            tm.save(out)
        res = do_validate(tm, against=None)
        return _finish("stl", tm, out, res, prepare_mode="starter",
                       settings_summary=_starter_summary(geometry_only=False))

    tm = ThreeMF.open(src)
    if not tm.has_part(SETTINGS):
        # Geometry-only / foreign-slicer 3MF (e.g. a PrusaSlicer export with no
        # project_settings.config): there is no project to repair, so wrap the
        # existing geometry into a clean U1 project, like the STL path.
        from .stl_wrap import wrap_geometry_3mf

        wrapped = wrap_geometry_3mf(str(src))
        if out:
            wrapped.save(out)
        res = do_validate(wrapped, against=None)
        return _finish("3mf-geometry", wrapped, out, res, prepare_mode="starter",
                       settings_summary=_starter_summary(geometry_only=True))

    # 3MF: repair into U1, validate against the source fingerprint (preservation).
    src_fp = compute_fingerprint(tm)
    raw_config = tm.read_part(SETTINGS)
    before = load_project_settings(raw_config)
    internal_mode = "preserve" if prepare_mode == "preserve" else "u1"
    outcome = do_repair(tm, mode=internal_mode, remap=None, dry_run=dry_run, opt_profile=None)
    after = load_project_settings(tm.read_part(SETTINGS))
    summary = _settings_summary(before, after, raw_config, outcome, prepare_mode)
    backup = src.with_suffix(".orig.3mf")
    if not dry_run and not backup.exists():
        shutil.copy2(src, backup)
    if out:
        tm.save(out)
    res = do_validate(tm, against=src_fp)
    return _finish("3mf", tm, out, res, prepare_mode=prepare_mode, settings_summary=summary)


def _scaled_output(src: Path, out_dir: Path | None, pct: float) -> Path:
    target_dir = out_dir if out_dir else src.parent
    tag = f"{int(round(pct))}"
    out = target_dir / f"{src.stem}_scaled_{tag}_U1.3mf"
    n = 2
    while out.resolve() == src.resolve() or out.exists():
        out = target_dir / f"{src.stem}_scaled_{tag}_U1_{n}.3mf"
        n += 1
    return out


def prepare_scaled_copy(path: str, scale_percent: float,
                        out_dir: str | None = None) -> ConversionResult:
    """Create a NEW uniformly-scaled U1 3MF copy. The original is never modified.

    beta.17: STL input is fully supported (vertex scale, geometry verified by bbox).
    3MF input is intentionally blocked with a clear message — uniform multi-part /
    painted-project scaling is not yet verified against Snapmaker Orca, and we do not
    ship unverified scaling. Preview (read-only) still works for any input.
    """
    src = Path(path)
    pct = float(scale_percent)
    if not (10.0 <= pct <= 1000.0):
        raise ValueError("scale_percent must be between 10 and 1000")
    s = pct / 100.0

    if src.suffix.lower() != ".stl":
        return ConversionResult(
            "blocked", "", "", False,
            ["Scaled copy currently supports STL files. For a 3MF project, preview the "
             "scale here, then resize in Snapmaker Orca — verified 3MF scaled export is "
             "coming. Your file was not changed."],
            scale_percent=pct, blocked=True)

    from .stl_wrap import wrap_stl
    from .geometry import load_mesh
    from .scale_doctor import _fits, U1_BED

    mesh = load_mesh(str(src))
    if mesh is None or not mesh.verts:
        raise ValueError("could not read STL geometry")
    xs = [v[0] for v in mesh.verts]; ys = [v[1] for v in mesh.verts]; zs = [v[2] for v in mesh.verts]
    orig = [max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)]
    scaled = [d * s for d in orig]

    out_parent = Path(out_dir) if out_dir else None
    if out_parent:
        out_parent.mkdir(parents=True, exist_ok=True)
    out = _scaled_output(src, out_parent, pct)

    tm = wrap_stl(str(src), scale=s)
    tm.save(out)
    res = do_validate(ThreeMF.open(out), against=None)
    result = _finish("stl-scaled", ThreeMF.open(out), out, res, prepare_mode="starter",
                     settings_summary=_starter_summary(geometry_only=False))
    result.scale_percent = pct
    result.original_mm = [round(d, 2) for d in orig]
    result.scaled_mm = [round(d, 2) for d in scaled]
    result.fits_u1 = bool(_fits({"x": scaled[0], "y": scaled[1], "z": scaled[2]}, U1_BED))
    return result
