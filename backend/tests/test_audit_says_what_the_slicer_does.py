"""A fact the copy carries faithfully, and the slicer then ignores.

Two rows in the fidelity audit are true of the two files and easy to read as
promises about the plate. Both were measured against Snapmaker Orca 2.3.5 by
handing it a prepared project and reading the project it saved back:

* a part's filament above the profile's filament count comes back **unassigned**,
  not clamped — the same file with the part one slot lower keeps it exactly;
* painting written in PrusaSlicer's `slic3rpe:mmu_segmentation` comes back with
  **no facet attributes at all**, because Orca reads `paint_color`.

Neither changes what Studio should write: the source states those facts and a copy
stating anything else would be a different project. What changes is that the row
now says what happens next, instead of stopping at "preserved".
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from snapstudio_core.convert import convert_to_u1
from snapstudio_core.fidelity import audit

FIXTURES = Path(__file__).parent / "fixtures" / "prusa-semantics"
TWO_VOLUMES = FIXTURES / "H_two_volumes_different_slots_out.3mf"


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    prepared = convert_to_u1(str(TWO_VOLUMES), out_dir=tempfile.mkdtemp()).output_path
    return audit(str(TWO_VOLUMES), prepared)["rows"]


def one(rows: list[dict], prefix: str) -> dict:
    found = [r for r in rows if r["element"].startswith(prefix)]
    assert found, f"no row starting {prefix!r}"
    return found[0]


def test_the_copy_still_states_the_filament_the_source_stated(rows):
    """Carrying the number is right even when the printer cannot use it."""
    row = one(rows, "Filament for each part")
    assert row["status"] == "preserved_exact"
    assert "[2, 5]" in row["detail"]


def test_a_filament_the_profile_does_not_have_is_named(rows):
    row = one(rows, "Filament for each part")
    assert row["reason"] and "filament 5" in row["reason"]
    assert "configures 4" in row["reason"]
    assert "unassigned" in row["reason"], "say what Orca does, not only that it differs"


def test_painting_in_the_wrong_dialect_is_named(rows):
    """Byte-identical is true of the files. It is not true of the plate."""
    row = one(rows, "Painted colour")
    assert row["status"] == "preserved_exact"
    assert row["reason"] and "no painting" in row["reason"]
    assert "paint them again in Orca" in row["reason"]


def test_painting_already_in_the_targets_dialect_is_not_warned_about(tmp_path):
    """The warning is about the dialect, not about painting."""
    from snapstudio_core.fidelity import _paint_dialect_reason
    from snapstudio_core.container import ThreeMF

    orca = (Path(__file__).parent / "fixtures" / "painted"
            / "snapmaker-orca-2.3.5-authored.3mf")
    assert _paint_dialect_reason(ThreeMF.open(str(orca))) is None


def test_a_project_whose_filaments_all_fit_gets_no_such_warning(tmp_path):
    """The warning is about a slot the printer does not have, not about slots."""
    plain = FIXTURES / "C_object_slot3_out.3mf"
    prepared = convert_to_u1(str(plain), out_dir=str(tmp_path)).output_path
    for row in audit(str(plain), prepared)["rows"]:
        assert "does not have" not in (row["reason"] or ""), row["element"]
