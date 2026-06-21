"""Scale Doctor — analysis-only preview tests. Read-only: writes no files,
never mutates the source. Uses the generic repo sample cube (no paid models)."""
import hashlib
import os
import shutil

import pytest

from snapstudio_core import scale_doctor as sd

_SAMPLE = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "sample_cube.stl")


def _sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


@pytest.mark.skipif(not os.path.exists(_SAMPLE), reason="sample cube not present")
def test_scale_up_beyond_bed_not_recommended():
    res = sd.preview(_SAMPLE, 5000)   # absurd upscale: must exceed the 270mm bed
    assert res["available"]
    assert res["fits_build_volume"] is False
    assert res["recommendation"] == "not recommended"


@pytest.mark.skipif(not os.path.exists(_SAMPLE), reason="sample cube not present")
def test_scale_down_reduces_material():
    res = sd.preview(_SAMPLE, 50)
    assert res["available"]
    assert res["estimated_material_delta"]["grams"] < 0


@pytest.mark.skipif(not os.path.exists(_SAMPLE), reason="sample cube not present")
def test_scale_up_increases_material():
    res = sd.preview(_SAMPLE, 200)
    assert res["available"]
    assert res["estimated_material_delta"]["grams"] > 0


@pytest.mark.skipif(not os.path.exists(_SAMPLE), reason="sample cube not present")
def test_source_unchanged_and_no_files_written(tmp_path):
    src = str(tmp_path / "cube.stl")
    shutil.copyfile(_SAMPLE, src)
    before = _sha(src)
    before_listing = sorted(os.listdir(tmp_path))
    sd.preview(src, 150)
    assert _sha(src) == before                       # source byte-identical
    assert sorted(os.listdir(tmp_path)) == before_listing   # no new files written


@pytest.mark.skipif(not os.path.exists(_SAMPLE), reason="sample cube not present")
def test_tolerance_warning_shown():
    res = sd.preview(_SAMPLE, 120)
    joined = " ".join(res["risks"]).lower()
    assert "tolerance" in joined
    assert "thin-wall" in joined


@pytest.mark.skipif(not os.path.exists(_SAMPLE), reason="sample cube not present")
def test_no_guarantee_language():
    res = sd.preview(_SAMPLE, 120)
    blob = (res["explanation"] + " " + res["recommendation"] + " " + " ".join(res["risks"])).lower()
    assert "guarantee" not in blob and "guaranteed" not in blob
    assert res["recommendation"] in {"likely safe", "caution", "not recommended"}


def test_invalid_scale_rejected():
    res = sd.preview(_SAMPLE, 0)
    assert res["available"] is False
