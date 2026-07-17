from __future__ import annotations
import copy
from .container import ThreeMF
from .config_io import load_project_settings, dump_project_settings
from .rules import load_rules, apply_clamps
from .profile import load_profile, apply_swap
from .filaments import apply_remap, filament_count, conform_filament_arrays
from .preserve import machine_compat_keys, prepare_preserved_values
from .detect import detect_source
from .optimize import load_optimization, apply_optimization
from .report import RepairOutcome
from .u1_identity import (
    normalize_project_identity, normalize_values, scrub_foreign, normalize_slice_info,
    normalize_presets,
)

SETTINGS = "Metadata/project_settings.config"
SLICE_INFO = "Metadata/slice_info.config"


def repair(tm: ThreeMF, mode: str = "u1", remap: dict | None = None,
           dry_run: bool = False, profile_name: str = "snapmaker_u1",
           opt_profile: str | None = None) -> RepairOutcome:
    assert mode in ("safe", "preserve", "u1", "optimize")
    remap = remap or {}
    source = detect_source(tm)
    cfg = load_project_settings(tm.read_part(SETTINGS))
    work = copy.deepcopy(cfg)

    report = {"source": source.family, "printer_model": source.printer_model,
              "mode": mode, "normalizations": [], "profile_changes": [],
              "optimizations": [], "filament": {"count": filament_count(work)},
              "dry_run": dry_run}

    report["normalizations"] = apply_clamps(work, load_rules())
    for change in report["normalizations"]:
        change["reason"] = (
            f"U1 compatibility clamp: {change['old']} → {change['new']}")

    # U1 supports >4 filament colours (verified: real U1 files carry 8 colours
    # with 4 toolheads). Never auto-cap; preserve all filament arrays in every
    # mode. Remap is an explicit, opt-in feature only.
    if remap:
        report["filament"].update(apply_remap(work, remap, max_tools=4))  # explicit remap only

    if mode in ("preserve", "u1", "optimize"):
        profile = load_profile(profile_name)
        compat_keys = machine_compat_keys(profile)
        preserve_creator_settings = mode == "preserve"
        report["profile_changes"] = apply_swap(
            work, profile, preserve_creator_settings=preserve_creator_settings)
        # Foreign projects often carry per-filament arrays longer than the real
        # colour count (e.g. 10 slots, 5 colours). Per-extruder vectors are
        # explicitly excluded by conform_filament_arrays and are resized later
        # to U1's four toolheads without losing their per-slot values.
        report["filament_array_changes"] = []
        conform_filament_arrays(work, filament_count(work),
                                changes=report["filament_array_changes"])
        # Make the project read as a genuine U1 project: rewrite the preset
        # identity block to known-good values and scrub any leftover
        # Bambu/BBL/H2D strings (e.g. foreign machine G-code).
        report["identity"] = normalize_project_identity(
            work, filament_count(work), preserve_filament_identity=preserve_creator_settings)
        report["value_normalizations"] = normalize_values(work)
        report["foreign"] = scrub_foreign(
            work, preserve_creator_settings=preserve_creator_settings,
            compat_keys=compat_keys)
        report["foreign_cleared"] = report["foreign"]["cleared"]
        report["warnings"] = report["foreign"]["warnings"]
        if preserve_creator_settings:
            preserved_changes, preserved_warnings = prepare_preserved_values(
                work, filament_count(work))
            report["preserved_value_changes"] = preserved_changes
            report["warnings"].extend(preserved_warnings)
            if work.get("print_sequence") == "by object":
                report["warnings"].append(
                    "May trigger a collision check dialog in Orca; Studio kept the creator's print order")
            dss = work.get("different_settings_to_system")
            if (isinstance(dss, list) and any(str(x) for x in dss)) or (isinstance(dss, str) and dss):
                report["warnings"].append(
                    "Snapmaker Orca may show a 'Customized Preset' notice — that is the creator's tuned settings being kept.")
            fsi = work.get("filament_settings_id")
            if isinstance(fsi, list) and not all(str(x).startswith("Snapmaker") for x in fsi):
                report["warnings"].append("Orca may ask to map an unknown filament preset")
        # Clean-import: clear the "Customized Preset" diff marker and reset the
        # "by object" print sequence (collision warning) to the U1 default.
        report["presets_normalized"] = normalize_presets(
            work, preserve_creator_settings=preserve_creator_settings)

    # Optimization is explicit + opt-in: applied ONLY in optimize mode when a
    # profile is named. Runs after the U1 swap so it overrides U1 defaults;
    # every change recorded old->new. safe/u1 never reach this.
    if mode == "optimize" and opt_profile:
        report["optimizations"] = apply_optimization(work, load_optimization(opt_profile))

    # ThreeMF is in-memory here. Replacing the parts even for dry runs lets the
    # caller validate the exact would-be project without writing an output file.
    tm.replace_part(SETTINGS, dump_project_settings(work))
    # Blank the Bambu slice_info version stamp (the "newer version" trigger).
    if mode in ("preserve", "u1", "optimize") and SLICE_INFO in tm.list_parts():
        original_slice_info = tm.read_part(SLICE_INFO)
        normalized_slice_info = normalize_slice_info(original_slice_info)
        if normalized_slice_info != original_slice_info:
            tm.replace_part(SLICE_INFO, normalized_slice_info)
            report["slice_info"] = [{
                "key": "slice_info",
                "reason": "X-BBL-Client-Version blanked for Snapmaker Orca",
            }]
    return RepairOutcome(mode=mode, report=report)
