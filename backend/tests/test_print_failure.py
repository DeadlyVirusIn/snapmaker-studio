"""Print Failure Troubleshooter — known-good-aware advisory. Read-only.

Hermetic: _read_settings is monkeypatched, so no real 3MF is needed and no private
model name appears here.
"""
import json
import os

from snapstudio_core import print_failure as pf

_BLAME = ["too aggressive", "bad profile", "settings are bad", "is wrong", "are wrong",
          "will fail", "unsafe", "you must slow", "must slow it down"]


def _patch(monkeypatch, **settings):
    base = {"supports_enabled": False, "outer_wall_speed": None, "inner_wall_speed": None,
            "support_speed": None, "filament_types": []}
    base.update(settings)
    monkeypatch.setattr(pf, "_read_settings", lambda path: base)


def _blob(r):
    return json.dumps(r).lower()


def test_known_good_prevents_blame_wording(monkeypatch):
    _patch(monkeypatch, outer_wall_speed=200, support_speed=150)
    r = pf.troubleshoot("x.3mf", known_good_print=True)
    b = _blob(r)
    for bad in _BLAME:
        assert bad not in b, f"blame wording leaked: {bad}"
    assert r["known_good_print"] is True
    assert "printed successfully before" in r["known_good_context"].lower()


def test_high_speed_is_troubleshooting_knob_not_error(monkeypatch):
    _patch(monkeypatch, outer_wall_speed=200, support_speed=150)
    r = pf.troubleshoot("x.3mf", known_good_print=True)
    f = next(x for x in r["findings"] if x["id"] == "speed_knob")
    assert "knob" in f["title"].lower()
    assert "not necessarily wrong" in f["explanation"].lower()
    assert f.get("safe_starting_point")


def test_silk_material_variability_guidance(monkeypatch):
    _patch(monkeypatch)
    r = pf.troubleshoot("x.3mf", known_good_material="Some Silk PLA")
    f = next(x for x in r["findings"] if x["id"] == "silk_variability")
    assert "vary by brand" in f["title"].lower()
    assert "never a single universal value" in f["suggested_action"].lower()


def test_supports_do_not_guarantee_success(monkeypatch):
    _patch(monkeypatch, supports_enabled=True)
    r = pf.troubleshoot("x.3mf", symptom="fails_even_with_supports")
    f = next(x for x in r["findings"] if x["id"] == "supports_no_guarantee")
    assert "does not guarantee success" in f["title"].lower()


def test_known_good_material_echoed(monkeypatch):
    _patch(monkeypatch)
    r = pf.troubleshoot("x.3mf", known_good_material="BrandX Silk", failed_material="BrandY Silk")
    f = next(x for x in r["findings"] if x["id"] == "known_good_material")
    assert "BrandX Silk" in f["evidence"]


def test_no_private_model_name_in_module():
    src = open(pf.__file__, encoding="utf-8").read().lower()
    assert "contenitore" not in src and "sunlu" not in src


def test_no_guarantee_language(monkeypatch):
    _patch(monkeypatch, outer_wall_speed=200)
    r = pf.troubleshoot("x.3mf", known_good_print=True)
    b = _blob(r)
    assert "guaranteed" not in b
    assert any("not a guarantee" in d.lower() for d in r["disclaimers"])


def test_no_auto_fix_claim(monkeypatch):
    _patch(monkeypatch)
    r = pf.troubleshoot("x.3mf")
    assert any("does not auto-edit" in d.lower() for d in r["disclaimers"])
    assert "auto-fix" not in _blob(r)


def test_no_file_writes(monkeypatch, tmp_path):
    _patch(monkeypatch)
    before = sorted(os.listdir(tmp_path))
    pf.troubleshoot(str(tmp_path / "x.3mf"))
    assert sorted(os.listdir(tmp_path)) == before


def test_malformed_settings_safe(monkeypatch):
    # real _read_settings on a bogus path returns {} — must not crash
    r = pf.troubleshoot("does-not-exist.3mf")
    assert r["available"] is True
    assert isinstance(r["findings"], list) and r["findings"]


def test_failure_stage_affects_output(monkeypatch):
    _patch(monkeypatch)
    r = pf.troubleshoot("x.3mf", failure_stage="first_layer")
    f = next((x for x in r["findings"] if x["id"] == "failure_stage"), None)
    assert f is not None and "first layer" in (f["title"] + f["explanation"]).lower()
    # 'unknown' adds no stage finding
    r2 = pf.troubleshoot("x.3mf", failure_stage="unknown")
    assert not any(x["id"] == "failure_stage" for x in r2["findings"])


def test_one_change_at_a_time_present(monkeypatch):
    _patch(monkeypatch)
    r = pf.troubleshoot("x.3mf")
    assert any("one thing at a time" in s.lower() or "one change at a time" in s.lower()
               for s in r["troubleshooting_steps"])
