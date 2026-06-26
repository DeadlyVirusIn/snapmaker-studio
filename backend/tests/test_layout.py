"""beta.18.4 layout / plate-fit detection — profile-compatible != plate-ready."""
import zipfile, os
from pathlib import Path
import pytest

from snapstudio_core.layout import assess_layout

_ROOT = Path(__file__).resolve().parents[2]
_SAMPLE = _ROOT / "examples" / "sample_cube_U1.3mf"


def _clone_with_item_transform(tmp, tx, ty):
    """Clone the sample 3MF and offset its build item by (tx, ty) mm — moving the
    single object off the plate when the offset is large."""
    if not _SAMPLE.exists():
        pytest.skip("sample 3MF absent")
    dst = os.path.join(tmp, "moved.3mf")
    zin = zipfile.ZipFile(str(_SAMPLE))
    model_name = "3D/3dmodel.model"
    raw = zin.read(model_name).decode("utf-8", "replace")
    import re
    new_tf = f'transform="1 0 0 0 1 0 0 0 1 {tx} {ty} 0"'
    if 'transform="' in raw and "<item" in raw:
        raw = re.sub(r'(<item\b[^>]*?)\s*transform="[^"]*"', r"\1 " + new_tf, raw, count=1)
    if new_tf not in raw:
        raw = raw.replace("<item ", f"<item {new_tf} ", 1)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in zin.infolist():
            data = raw.encode("utf-8") if it.filename == model_name else zin.read(it.filename)
            zo.writestr(it, data)
    return dst


def test_clean_single_plate_passes():
    if not _SAMPLE.exists():
        pytest.skip("sample absent")
    r = assess_layout(str(_SAMPLE))
    if r["plates"] == 1:
        assert r["status"] == "pass"


def test_object_pushed_off_plate_fails(tmp_path):
    moved = _clone_with_item_transform(str(tmp_path), 600, 600)
    r = assess_layout(moved)
    assert r["status"] == "fail"
    assert any("plate" in m.lower() for m in r["messages"])


def test_no_placement_data_is_unknown_not_pass(tmp_path):
    bad = os.path.join(str(tmp_path), "empty.3mf")
    with zipfile.ZipFile(bad, "w") as zo:
        zo.writestr("[Content_Types].xml", "<x/>")
    r = assess_layout(bad)
    assert r["status"] == "unknown"
    assert r["status"] != "pass"


def test_report_layout_blocks_ready(tmp_path):
    from snapstudio_core.validation_report import readiness_report
    moved = _clone_with_item_transform(str(tmp_path), 600, 600)
    rep = readiness_report(moved)
    assert rep["layout_status"] == "fail"
    assert rep["ready"] is False
    assert any(c["name"] == "Layout / plate fit" for c in rep["checks"])


def test_plate_window_per_axis_convention():
    """P0/P2 fix: ONE convention PER AXIS — no dual-window false pass, and a negative Y must
    not flip the X window."""
    from snapstudio_core.layout import plate_window, U1_PLATE_MM, U1_HEIGHT_MM
    assert U1_HEIGHT_MM == 270.0
    corner = [{"bounds": {"min": (10.0, 10.0, 0.0), "max": (60.0, 60.0, 20.0)}}]
    assert plate_window(corner) == ((0.0, U1_PLATE_MM), (0.0, U1_PLATE_MM))     # all-positive
    # negative only on Y: X stays corner (0..270), Y flips centred — axes independent.
    mixed = [{"bounds": {"min": (10.0, -50.0, 0.0), "max": (60.0, 10.0, 20.0)}}]
    (xlo, xhi), (ylo, yhi) = plate_window(mixed)
    assert (xlo, xhi) == (0.0, U1_PLATE_MM)
    assert ylo < 0 and yhi == U1_PLATE_MM / 2.0
