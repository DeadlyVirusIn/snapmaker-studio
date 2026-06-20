"""Bed-Fit / Out-of-Bounds Doctor — explain Orca's cryptic "out of bounds".

The #1 recurring U1 pain: Snapmaker Orca refuses to slice with "out of bounds"
and no reason. This catches it pre-slice from geometry vs the U1 bed and says
exactly why and how to fix it (scale %, rotate, split, or make room for the
multi-material prime tower). Read-only; offline-capable with the known U1 bed.
"""
from snapstudio_core import bed_fit


def test_unavailable_without_dims():
    out = bed_fit.assess(None)
    assert out["available"] is False


def test_fits_with_room():
    out = bed_fit.assess({"x": 80, "y": 60, "z": 40})
    assert out["available"] is True
    assert out["overall_level"] == "ok"


def test_too_wide_is_out_of_bounds_with_scale_fix():
    out = bed_fit.assess({"x": 320, "y": 100, "z": 50})   # 320 > 270 bed
    assert out["overall_level"] == "risk"
    txt = " ".join(f["text"].lower() for f in out["findings"])
    assert "out of bounds" in txt
    # a concrete scale-to-fit percentage is offered (270/320 ~ 84%)
    assert any("%" in f["text"] for f in out["findings"])
    assert any("scale" in s.lower() for s in out["fixes"])


def test_too_tall_flags_height():
    out = bed_fit.assess({"x": 50, "y": 50, "z": 300})    # 300 > 270 height
    assert out["overall_level"] == "risk"
    txt = " ".join(f["text"].lower() for f in out["findings"])
    assert "tall" in txt or "height" in txt


def test_rotate_suggested_when_diagonal_fits():
    # 300 x 60: too wide on X, but rotating 45° brings the diagonal footprint in.
    out = bed_fit.assess({"x": 300, "y": 60, "z": 40})
    assert any("rotate" in s.lower() for s in out["fixes"])


def test_near_edge_warns():
    out = bed_fit.assess({"x": 262, "y": 120, "z": 40})   # 262/270 ~ 97% of bed
    assert out["overall_level"] in ("warn", "risk")


def test_multimaterial_reserves_prime_tower_room():
    # Fits the bed alone, but leaves no margin for the prime tower in MM mode.
    solo = bed_fit.assess({"x": 250, "y": 250, "z": 40}, multi_material=False)
    mm = bed_fit.assess({"x": 250, "y": 250, "z": 40}, multi_material=True)
    txt = " ".join(f["text"].lower() for f in mm["findings"])
    assert "tower" in txt or "prime" in txt
    assert mm["overall_level"] != "ok" or solo["overall_level"] == "ok"


def test_uses_real_bed_when_known():
    # A smaller connected bed should flag a model the default U1 bed would pass.
    out = bed_fit.assess({"x": 200, "y": 80, "z": 40},
                        bed={"x": 180, "y": 180, "z": 180}, bed_known=True)
    assert out["overall_level"] == "risk"
    assert "connected" in out["bed_source"].lower() or out["bed_known"] is True
