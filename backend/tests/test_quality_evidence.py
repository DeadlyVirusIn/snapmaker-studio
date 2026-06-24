"""Print Quality Doctor evidence aggregation — pure logic tests (no I/O)."""
from snapstudio_core.quality_evidence import evidence_for

MESH = {
    "overhang": {"overhang_pct": 22.0, "severe_pct": 14.0, "supports_likely": True},
    "stability": {"tip_risk": True, "margin_mm": 1.2, "height_mm": 180, "aspect": 6.0},
    "footprint": {"base_area_mm2": 150.0, "min_dim_mm": 6.0, "width_x_mm": 20.0},
}
INSIGHTS = {"colors": 4, "materials": [{"type": "PETG"}, {"type": "PLA"}]}
BED_FIT = {"overall_level": "warn", "overall_text": "Close to the bed edge on X."}
FIRST_LAYER = {"findings": [{"level": "risk", "text": "Tiny first-layer contact area."}]}


def _labels(ev):
    return {e["label"] for e in ev}


def test_bed_adhesion_pulls_bedfit_footprint_firstlayer():
    ev = evidence_for("bed_adhesion", MESH, INSIGHTS, BED_FIT, FIRST_LAYER)
    assert "Bed fit" in _labels(ev)
    assert "Footprint" in _labels(ev)
    assert "First layer" in _labels(ev)
    assert all(e["level"] in ("ok", "warn", "risk") for e in ev)


def test_support_failure_uses_overhang_and_tip_risk():
    ev = evidence_for("fails_even_with_supports", MESH, INSIGHTS, BED_FIT, FIRST_LAYER)
    labels = _labels(ev)
    assert "Overhangs" in labels and "Stability" in labels
    over = next(e for e in ev if e["label"] == "Overhangs")
    assert over["level"] == "risk" and "support" in over["text"].lower()


def test_warping_flags_tall_narrow():
    ev = evidence_for("warping", MESH, INSIGHTS, BED_FIT, FIRST_LAYER)
    assert "Proportions" in _labels(ev)


def test_stringing_reports_material_types():
    ev = evidence_for("stringing", MESH, INSIGHTS, BED_FIT, FIRST_LAYER)
    mats = next(e for e in ev if e["label"] == "Materials")
    assert "PETG" in mats["text"]


def test_color_issue_reports_colour_count():
    ev = evidence_for("color_change", MESH, INSIGHTS, BED_FIT, FIRST_LAYER)
    cols = next(e for e in ev if e["label"] == "Colours")
    assert "4 colours" in cols["text"]


def test_graceful_when_no_evidence_available():
    assert evidence_for("bed_adhesion", None, None, None, None) == []
    assert evidence_for("warping", {}, {}, {}, {}) == []


def test_no_guarantee_language():
    for sym in ("bed_adhesion", "fails_even_with_supports", "warping", "stringing", "color_change"):
        for e in evidence_for(sym, MESH, INSIGHTS, BED_FIT, FIRST_LAYER):
            t = e["text"].lower()
            assert "guarantee" not in t and "100%" not in t and "will succeed" not in t
