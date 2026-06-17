from __future__ import annotations
import copy
from .container import ThreeMF
from .config_io import load_project_settings, dump_project_settings
from .rules import load_rules, apply_clamps
from .profile import load_profile, apply_swap
from .filaments import apply_remap, filament_count
from .detect import detect_source
from .optimize import load_optimization, apply_optimization
from .report import RepairOutcome

SETTINGS = "Metadata/project_settings.config"


def repair(tm: ThreeMF, mode: str = "u1", remap: dict | None = None,
           dry_run: bool = False, profile_name: str = "snapmaker_u1",
           opt_profile: str | None = None) -> RepairOutcome:
    assert mode in ("safe", "u1", "optimize")
    remap = remap or {}
    source = detect_source(tm)
    cfg = load_project_settings(tm.read_part(SETTINGS))
    work = copy.deepcopy(cfg)

    report = {"source": source.family, "printer_model": source.printer_model,
              "mode": mode, "normalizations": [], "profile_changes": [],
              "optimizations": [], "filament": {"count": filament_count(work)},
              "dry_run": dry_run}

    report["normalizations"] = apply_clamps(work, load_rules())

    # U1 supports >4 filament colours (verified: real U1 files carry 8 colours
    # with 4 toolheads). Never auto-cap; preserve all filament arrays in every
    # mode. Remap is an explicit, opt-in feature only.
    if remap:
        report["filament"].update(apply_remap(work, remap, max_tools=4))  # explicit remap only

    if mode in ("u1", "optimize"):
        report["profile_changes"] = apply_swap(work, load_profile(profile_name))

    # Optimization is explicit + opt-in: applied ONLY in optimize mode when a
    # profile is named. Runs after the U1 swap so it overrides U1 defaults;
    # every change recorded old->new. safe/u1 never reach this.
    if mode == "optimize" and opt_profile:
        report["optimizations"] = apply_optimization(work, load_optimization(opt_profile))

    if not dry_run:
        tm.replace_part(SETTINGS, dump_project_settings(work))
    return RepairOutcome(mode=mode, report=report)
