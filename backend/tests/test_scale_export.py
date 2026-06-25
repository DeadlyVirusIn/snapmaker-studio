"""Scale Doctor — prepare scaled copy (beta.17). Proves real geometry scaling."""
import hashlib
from pathlib import Path

import pytest

from snapstudio_core.convert import prepare_scaled_copy
from snapstudio_core.geometry import load_mesh

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"
STL = EXAMPLES / "sample_cube.stl"
U1_3MF = EXAMPLES / "sample_cube_U1.3mf"


def _bbox(mesh):
    xs = [v[0] for v in mesh.verts]; ys = [v[1] for v in mesh.verts]; zs = [v[2] for v in mesh.verts]
    return [max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)]


@pytest.mark.skipif(not STL.exists(), reason="sample STL absent")
def test_stl_scaled_copy_geometry_actually_scales(tmp_path):
    before = hashlib.sha256(STL.read_bytes()).hexdigest()
    in_bbox = _bbox(load_mesh(str(STL)))

    res = prepare_scaled_copy(str(STL), 150.0, out_dir=str(tmp_path))

    # original never modified
    assert hashlib.sha256(STL.read_bytes()).hexdigest() == before
    # a new file was created, name carries the scale
    out = Path(res.output_path)
    assert out.exists() and "_scaled_150_U1" in out.name
    assert res.source_type == "stl-scaled" and not res.blocked
    assert res.validated_ok
    # output geometry is the input bbox * 1.5 (real scaling, not just a label)
    out_bbox = _bbox(load_mesh(str(out)))
    for got, exp in zip(out_bbox, [d * 1.5 for d in in_bbox]):
        assert abs(got - exp) < 0.01, (out_bbox, in_bbox)
    # reported dims match
    assert res.scale_percent == 150.0
    for got, exp in zip(res.scaled_mm, [round(d * 1.5, 2) for d in in_bbox]):
        assert abs(got - exp) < 0.05


@pytest.mark.skipif(not STL.exists(), reason="sample STL absent")
def test_scale_out_of_range_blocks(tmp_path):
    with pytest.raises(ValueError):
        prepare_scaled_copy(str(STL), 5.0, out_dir=str(tmp_path))
    with pytest.raises(ValueError):
        prepare_scaled_copy(str(STL), 2000.0, out_dir=str(tmp_path))


@pytest.mark.skipif(not U1_3MF.exists(), reason="sample 3MF absent")
def test_3mf_scaled_copy_blocked_honestly(tmp_path):
    before = hashlib.sha256(U1_3MF.read_bytes()).hexdigest()
    res = prepare_scaled_copy(str(U1_3MF), 128.0, out_dir=str(tmp_path))
    assert res.blocked is True
    assert res.output_path == ""           # no file created
    assert hashlib.sha256(U1_3MF.read_bytes()).hexdigest() == before
    assert any("STL" in e for e in res.errors)
    # honest: must not imply success
    joined = " ".join(res.errors).lower()
    assert "guarantee" not in joined


@pytest.mark.skipif(not STL.exists(), reason="sample STL absent")
def test_scaled_copy_fit_flag_present(tmp_path):
    res = prepare_scaled_copy(str(STL), 110.0, out_dir=str(tmp_path))
    assert isinstance(res.fits_u1, bool)
    assert res.original_mm and res.scaled_mm
