"""Firmware shapes read from a real Snapmaker U1.

These fixtures are not invented. They were captured read-only from a U1 on a LAN
(firmware reporting four toolheads and a 271 x 335 x 281 mm volume) during the
beta.23 acceptance work. The previous `loaded_filaments()` looked for a list of
objects and therefore returned "this printer does not report it" against a
printer that was reporting it perfectly well — an honest answer that was
nevertheless wrong. These tests pin the real shape so that cannot recur.

Everything here is offline: the captured payload is replayed, no printer is
contacted, and no control call exists in this module.
"""
from __future__ import annotations

import json

from snapstudio_core import moonraker

# Trimmed from a live `GET /printer/objects/query?print_task_config`. Colours and
# materials are the machine's own values; nothing identifying the owner is kept.
REAL_PRINT_TASK_CONFIG = {
    "filament_type": ["PLA", "PLA", "PLA", "PLA"],
    "filament_sub_type": ["Matte", "Silk", "Basic", "Matte"],
    "filament_color_rgba": ["000000FF", "2D9E59FF", "F8F81CFF", "FFFFFFFF"],
    "filament_color": [4278190080, 4281179737, 4294506524, 4294967295],
    "filament_vendor": ["Snapmaker", "Snapmaker", "Snapmaker", "Snapmaker"],
    "filament_exist": [True, True, True, True],
    "extruders_used": [],
}


def _replay(monkeypatch, payload):
    def fake_get(host, port, path, timeout):
        assert path.startswith("/printer/objects/query?print_task_config")
        return {"result": {"status": {"print_task_config": payload} if payload else {}}}

    monkeypatch.setattr(moonraker, "_get", fake_get)


def test_real_parallel_arrays_are_read(monkeypatch):
    _replay(monkeypatch, REAL_PRINT_TASK_CONFIG)
    loaded = moonraker.loaded_filaments("u1.local")
    assert loaded is not None, "the real firmware shape must not read as 'not reported'"
    assert len(loaded) == 4
    assert loaded[0] == {"color": "#000000", "material": "PLA Matte", "vendor": "Snapmaker"}
    assert loaded[1]["color"] == "#2D9E59"
    assert loaded[2]["material"] == "PLA Basic"


def test_an_empty_slot_is_reported_as_empty(monkeypatch):
    """`filament_exist` is the printer's own answer to whether a spool is loaded."""
    payload = json.loads(json.dumps(REAL_PRINT_TASK_CONFIG))
    payload["filament_exist"] = [True, False, True, False]
    _replay(monkeypatch, payload)
    loaded = moonraker.loaded_filaments("u1.local")
    assert [bool(entry) for entry in loaded] == [True, False, True, False]


def test_a_printer_without_the_object_still_reports_unknown(monkeypatch):
    _replay(monkeypatch, None)
    assert moonraker.loaded_filaments("u1.local") is None


def test_an_unfamiliar_shape_reports_unknown_rather_than_guessing(monkeypatch):
    _replay(monkeypatch, {"something_else": 1})
    assert moonraker.loaded_filaments("u1.local") is None


def test_material_falls_back_to_type_when_there_is_no_subtype(monkeypatch):
    payload = {"filament_type": ["PETG", "PLA"], "filament_color_rgba": ["FF0000FF", "00FF00FF"]}
    _replay(monkeypatch, payload)
    loaded = moonraker.loaded_filaments("u1.local")
    assert loaded[0]["material"] == "PETG"
    assert loaded[0]["color"] == "#FF0000"


def test_preflight_uses_the_real_loaded_count(monkeypatch):
    """The join that matters: six materials needed, four loaded."""
    from snapstudio_core import preflight as pf

    _replay(monkeypatch, REAL_PRINT_TASK_CONFIG)
    loaded = moonraker.loaded_filaments("u1.local")
    out = pf.evaluate(
        {"filament_count": {"value": 6, "confidence": "confirmed", "evidence": "test"}},
        {"reachable": True, "host": "u1.local", "port": 7125, "toolhead_count": 4,
         "bed_mm": {"x": 271.0, "y": 335.0, "z": 281.0}, "klipper_objects": ["extruder"],
         "print_state": "standby", "loaded_filaments": loaded},
    )
    materials = next(c for c in out["checks"] if c["id"] == "materials.loaded")
    assert materials["result"] == pf.ATTENTION
    assert "4 loaded" in materials["evidence"] and "6" in materials["evidence"]


def test_the_summary_does_not_lowercase_the_product_name():
    """`capitalize()` would turn "Studio" into "studio" mid-sentence."""
    from snapstudio_core import preflight as pf

    out = pf.evaluate(
        {"filament_count": {"value": 6, "confidence": "confirmed", "evidence": "t"},
         "nozzle_diameters": {"value": ["0.4"], "confidence": "confirmed", "evidence": "t"}},
        {"reachable": True, "host": "u1.local", "port": 7125, "toolhead_count": 4,
         "klipper_objects": ["extruder"], "print_state": "standby"},
    )
    assert "studio cannot" not in out["summary"]
    assert "Studio cannot" in out["summary"]
