"""A fact in the file is not a fact the slicer reads.

The fidelity audit compares two files. That question can be answered "yes" about
a fact Snapmaker Orca never looks at — and it was: a prepared copy stated an
object's filament correctly, the audit called it preserved, and Orca loaded the
geometry and nothing else, so the object printed unassigned.

Everything here encodes a measurement against Snapmaker Orca 2.3.6: a project
handed to Orca, saved back by Orca, and read, with one variable changed and a
control that discriminates.
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from snapstudio_core import preset_deviation, stl_wrap, target_reachability
from snapstudio_core.config_io import dump_project_settings
from snapstudio_core.container import ThreeMF
from snapstudio_core.convert import convert_to_u1
from snapstudio_core.fidelity import audit
from snapstudio_core.repair import repair
from snapstudio_core.u1_identity import is_u1_clean

FIXTURES = Path(__file__).parent / "fixtures"
ORCA_AUTHORED = FIXTURES / "painted" / "snapmaker-orca-2.3.5-authored.3mf"
MULTI = FIXTURES / "prusa-multi-object" / "prusa_three_objects.3mf"
PROJECT = "Metadata/project_settings.config"


# --- the declaration that makes a stated value reach the slicer --------------
#
# Measured, one variable per file. A project stating support_style=tree_hybrid,
# brim_type=no_brim, prime_tower_width=60 and gap_fill_target=nowhere came back
# from Orca as default / auto_brim / 30 / topbottom when the deviations were not
# declared, and kept all four when they were.

def test_a_changed_value_is_declared():
    cfg = {"different_settings_to_system": None}
    change = preset_deviation.declare(cfg, ["brim_type", "support_style"], filaments=4)
    assert change is not None
    assert cfg["different_settings_to_system"][0] == "brim_type;support_style"


def test_the_list_is_the_length_orca_writes_for_that_many_filaments():
    """One entry for the process, one per filament, one for the printer."""
    for filaments, size in ((4, 6), (5, 7), (1, 3)):
        cfg = {}
        preset_deviation.declare(cfg, ["brim_type"], filaments=filaments)
        assert len(cfg["different_settings_to_system"]) == size, filaments


def test_a_filament_key_goes_in_the_filament_entries_not_the_process_one():
    """Measured both ways.

    `nozzle_temperature` named in entry 0 was ignored and the value reset from
    230 to 215. The same key named in the filament entries was kept at 230.
    """
    cfg = {}
    preset_deviation.declare(cfg, ["nozzle_temperature", "support_style"], filaments=4)
    entries = cfg["different_settings_to_system"]
    assert entries[0] == "support_style"
    assert all("nozzle_temperature" in entries[i] for i in range(1, 5))
    assert entries[-1] == ""


def test_a_project_that_deviates_in_nothing_declares_nothing():
    """The common case still imports without a 'Customized Preset' notice."""
    cfg = {}
    assert preset_deviation.declare(cfg, [], filaments=4) is None
    assert "different_settings_to_system" not in cfg


def test_a_deviation_the_source_already_declared_is_kept():
    cfg = {"different_settings_to_system": ["seam_gap", "", "", "", "", ""]}
    preset_deviation.declare(cfg, ["brim_type"], filaments=4)
    assert cfg["different_settings_to_system"][0] == "brim_type;seam_gap"


def test_the_declaration_itself_is_never_declared():
    keys = preset_deviation.keys_from_changes(
        [{"key": "brim_type"}, {"key": "different_settings_to_system"}])
    assert keys == {"brim_type"}


def test_the_keys_come_from_studios_own_change_records():
    keys = preset_deviation.keys_from_changes(
        [{"key": "a"}, {"key": "b"}], None, [{"no_key": 1}], [{"key": "a"}])
    assert keys == {"a", "b"}


@pytest.mark.parametrize("mode, opt", [("u1", None), ("optimize", "u1_fast_prime_tower")])
def test_every_compatibility_fix_and_optimization_is_declared(mode, opt):
    """These are the values that were being reported as applied and discarded."""
    tm = ThreeMF.open(str(ORCA_AUTHORED))
    outcome = repair(tm, mode=mode, opt_profile=opt)
    cfg = json.loads(tm.read_part(PROJECT).decode("utf-8"))
    declared = preset_deviation.declared_process_keys(cfg)
    changed = {c["key"] for c in (outcome.report.get("orca_compatibility") or [])}
    changed |= {c["key"] for c in (outcome.report.get("optimizations") or [])}
    assert changed, "the fixture should exercise at least one change"
    assert changed <= declared, f"undeclared: {sorted(changed - declared)}"


def test_the_optimize_profiles_settings_survive_the_declaration():
    tm = ThreeMF.open(str(ORCA_AUTHORED))
    repair(tm, mode="optimize", opt_profile="u1_fast_prime_tower")
    cfg = json.loads(tm.read_part(PROJECT).decode("utf-8"))
    assert cfg["prime_tower_width"] == "60"
    assert "prime_tower_width" in preset_deviation.declared_process_keys(cfg)


def test_the_template_no_longer_states_a_value_that_never_reached_a_print():
    """`gap_fill_target` was 'nowhere' in Studio's own U1 template and 'topbottom'
    in the preset it names. Undeclared, Orca reset it on every open, so 'nowhere'
    has never reached a print. The template now states what has always been used.
    """
    base = stl_wrap._base_settings(["#FFFFFFFF"] * 4)
    assert base["gap_fill_target"] == "topbottom"


def test_a_declared_deviation_does_not_fail_the_cleanliness_gate():
    cfg = {"printer_model": "Snapmaker U1", "printer_variant": "0.4",
           "printer_settings_id": "Snapmaker U1 (0.4 nozzle)",
           "print_settings_id": "0.20 Standard @Snapmaker U1 (0.4 nozzle)",
           "filament_settings_id": ["Snapmaker PLA"], "version": "01.10.01.50",
           "different_settings_to_system": ["brim_type", "", "", "", "", ""]}
    ok, issues = is_u1_clean(cfg)
    assert ok is True
    assert any(i.startswith("warning:") and "Customized Preset" in i for i in issues)


# --- the Application gate, corrected -----------------------------------------
#
# The previous sprint concluded that "a foreign Application makes Orca load
# geometry only". Measured properly, the rule is narrower and needs two things
# at once, and a fix built on the wider claim would have been built on sand.

def test_the_copy_never_claims_to_be_prusaslicer():
    root = ('<?xml version="1.0" encoding="UTF-8"?><model>'
            '<metadata name="Application">PrusaSlicer-2.9.6</metadata>'
            '<resources><object id="1"><mesh/></object></resources>'
            '<build><item objectid="1"/></build></model>')
    out = stl_wrap._own_the_root_model(root.encode()).decode()
    assert "PrusaSlicer" not in out
    assert stl_wrap.APPLICATION in out
    assert '<object id="1"><mesh/></object>' in out


def test_a_prepared_prusa_project_states_studio_as_its_application(tmp_path):
    source = FIXTURES / "prusa-semantics" / "J_per_object_override_out.3mf"
    prepared = convert_to_u1(str(source), out_dir=str(tmp_path)).output_path
    with zipfile.ZipFile(prepared) as z:
        root = z.read("3D/3dmodel.model").decode("utf-8", "replace")
    assert "PrusaSlicer" not in root


# --- the second dimension ----------------------------------------------------

def test_a_measured_fact_says_whether_the_slicer_reads_it():
    verdict, why = target_reachability.of("Which filament each object uses")
    assert verdict == target_reachability.REACHES
    assert why


def test_a_fact_orca_rebuilds_is_not_called_preserved_without_qualification():
    """slice_info.config was removed and deliberately falsified; both opened the
    same, and Orca wrote an empty one back in every case."""
    verdict, why = target_reachability.of(
        "Slicing summary recorded by the original slicer")
    assert verdict == target_reachability.RECONSTRUCTED
    assert target_reachability.qualifies(verdict)


def test_an_unmeasured_fact_gets_no_verdict_rather_than_a_reassuring_one():
    assert target_reachability.of("Something nobody has measured") == (None, None)


def test_every_audit_row_carries_both_answers(tmp_path):
    prepared = convert_to_u1(str(MULTI), out_dir=str(tmp_path)).output_path
    rows = audit(str(MULTI), prepared)["rows"]
    assert rows
    for row in rows:
        assert "status" in row and "target" in row
    measured = [r for r in rows if r["target"]]
    assert measured, "the load-bearing facts should all be measured"
    for row in measured:
        assert row["target_detail"], row["element"]


def test_the_print_settings_row_does_not_claim_the_slicer_uses_them():
    """It uses the ones that are declared, and this row counts many settings."""
    verdict, why = target_reachability.of("Print settings kept")
    assert verdict == target_reachability.NOT_ESTABLISHED
    assert "different_settings_to_system" in why


# --- the printer entry, and the two package gates ---------------------------

def test_a_printer_key_goes_in_the_last_entry():
    """Measured. `nozzle_type` left undeclared came back reset from
    `stainless_steel` to the preset's `hardened_steel`; declared in the last
    entry it was kept, and sentinel comments injected into `machine_start_gcode`
    and `machine_end_gcode` reached the exported G-code."""
    cfg: dict = {}
    change = preset_deviation.declare(
        cfg, ["nozzle_type", "machine_start_gcode", "brim_type"], filaments=4)
    entries = cfg["different_settings_to_system"]
    assert entries[preset_deviation.PROCESS] == "brim_type"
    assert entries[-1] == "machine_start_gcode;nozzle_type"
    assert change["printer_keys"] == ["machine_start_gcode", "nozzle_type"]


def test_a_printer_key_is_not_left_in_the_process_entry():
    cfg: dict = {}
    preset_deviation.declare(cfg, ["nozzle_type"], filaments=4)
    assert "nozzle_type" not in cfg["different_settings_to_system"][0]


def test_the_package_relationships_are_required():
    verdict, why = target_reachability.of("Archive relationships")
    assert verdict == target_reachability.REACHES
    assert "REQUIRED" in why


def test_the_content_types_index_is_ignored():
    """Removed, stripped, mistyped and malformed all opened as full projects."""
    verdict, why = target_reachability.of("Archive index")
    assert verdict == target_reachability.IGNORED
    assert target_reachability.qualifies(verdict)


# --- the settings carried from a PrusaSlicer project ------------------------

def test_the_settings_carried_from_the_source_are_declared(tmp_path):
    """Five process values are translated from the source project. Undeclared,
    every one of them is replaced by the U1 preset on load — the whole promise,
    correct in the file and invisible to the slicer."""
    import zipfile

    source = FIXTURES / "prusa-semantics" / "C_object_slot3_out.3mf"
    carrier = tmp_path / "prusa_distinct.3mf"
    with zipfile.ZipFile(source) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    parts["Metadata/Slic3r_PE.config"] = (
        "; layer_height = 0.15\n; first_layer_height = 0.3\n"
        "; fill_density = 37%\n; perimeters = 4\n; brim_width = 8\n").encode("utf-8")
    with zipfile.ZipFile(carrier, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)

    prepared = convert_to_u1(str(carrier), out_dir=str(tmp_path)).output_path
    with zipfile.ZipFile(prepared) as z:
        cfg = json.loads(z.read(PROJECT).decode("utf-8"))

    assert cfg["layer_height"] == "0.15"
    assert cfg["sparse_infill_density"] == "37%"
    assert cfg["wall_loops"] == "4"
    declared = preset_deviation.declared_process_keys(cfg)
    for key in ("layer_height", "initial_layer_print_height",
                "sparse_infill_density", "wall_loops", "brim_width"):
        assert key in declared, f"{key} was carried and not declared"


def test_a_source_whose_settings_match_the_u1_declares_nothing(tmp_path):
    """No deviation, no notice. The common case still imports clean."""
    import zipfile

    source = FIXTURES / "prusa-semantics" / "A_no_assignment_out.3mf"
    prepared = convert_to_u1(str(source), out_dir=str(tmp_path)).output_path
    with zipfile.ZipFile(prepared) as z:
        cfg = json.loads(z.read(PROJECT).decode("utf-8"))
    assert not preset_deviation.declared_process_keys(cfg)
