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


# --- the same real shape, through the printer-profile layer ------------------
#
# The second-printer work put a profile/capability layer between the Moonraker
# client and every check. That layer is where a U1 regression would hide: an
# abstraction that quietly answers from a profile instead of from the machine
# looks identical until the machine disagrees with it. These replay the shape a
# real U1 reported and assert the U1 still comes out of the new path unchanged.

#: Recorded from the same real U1 as the payload above, and written down in
#: docs/internal/hardware-0.7.2.json: four extruder objects, a 271 x 335 x 281 mm
#: axis range, and the Snapmaker-specific print_task_config object. Trimmed to the
#: objects Studio reasons about — the machine listed 196.
REAL_U1_OBJECTS = [
    "extruder", "extruder1", "extruder2", "extruder3",
    "print_task_config", "toolhead", "heater_bed", "print_stats",
    "bed_mesh", "exclude_object", "input_shaper", "pause_resume",
    "probe_eddy_current", "filament_switch_sensor runout", "virtual_sdcard",
    "gcode_move", "display_status",
]

REAL_U1_FACTS = {
    "reachable": True, "host": "u1.local", "port": 7125,
    "toolhead_count": 4,
    "bed_mm": {"x": 271.0, "y": 335.0, "z": 281.0},
    "klipper_objects": REAL_U1_OBJECTS,
    "print_state": "standby",
}


def test_a_real_u1_is_still_identified_as_one():
    from snapstudio_core import printer_profiles

    out = printer_profiles.identify(REAL_U1_FACTS)
    assert out["matched"] is True
    assert out["printer_id"] == "snapmaker_u1"
    assert out["confidence"] == "confirmed"
    assert "print_task_config" in out["evidence"]


def test_the_u1_profile_still_reads_as_hardware_verified():
    from snapstudio_core import printer_profiles

    profile = printer_profiles.load("snapmaker_u1")
    assert profile["verification_level"] == printer_profiles.HARDWARE_VERIFIED
    assert printer_profiles.level_label(profile["verification_level"]) == "Hardware verified"


def test_the_new_layer_answers_from_the_u1_not_from_its_profile():
    """Every U1 fact below must come from the machine, not from the profile."""
    from snapstudio_core import printer_profiles

    profile = printer_profiles.load("snapmaker_u1")
    out = printer_profiles.resolve(REAL_U1_FACTS, profile)
    assert out["tool_count"] == 4 and out["sources"]["tool_count"] == "live"
    assert out["build_volume_mm"] == {"x": 271.0, "y": 335.0, "z": 281.0}
    assert out["sources"]["build_volume_mm"] == "live"
    for name in ("bed_mesh", "exclude_object", "input_shaper", "pause_resume",
                 "eddy_probe", "filament_runout"):
        capability = out["capabilities"][name]
        assert capability["state"] == printer_profiles.PRESENT, name
        assert capability["source"] == "live", name
    # No conflict: the machine and the profile agree about the toolheads. The bed
    # differs by design — 335 mm of Y travel over a 270 mm plate — and that is
    # not reported as a disagreement.
    assert out["conflicts"] == []


def test_a_real_u1_still_reports_its_loaded_filament_through_the_new_layer(monkeypatch):
    from snapstudio_core import printer_profiles

    _replay(monkeypatch, REAL_PRINT_TASK_CONFIG)
    facts = dict(REAL_U1_FACTS,
                 loaded_filaments=moonraker.loaded_filaments("u1.local"))
    out = printer_profiles.resolve(facts, printer_profiles.load("snapmaker_u1"))
    assert out["material_state"]["known"] is True
    assert out["material_state"]["slots"] == 4
    assert out["material_state"]["source"] == "live"


def test_a_u1_job_on_a_u1_is_still_the_right_machine():
    """The rewritten sliced-machine check must not have cost the U1 anything."""
    from snapstudio_core import post_slice

    facts = dict(REAL_U1_FACTS,
                 identity={"matched": True, "printer_id": "snapmaker_u1",
                           "confidence": "confirmed"})
    job = {"available": True, "printer_model": "Snapmaker U1", "tools_used": [0, 1],
           "slots": [{"tool": 0, "type": "PLA"}, {"tool": 1, "type": "PLA"}]}
    out = post_slice.analyse(job, facts)
    machine = next(c for c in out["checks"] if c["id"] == "gcode.machine")
    assert machine["result"] == post_slice.OK

    foreign = post_slice.analyse(dict(job, printer_model="Bambu Lab X1 Carbon"), facts)
    check = next(c for c in foreign["checks"] if c["id"] == "gcode.machine")
    assert check["result"] == post_slice.ATTENTION


def test_a_u1_job_with_no_printer_connected_still_compares_to_the_u1():
    """Offline, the comparison falls back to the machine Studio prepares for."""
    from snapstudio_core import post_slice

    job = {"available": True, "printer_model": "Snapmaker U1", "tools_used": [0],
           "slots": [{"tool": 0, "type": "PLA"}]}
    out = post_slice.analyse(job, {"reachable": False})
    machine = next(c for c in out["checks"] if c["id"] == "gcode.machine")
    assert machine["result"] == post_slice.OK

    foreign = post_slice.analyse(dict(job, printer_model="Prusa MK4"), {"reachable": False})
    check = next(c for c in foreign["checks"] if c["id"] == "gcode.machine")
    assert check["result"] == post_slice.ATTENTION
    assert "Snapmaker Orca" in check["action"]
