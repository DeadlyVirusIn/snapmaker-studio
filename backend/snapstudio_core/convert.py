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
    source_type: str          # "stl" | "3mf" | "stl-scaled" | "blocked"
    output_path: str
    output_name: str
    validated_ok: bool
    errors: list
    schema_version: str = "convert/1"
    # Scaled-copy fields (None for a plain convert)
    scale_percent: float | None = None
    original_mm: list | None = None   # [x, y, z] before scaling
    scaled_mm: list | None = None     # [x, y, z] after scaling
    fits_u1: bool | None = None
    blocked: bool = False

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
    # Never collide with the source, and never silently overwrite a previous
    # conversion: bump a numeric suffix until the path is free.
    n = 2
    while out.resolve() == src.resolve() or out.exists():
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
    result = _finish("stl-scaled", out, res)
    result.scale_percent = pct
    result.original_mm = [round(d, 2) for d in orig]
    result.scaled_mm = [round(d, 2) for d in scaled]
    result.fits_u1 = bool(_fits({"x": scaled[0], "y": scaled[1], "z": scaled[2]}, U1_BED))
    return result
