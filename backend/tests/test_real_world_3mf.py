"""Studio's readers against 3MFs that real slicers actually wrote.

Every other 3MF test in this suite builds its own archive. That proves the logic
and proves nothing about the format as it exists in the wild. These run against
genuine OrcaSlicer, BambuStudio and PrusaSlicer project files.

The files are fetched rather than committed — they are AGPL-3.0, and one embeds
an upstream developer's local path — so every test here skips cleanly when they
are absent. See fixtures/REAL_WORLD_PROVENANCE.md.

    python tests/fixtures/fetch_real_world.py
"""
from __future__ import annotations

from pathlib import Path

import pytest

from snapstudio_core import (color_plan, container, ecosystem, fidelity,
                             plate_placement, project_cost, project_traits)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "real-world"


def fixture(name: str) -> str:
    path = FIXTURES / name
    if not path.exists():
        pytest.skip(f"{name} not fetched — run tests/fixtures/fetch_real_world.py")
    return str(path)


ORCA_DUAL = "orca-pa-line-dual.3mf"
ORCA_BADGE = "orca-badge.3mf"
BAMBU_PA = "bambu-pa-pattern.3mf"
PRUSA_SEAM = "prusa-seam-test.3mf"

ALL = [ORCA_DUAL, ORCA_BADGE, BAMBU_PA, PRUSA_SEAM]


# --- the reader survives them ----------------------------------------------

@pytest.mark.parametrize("name", ALL)
def test_every_real_project_opens(name):
    tm = container.ThreeMF.open(fixture(name))
    assert tm.list_parts(), "no parts read"
    assert any(p.endswith(".model") for p in tm.list_parts())


@pytest.mark.parametrize("name", ALL)
def test_traits_never_raise_and_are_graded(name):
    traits = project_traits.extract(fixture(name))
    assert traits["readable"] is True, traits.get("notes")
    for key in project_traits.TRAIT_KEYS:
        entry = traits[key]
        assert entry["confidence"] in (
            project_traits.CONFIRMED, project_traits.LIKELY,
            project_traits.INFORMATIONAL, project_traits.UNKNOWN)


# --- the Bambu/Orca dialect -------------------------------------------------

def test_orca_project_is_recognised_as_bambu_family():
    traits = project_traits.extract(fixture(ORCA_DUAL))
    assert traits["origin_family"]["value"] == "bambu-family"
    assert traits["origin_family"]["confidence"] == project_traits.CONFIRMED


def test_orca_multimaterial_project_reports_its_filaments():
    traits = project_traits.extract(fixture(ORCA_DUAL))
    assert traits["filament_count"]["value"] >= 2, "a dual-material calibration project"
    assert traits["object_count"]["value"] >= 1


def test_a_six_byte_settings_file_does_not_break_anything():
    """OrcaBadge ships a 6-byte project_settings.config — a real empty-settings
    edge case that a naive JSON read would raise on."""
    traits = project_traits.extract(fixture(ORCA_BADGE))
    assert traits["readable"] is True
    assert traits["origin_family"]["value"] == "bambu-family"
    # No settings means no printer can be claimed.
    assert traits["target_printer"]["confidence"] == project_traits.UNKNOWN


def test_spaces_in_part_names_are_handled():
    parts = container.ThreeMF.open(fixture(ORCA_BADGE)).list_parts()
    assert any(" " in p for p in parts), "this fixture is here for its spaced part names"


def test_real_per_layer_gcode_is_detected():
    """The Bambu pressure-advance pattern carries 90 KB of real
    custom_gcode_per_layer.xml — the record the colour planner reads."""
    traits = project_traits.extract(fixture(BAMBU_PA))
    assert traits["has_custom_per_layer_gcode"]["value"] is True


def test_colour_planner_runs_on_a_real_project():
    plan = color_plan.analyse(fixture(BAMBU_PA), toolheads=4)
    assert plan["available"] is True
    assert plan["verdict"] in (color_plan.FITS, color_plan.POSSIBLE_WITH_SWAPS,
                              color_plan.NEEDS_REDUCTION, color_plan.CANNOT_CLASSIFY)
    for bucket in ("simultaneous", "layer_based", "unclassified"):
        for entry in plan[bucket]:
            assert entry["evidence"], "a real project must still carry its evidence"


# --- the PrusaSlicer dialect ------------------------------------------------

def test_prusa_project_is_recognised_as_prusa():
    traits = project_traits.extract(fixture(PRUSA_SEAM))
    assert traits["origin_family"]["value"] == "prusa"
    assert traits["origin_family"]["confidence"] == project_traits.CONFIRMED


def test_prusa_project_is_not_mistaken_for_a_u1_project():
    traits = project_traits.extract(fixture(PRUSA_SEAM))
    assert traits["is_u1_project"]["value"] is not True


# --- the rest of the pipeline -----------------------------------------------

@pytest.mark.parametrize("name", ALL)
def test_placement_check_never_raises(name):
    out = plate_placement.assess(fixture(name))
    assert out["schema_version"] == plate_placement.SCHEMA_VERSION
    if out["available"]:
        for item in out["items"]:
            assert item["dimensions"]["x"] >= 0


@pytest.mark.parametrize("name", ALL)
def test_cost_either_costs_or_explains(name):
    out = project_cost.estimate(fixture(name))
    if out["available"]:
        assert out["cost"] is not None and out["basis"] == project_cost.BASIS_SLICED
    else:
        assert out["reason"], "a refusal must carry its reason"


@pytest.mark.parametrize("name", ALL)
def test_ecosystem_advice_is_earned_on_real_files(name):
    advice = ecosystem.advise(fixture(name))
    for entry in [advice["primary"], *advice["alternatives"]]:
        if entry and entry["score"] > 0 and entry["id"] != "snapmaker-orca":
            assert entry["why"], f"{entry['id']} was suggested with no reason"


@pytest.mark.parametrize("name", [ORCA_DUAL, BAMBU_PA])
def test_preparing_a_real_project_is_fully_accounted_for(tmp_path, name):
    """The strongest end-to-end claim: convert a genuine slicer project and have
    the fidelity audit account for every element."""
    from snapstudio_core.convert import convert_to_u1

    src = fixture(name)
    result = convert_to_u1(src, out_dir=str(tmp_path / "out"))
    assert result.output_path

    report = fidelity.audit(src, result.output_path)
    assert report["available"] is True
    assert not report["unverified"], (
        f"unaccounted elements in a real project: "
        f"{[r['element'] for r in report['unverified']]}")


@pytest.mark.parametrize("name", ALL)
def test_the_original_is_never_modified(tmp_path, name):
    import hashlib

    from snapstudio_core.convert import convert_to_u1

    src = Path(fixture(name))
    before = hashlib.sha256(src.read_bytes()).hexdigest()
    try:
        convert_to_u1(str(src), out_dir=str(tmp_path / "out"))
    except Exception:
        pass  # a refusal is fine; modifying the input is not
    assert hashlib.sha256(src.read_bytes()).hexdigest() == before
