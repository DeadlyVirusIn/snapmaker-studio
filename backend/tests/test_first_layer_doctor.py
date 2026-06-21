"""First Layer Doctor MVP — advisory knowledge base tests (static, offline)."""
from snapstudio_core import first_layer_doctor as fld

_EXPECTED = {
    "not_stick", "nozzle_too_high", "nozzle_too_low", "wrinkles", "gaps",
    "corners_lifting", "blob_drag", "area_specific", "toolhead_specific", "breaks_loose",
}


def test_all_ten_symptoms_present():
    assert {s["id"] for s in fld.symptoms()} == _EXPECTED


def test_each_symptom_nonempty():
    for sid in _EXPECTED:
        r = fld.lookup(sid)["result"]
        assert r is not None
        assert r["likely_causes"] and r["first_checks"]
        assert r["u1_checks"] and r["slicer_checks"] and r["avoid"]
        assert r["disclaimer"]


def test_unknown_symptom_safe():
    out = fld.lookup("nope")
    assert out["result"] is None
    assert out["warnings"] and "unknown symptom" in out["warnings"][0]


def test_no_guarantee_language():
    for sid in _EXPECTED:
        r = fld.lookup(sid)["result"]
        blob = " ".join(r["likely_causes"] + r["first_checks"] + r["u1_checks"]
                        + r["slicer_checks"] + r["avoid"]).lower()
        assert "guarante" not in blob
        assert "not a guarantee" in r["disclaimer"].lower()


def test_no_autoedit_or_ignore_language():
    for sid in _EXPECTED:
        r = fld.lookup(sid)["result"]
        blob = " ".join(r["first_checks"] + r["u1_checks"] + r["slicer_checks"] + r["avoid"]).lower()
        assert "auto-fix" not in blob and "automatically" not in blob
        # never instruct the user TO ignore the result (telling them NOT to ignore is fine)
        assert "ignore the bad" not in blob and "ignore it" not in blob
    d = fld.lookup("not_stick")["result"]["disclaimer"].lower()
    assert "does not change your printer config" in d
    assert "never ignore a bad first layer" in d


def test_covers_core_first_layer_topics():
    # aggregate text across all symptoms should cover the required topics
    text = []
    for sid in _EXPECTED:
        r = fld.lookup(sid)["result"]
        text += r["first_checks"] + r["u1_checks"] + r["slicer_checks"]
    joined = " ".join(text).lower()
    assert "clean the build plate" in joined          # build plate cleanliness
    assert "leveling" in joined or "level" in joined  # bed leveling
    assert "z-offset" in joined                       # Z-offset
    assert "filament" in joined and "dry" in joined   # filament quality
    assert "contact area" in joined or "brim" in joined  # contact area / adhesion
    assert "pei" in joined                            # PEI condition
    assert "toolhead 1" in joined                     # U1-specific toolhead check
    assert "bed mesh" in joined or "fluidd" in joined  # advanced mesh/Fluidd check


def test_no_paid_model_names():
    joined = []
    for sid in _EXPECTED:
        r = fld.lookup(sid)["result"]
        joined += r["likely_causes"] + r["first_checks"] + [r["title"]]
    blob = " ".join(joined).lower()
    for name in ("freedom torch", "fox sake", "jesus", "shadow_ams"):
        assert name not in blob
