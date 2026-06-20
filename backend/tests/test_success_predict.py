"""Print Success Prediction — pre-print odds from signals Studio already has.

Synthesises design readiness, toolhead fit, first-layer risk, the printer's health
score, and whether this exact file has failed before into one "will it print?"
likelihood. Pure read-only synthesis — no webcam, no control, no new printer calls.
"""
from snapstudio_core import success_predict as sp


def test_unavailable_with_no_signals():
    out = sp.predict()
    assert out["available"] is False


def test_clean_design_healthy_printer_is_likely():
    out = sp.predict(
        readiness={"ready": True, "warnings": []},
        toolfit={"available": True, "overall_level": "ok"},
        first_layer={"overall_level": "ok"},
        health={"available": True, "score": 95},
        prior_failures=0,
    )
    assert out["available"] is True
    assert out["likelihood"] == 100
    assert out["band"] == "likely"
    assert isinstance(out["factors"], list)


def test_color_overflow_and_bad_first_layer_lower_odds():
    out = sp.predict(
        readiness={"ready": True, "warnings": []},
        toolfit={"available": True, "overall_level": "risk"},
        first_layer={"overall_level": "warn"},
        health={"available": True, "score": 90},
    )
    # toolfit risk -25, first_layer warn -10
    assert out["likelihood"] == 65
    assert out["band"] in ("uncertain", "likely")
    assert any("colour" in f.lower() or "toolhead" in f.lower() for f in out["factors"])


def test_repeat_offender_is_a_strong_signal():
    clean = sp.predict(readiness={"ready": True, "warnings": []},
                       health={"available": True, "score": 90})
    repeat = sp.predict(readiness={"ready": True, "warnings": []},
                       health={"available": True, "score": 90}, prior_failures=2)
    assert repeat["likelihood"] < clean["likelihood"]
    assert any("before" in f.lower() or "fail" in f.lower() for f in repeat["factors"])


def test_everything_wrong_clamps_and_is_risky():
    out = sp.predict(
        readiness={"ready": False, "warnings": ["a", "b", "c", "d"]},
        toolfit={"available": True, "overall_level": "risk"},
        first_layer={"overall_level": "risk"},
        health={"available": True, "score": 20},
        prior_failures=3,
    )
    assert 0 <= out["likelihood"] <= 100
    assert out["band"] == "risky"
    assert "firmware" not in out["verdict"].lower()  # plain language, no jargon dump


def test_band_thresholds():
    assert sp._band(75) == "likely"
    assert sp._band(74) == "uncertain"
    assert sp._band(50) == "uncertain"
    assert sp._band(49) == "risky"
