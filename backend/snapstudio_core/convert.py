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

from .container import ThreeMF
from .config_io import load_project_settings
from .fingerprint import compute_fingerprint
from .repair import repair as do_repair
from .validate import validate as do_validate
from .u1_identity import is_u1_clean

SETTINGS = "Metadata/project_settings.config"


@dataclass
class ConversionResult:
    source_type: str          # "stl" | "3mf"
    output_path: str
    output_name: str
    validated_ok: bool
    errors: list
    schema_version: str = "convert/1"

    def to_dict(self) -> dict:
        return asdict(self)


def _finish(source_type: str, out: Path, res) -> ConversionResult:
    """Fold structural/preservation validation together with the U1-cleanliness
    gate: a project that still carries Bambu/BBL/H2D identity is NOT validated_ok,
    even if its geometry checks pass."""
    errors = list(res.errors)
    clean_ok = True
    out_tm = ThreeMF.open(out)
    if SETTINGS in out_tm.list_parts():
        cfg = load_project_settings(out_tm.read_part(SETTINGS))
        clean_ok, clean_issues = is_u1_clean(cfg)
        errors += clean_issues
    return ConversionResult(source_type, str(out), out.name, bool(res.ok and clean_ok), errors)


def _unique_output(src: Path, out_dir: Path | None) -> Path:
    target_dir = out_dir if out_dir else src.parent
    out = target_dir / f"{src.stem}_SnapmakerU1.3mf"
    # Never collide with the source itself (e.g. already-named source).
    n = 2
    while out.resolve() == src.resolve():
        out = target_dir / f"{src.stem}_SnapmakerU1_{n}.3mf"
        n += 1
    return out


def convert_to_u1(path: str, out_dir: str | None = None) -> ConversionResult:
    """Convert a single STL or 3MF into a saved U1-ready 3MF. Returns the result."""
    src = Path(path)
    out_parent = Path(out_dir) if out_dir else None
    if out_parent:
        out_parent.mkdir(parents=True, exist_ok=True)
    out = _unique_output(src, out_parent)

    if src.suffix.lower() == ".stl":
        from .stl_wrap import wrap_stl

        tm = wrap_stl(str(src))
        tm.save(out)
        res = do_validate(ThreeMF.open(out), against=None)
        return _finish("stl", out, res)

    tm = ThreeMF.open(src)
    if not tm.has_part(SETTINGS):
        # Geometry-only / foreign-slicer 3MF (e.g. a PrusaSlicer export with no
        # project_settings.config): there is no project to repair, so wrap the
        # existing geometry into a clean U1 project, like the STL path.
        from .stl_wrap import wrap_geometry_3mf

        wrapped = wrap_geometry_3mf(str(src))
        wrapped.save(out)
        res = do_validate(ThreeMF.open(out), against=None)
        return _finish("3mf-geometry", out, res)

    # 3MF: repair into U1, validate against the source fingerprint (preservation).
    src_fp = compute_fingerprint(tm)
    do_repair(tm, mode="u1", remap=None, dry_run=False, opt_profile=None)
    backup = src.with_suffix(".orig.3mf")
    if not backup.exists():
        shutil.copy2(src, backup)
    tm.save(out)
    res = do_validate(ThreeMF.open(out), against=src_fp)
    return _finish("3mf", out, res)
