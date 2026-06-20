"""Toolhead-Fit Intelligence — pure assessment logic."""
from snapstudio_core import toolhead_fit as tf


def test_unknown_color_count_is_unavailable():
    out = tf.assess(None)
    assert out["available"] is False
    assert out["toolhead_count"] == tf.U1_TOOLHEADS  # falls back to the U1's 4


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
    out = tf.assess(2, toolhead_count=4, printer_known=True)
    assert "your connected U1" in out["findings"][0]["text"]
