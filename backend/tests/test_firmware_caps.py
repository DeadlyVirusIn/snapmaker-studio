"""Firmware Capability Intelligence — what THIS U1's firmware actually exposes.

The U1 is open Klipper/Moonraker; its loaded objects reveal real features (mesh
levelling, input shaping, runout sensors, object exclusion, custom macros) and
hint at extended/community firmware. This interprets the raw klipper object list
into a plain-language capability set. Read-only; honest about what it can't see.
"""
from snapstudio_core import firmware_caps as fc


def test_empty_objects_unavailable():
    out = fc.interpret([], None, None)
    assert out["available"] is False


def test_detects_core_features():
    objs = ["bed_mesh", "input_shaper", "probe_eddy_current stepper_z",
            "exclude_object", "pause_resume", "extruder", "extruder1"]
    out = fc.interpret(objs, 2, {"x": 220, "y": 220, "z": 220})
    names = " ".join(f["name"].lower() for f in out["features"])
    assert out["available"] is True
    assert "mesh" in names
    assert "input" in names or "resonance" in names
    assert "eddy" in names or "probe" in names
    assert "exclusion" in names or "exclude" in names
    assert out["toolhead_count"] == 2


def test_counts_custom_macros():
    objs = ["bed_mesh"] + [f"gcode_macro CUSTOM_{i}" for i in range(12)]
    out = fc.interpret(objs, 1, None)
    macro = next((f for f in out["features"] if "macro" in f["name"].lower()), None)
    assert macro is not None
    assert "12" in (macro.get("detail") or "")


def test_extended_firmware_flag_on_many_macros():
    stock = ["bed_mesh", "input_shaper", "extruder"]
    out_stock = fc.interpret(stock, 1, None)
    extended = stock + [f"gcode_macro EXT_{i}" for i in range(20)]
    out_ext = fc.interpret(extended, 1, None)
    assert out_stock["extended_firmware"] is False
    assert out_ext["extended_firmware"] is True


def test_runout_sensor_detected():
    out = fc.interpret(["filament_switch_sensor runout", "extruder"], 1, None)
    names = " ".join(f["name"].lower() for f in out["features"])
    assert "runout" in names or "filament" in names


def test_summary_is_plain_language():
    out = fc.interpret(["bed_mesh", "input_shaper", "extruder", "extruder1",
                        "extruder2", "extruder3"], 4, {"x": 220, "y": 220, "z": 220})
    assert isinstance(out["summary"], str) and out["summary"]
