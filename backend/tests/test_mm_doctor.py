"""Multi-Material Doctor — one pre-flight verdict for a multicolour U1 print.

The U1's signature is 4-toolhead multimaterial, and multicolour failures are a top
community pain Orca doesn't explain. This unifies the scattered checks — colours vs
toolheads, filament-settings consistency, and painted-region mapping — into one
plain-language verdict + fixes. Read-only; only meaningful for multicolour designs.
"""
from snapstudio_core import mm_doctor as md


def test_single_colour_is_not_multimaterial():
    out = md.assess(colors=1, heads=4)
    assert out["available"] is True
    assert out["multi_material"] is False


def test_colours_within_toolheads_is_ok():
    out = md.assess(colors=3, heads=4, heads_known=True)
    assert out["multi_material"] is True
    assert out["overall_level"] == "ok"


def test_too_many_colours_is_risk_with_remap_fix():
    out = md.assess(colors=6, heads=4)
    assert out["overall_level"] == "risk"
    txt = " ".join(f["text"].lower() for f in out["findings"])
    assert "toolhead" in txt
    assert any("remap" in s.lower() or "swap" in s.lower() for s in out["fixes"])


def test_inconsistent_filament_metadata_warns():
    out = md.assess(colors=3, heads=4,
                    metadata_issues=["flush_volumes_matrix length 4 != 9"])
    assert out["overall_level"] in ("warn", "risk")
    txt = " ".join(f["text"].lower() for f in out["findings"])
    assert "inconsistent" in txt or "preset" in txt


def test_painted_but_single_colour_warns():
    out = md.assess(colors=1, heads=4, painted=True)
    # Painted regions but one colour configured — the paint won't print as colours.
    assert out["overall_level"] == "warn"


def test_painted_multicolour_notes_mapping():
    out = md.assess(colors=3, heads=4, painted=True)
    txt = " ".join(f["text"].lower() for f in out["findings"])
    assert "paint" in txt or "region" in txt


def test_default_heads_is_u1_four():
    out = md.assess(colors=5)   # heads unknown -> assume U1's 4
    assert out["heads"] == 4
    assert out["overall_level"] == "risk"


def test_verdict_is_plain_language():
    out = md.assess(colors=4, heads=4)
    assert isinstance(out["verdict"], str) and out["verdict"]
