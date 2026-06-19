"""First-Layer Intelligence risk model — pure unit tests (no network).
Feeds synthetic footprint/stability/bed stats into assess() and pins the plain-language
verdicts: adhesion, first-layer evenness, corner-lift, orientation, small-footprint."""
from snapstudio_core import first_layer as FL


def _foot(area, min_dim=20.0, wx=20.0, wy=20.0):
    return {"base_area_mm2": area, "min_dim_mm": min_dim, "width_x_mm": wx, "width_y_mm": wy, "center_xy": [0, 0]}


def _bed(rng, center=None, corner=0.0):
    return {"available": True, "range_mm": rng, "center_range_mm": center if center is not None else rng,
            "corner_spread_mm": corner, "std_mm": rng / 3}


def test_flat_bed_solid_footprint_is_ok():
    r = FL.assess(_foot(2500, 50, 50, 50), {"height_mm": 20, "tip_risk": False}, _bed(0.04))
    assert r["overall_level"] == "ok"
    assert r["bed_aware"] is True
    assert "measured bed mesh" in r["signals_used"]


def test_tiny_footprint_is_adhesion_risk():
    r = FL.assess(_foot(30, 4, 6, 6), {"height_mm": 40, "tip_risk": True}, _bed(0.05))
    assert r["overall_level"] == "risk"
    assert any("small base" in f["text"].lower() for f in r["findings"])
    # orientation suggestion offered for small/tippy parts
    assert any("reorient" in f["text"].lower() for f in r["findings"])


def test_uneven_bed_under_print_is_first_layer_risk():
    r = FL.assess(_foot(1500, 38, 38, 40), {"height_mm": 30, "tip_risk": False}, _bed(0.25, center=0.25))
    assert r["overall_level"] == "risk"
    assert any("bed varies" in f["text"].lower() for f in r["findings"])


def test_mild_bed_is_warn_not_risk():
    r = FL.assess(_foot(3000, 55, 55, 55), {"height_mm": 20, "tip_risk": False}, _bed(0.13, center=0.13))
    assert r["overall_level"] == "warn"


def test_wide_flat_tall_with_uneven_corners_flags_corner_lift():
    r = FL.assess(_foot(8000, 90, 90, 90), {"height_mm": 120, "tip_risk": False}, _bed(0.12, center=0.06, corner=0.22))
    assert r["overall_level"] == "risk"
    assert any("lift" in f["text"].lower() or "warp" in f["text"].lower() for f in r["findings"])


def test_design_only_without_printer_still_advises():
    # no bed (no printer connected) -> still gives footprint/orientation guidance
    r = FL.assess(_foot(35, 5, 6, 6), {"height_mm": 40, "tip_risk": True}, None)
    assert r["bed_aware"] is False
    assert r["overall_level"] == "risk"
    assert "measured bed mesh" not in r["signals_used"]


def test_no_red_flags_message():
    r = FL.assess(_foot(2500, 50, 50, 50), {"height_mm": 20, "tip_risk": False}, None)
    assert r["overall_level"] == "ok"
    assert r["findings"]


def test_service_first_layer_design_only(tmp_path):
    import struct
    from snapstudio_api import service
    # closed box STL -> footprint present, no host -> design-only first-layer assessment
    def box(x, y, z):
        v = [(0,0,0),(x,0,0),(x,y,0),(0,y,0),(0,0,z),(x,0,z),(x,y,z),(0,y,z)]
        quads = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(3,0,4,7)]
        t = []
        for a,b,c,d in quads:
            t += [(v[a],v[b],v[c]),(v[a],v[c],v[d])]
        return t
    p = tmp_path / "box.stl"
    out = b"\x00"*80 + struct.pack("<I", 12)
    for (p1,p2,p3) in box(20,20,20):
        out += struct.pack("<12fH", 0,0,0, *p1, *p2, *p3, 0)
    p.write_bytes(out)
    r = service.first_layer(str(p), None)
    assert r["available"] is True and r["bed_aware"] is False
    assert r["overall_level"] in ("ok", "warn", "risk")
