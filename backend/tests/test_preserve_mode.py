"""Creator-setting preservation contract, using a programmatically tuned 3MF."""
from __future__ import annotations

import copy
import json
import shutil
import struct
import threading
import urllib.error
import urllib.request
from pathlib import Path

from snapstudio_core.config_io import dump_project_settings, load_project_settings
from snapstudio_core.container import ThreeMF
from snapstudio_core.convert import convert_to_u1
from snapstudio_core.filaments import PER_FILAMENT_KEYS
from snapstudio_core.preserve import CATEGORY_A, config_diff
from snapstudio_api.server import build_server


SETTINGS = "Metadata/project_settings.config"


def _creator_project(tmp_path, *, multi=False):
    source = tmp_path / "creator.3mf"
    shutil.copy2("../examples/sample_cube_foreign.3mf", source)
    tm = ThreeMF.open(source)
    cfg = load_project_settings(tm.read_part(SETTINGS))
    tuned = {
        "nozzle_temperature": ["235"] * 4,
        "nozzle_temperature_initial_layer": ["240"] * 4,
        "nozzle_temperature_range_high": ["250"] * 4,
        "nozzle_temperature_range_low": ["205"] * 4,
        "retraction_length": ["0.8"], "retraction_speed": ["35"],
        "filament_retraction_length": ["0.8"], "filament_retraction_speed": ["35"],
        "outer_wall_speed": "42", "inner_wall_speed": "88", "sparse_infill_speed": "120",
        "outer_wall_acceleration": "2100", "fan_max_speed": ["85"], "fan_min_speed": ["20"],
        "slow_down_layer_time": ["9"], "enable_support": "1", "support_type": "tree(auto)",
        "support_threshold_angle": "38", "layer_height": "0.16", "filament_flow_ratio": ["0.97"],
        "wall_loops": "4", "sparse_infill_density": "18%", "top_surface_pattern": "monotonic",
        "seam_position": "rear", "ironing_type": "top", "brim_type": "outer_only",
        "z_hop": ["0.2"] * 4, "z_hop_types": ["Normal"] * 4,
        "z_hop_when_prime": ["1"] * 4, "prime_tower_width": "45", "prime_volume": "61",
        "wipe_tower_x": ["40"], "wipe_tower_y": ["40"], "wipe_tower_wall_type": "rounded",
        "wipe_tower_extra_spacing": "117%", "print_sequence": "by object",
        "hot_plate_temp": ["72"], "hot_plate_temp_initial_layer": ["78"],
        "filament_type": ["PETG"], "curr_bed_type": "High Temp Plate",
        "default_bed_type": "High Temp Plate", "gcode_comments": "1",
        "single_extruder_multi_material_priming": "1", "wipe_tower_filament": "0",
        "different_settings_to_system": ["enable_support;print_sequence"],
        "print_settings_id": "0.20mm Standard @BBL X1C",
        "filament_settings_id": ["Creator PETG"], "filament_vendor": ["Creator"],
        "default_filament_profile": ["Creator PETG"],
    }
    cfg.update(tuned)
    if multi:
        cfg.update({
            "filament_colour": ["#ff0000", "#00ff00", "#0000ff", "#ffffff"],
            "filament_type": ["PETG", "PETG", "PETG", "PETG"],
            "flush_volumes_matrix": list(range(16)), "flush_volumes_vector": list(range(8)),
            "prime_tower_width": "47", "wipe_tower_x": ["41"], "wipe_tower_y": ["42"],
        })
    tm.replace_part(SETTINGS, dump_project_settings(cfg))
    tm.save(source)
    return source, cfg


def _prepared(result):
    return load_project_settings(ThreeMF.open(result.output_path).read_part(SETTINGS))


def test_preserve_keeps_creator_quality_and_accounts_for_every_change(tmp_path):
    src, before = _creator_project(tmp_path)
    result = convert_to_u1(str(src))
    after = _prepared(result)
    assert result.prepare_mode == "preserve" and result.schema_version == "convert/2"
    for key in CATEGORY_A:
        if key in before:
            assert after[key] == before[key], key
    # Representative process, filament, support, cooling, speed and flow values remain exact.
    # Single-value per-filament settings are replicated to the four creator colours.
    replicated = {
        key for key, value in before.items()
        if key in PER_FILAMENT_KEYS and isinstance(value, list) and len(value) == 1
    }
    for key in replicated:
        assert after[key] == [before[key][0]] * len(before["filament_colour"]), key
    for key in ("retraction_length", "filament_retraction_length", "outer_wall_speed",
                "fan_max_speed", "enable_support", "support_type", "layer_height",
                "filament_flow_ratio", "wall_loops", "seam_position", "hot_plate_temp"):
        if key in replicated:
            assert after[key] == [before[key][0]] * len(before["filament_colour"]), key
        else:
            assert after[key] == before[key], key
    compat_changed = result.settings_summary["compat_changed"]
    changed = {item["key"] for item in compat_changed}
    assert {"printer_model", "printer_settings_id", "print_settings_id"} <= changed
    print_settings = next(item for item in compat_changed if item["key"] == "print_settings_id")
    assert print_settings["old"] == "0.20mm Standard @BBL X1C"
    assert print_settings["new"] == after["print_settings_id"]
    assert "@Snapmaker U1" in after["print_settings_id"]
    resize = next(item for item in compat_changed if item["key"] == "filament_retraction_length")
    assert resize["old"] == before["filament_retraction_length"]
    assert resize["new"] == after["filament_retraction_length"]
    assert all(d["key"] in changed | {x["key"] for x in result.settings_summary["could_not_carry"]}
               for d in config_diff(before, after))
    assert result.settings_summary["source_has_creator_settings"] is True
    assert len(result.settings_summary["source_config_sha256"]) == 64


def test_recommended_is_opt_in_and_print_sequence_contract(tmp_path):
    src, before = _creator_project(tmp_path)
    preserve = convert_to_u1(str(src), prepare_mode="preserve")
    recommended = convert_to_u1(str(src), prepare_mode="recommended")
    assert _prepared(preserve)["print_sequence"] == "by object"
    assert any("collision check" in w for w in preserve.settings_summary["warnings"])
    assert _prepared(recommended)["print_sequence"] == "by layer"
    assert _prepared(recommended)["nozzle_temperature"] != before["nozzle_temperature"]
    assert any(x["key"] == "nozzle_temperature" for x in recommended.settings_summary["compat_changed"])
    assert preserve.settings_summary["recommended_changes"]


def test_dry_run_starter_and_multimaterial_preservation(tmp_path):
    src, before = _creator_project(tmp_path, multi=True)
    dry = convert_to_u1(str(src), dry_run=True)
    assert dry.output_path == "" and dry.validated_ok and dry.settings_summary["compat_changed"]
    assert not list(tmp_path.glob("creator_SnapmakerU1*.3mf"))
    result = convert_to_u1(str(src))
    after = _prepared(result)
    for key in ("prime_tower_width", "wipe_tower_x", "wipe_tower_y", "flush_volumes_matrix", "flush_volumes_vector"):
        assert after[key] == before[key]

    stl = tmp_path / "tiny.stl"
    stl.write_bytes(
        b"\0" * 80 + struct.pack("<I", 1)
        + struct.pack("<3f", 0, 0, 0)  # normal
        + struct.pack("<3f", 0, 0, 0)
        + struct.pack("<3f", 1, 0, 0)
        + struct.pack("<3f", 0, 1, 0)
        + struct.pack("<H", 0)
    )
    starter = convert_to_u1(str(stl))
    assert starter.prepare_mode == "starter"
    assert starter.settings_summary["warnings"] == [
        "This STL does not include creator slicer settings. Studio will use a U1 starter profile unless you choose another Orca profile."]


def test_support_heavy_creator_values_survive(tmp_path):
    src, before = _creator_project(tmp_path)
    tm = ThreeMF.open(src)
    cfg = load_project_settings(tm.read_part(SETTINGS))
    for key in [k for k in cfg if k.startswith("support_")]:
        cfg[key] = f"creator-{key}"
    tm.replace_part(SETTINGS, dump_project_settings(cfg)); tm.save(src)
    after = _prepared(convert_to_u1(str(src)))
    for key, value in cfg.items():
        if key.startswith("support_"):
            assert after[key] == value, key


def test_summary_copy_guard_and_large_values(tmp_path):
    src, _ = _creator_project(tmp_path)
    tm = ThreeMF.open(src)
    cfg = load_project_settings(tm.read_part(SETTINGS))
    cfg["machine_start_gcode"] = "bambu " + "x" * 400
    tm.replace_part(SETTINGS, dump_project_settings(cfg)); tm.save(src)
    result = convert_to_u1(str(src))
    blob = json.dumps(result.settings_summary).lower()
    assert not any(word in blob for word in ("optimized", "safe settings", "we fixed", "best", "ready", "clean"))
    start = next(x for x in result.settings_summary["compat_changed"] if x["key"] == "machine_start_gcode")
    assert isinstance(start["old"], str) and start["old"].endswith("…") and len(start["old"]) <= 120


def test_api_prepare_mode_validation_and_legacy_alias():
    httpd, token = build_server(port=0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    endpoint = f"http://127.0.0.1:{httpd.server_address[1]}/convert"
    headers = {"Content-Type": "application/json", "X-Auth-Token": token}
    sample = str(Path("../examples/sample_cube_foreign.3mf").resolve())
    try:
        bad = urllib.request.Request(endpoint, data=json.dumps({"path": sample, "prepare_mode": "nope"}).encode(), headers=headers)
        try:
            urllib.request.urlopen(bad, timeout=5)
            assert False, "invalid prepare_mode must be rejected"
        except urllib.error.HTTPError as error:
            assert error.code == 400
        legacy = urllib.request.Request(endpoint, data=json.dumps({"path": sample, "prepare_mode": "u1", "dry_run": True}).encode(), headers=headers)
        with urllib.request.urlopen(legacy, timeout=5) as response:
            assert json.loads(response.read())["prepare_mode"] == "recommended"
    finally:
        httpd.shutdown()
