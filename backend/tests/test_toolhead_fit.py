"""Toolhead-Fit Intelligence — pure assessment logic."""
from snapstudio_core import toolhead_fit as tf


def test_unknown_color_count_is_unavailable():
    """The offline fallback is still four toolheads — now read from the U1 profile
    rather than from a module constant, so it says which machine it came from."""
    from snapstudio_core import printer_profiles

    out = tf.assess(None)
    assert out["available"] is False
    assert out["toolhead_count"] == printer_profiles.prepare_target()["tool_count"] == 4
    assert out["toolhead_count_source"] == "profile"
    assert out["measured_against"]["printer_id"] == "snapmaker_u1"


def test_single_color_is_ok():
    out = tf.assess(1)
    assert out["available"] is True
    assert out["overall_level"] == "ok"
    assert out["color_count"] == 1


def test_colors_within_toolheads_is_ok_offline_default():
    out = tf.assess(3)  # no printer -> default 4 toolheads
    assert out["overall_level"] == "ok"
    assert out["toolhead_count"] == 4
    assert out["printer_aware"] is False


def test_colors_equal_toolheads_is_ok_no_spare():
    out = tf.assess(4)
    assert out["overall_level"] == "ok"
    # exactly fits: no "to spare" phrasing
    assert "to spare" not in out["findings"][0]["text"]


def test_more_colors_than_toolheads_is_risk():
    out = tf.assess(5)
    assert out["overall_level"] == "risk"
    # leads with the blocking problem, then offers the swap/remap recommendation
    assert out["findings"][0]["level"] == "risk"
    assert any(f["level"] == "warn" for f in out["findings"])
    assert "5" in out["findings"][0]["text"]


def test_real_printer_count_overrides_default():
    # a printer reporting 2 toolheads makes a 3-colour design a risk
    out = tf.assess(3, toolhead_count=2, printer_known=True)
    assert out["toolhead_count"] == 2
    assert out["printer_aware"] is True
    assert out["overall_level"] == "risk"


def test_real_printer_aware_phrasing():
    """A live count is described as the connected printer's, whatever it is — Studio
    has no evidence of the model, only of the toolheads."""
    out = tf.assess(2, toolhead_count=4, printer_known=True)
    assert "your connected printer" in out["findings"][0]["text"]
    assert out["toolhead_count_source"] == "live"
    assert out["measured_against"] is None
