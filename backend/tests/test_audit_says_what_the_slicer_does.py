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

import json
import tempfile
import zipfile
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


def test_the_copy_states_the_filament_the_source_stated(rows):
    row = one(rows, "Filament for each part")
    assert row["status"] == "preserved_exact"
    assert "[2, 5]" in row["detail"]


def test_the_copy_declares_enough_filaments_to_mean_it(tmp_path):
    """Stating slot 5 against four declared filaments is a reference Orca drops.

    Measured against Orca 2.3.5: with four declared, a part on 5 came back
    unassigned; with five declared, it came back as 5. So the copy declares as
    many as the source refers to, and the four physical nozzles are untouched.
    """
    prepared = convert_to_u1(str(TWO_VOLUMES), out_dir=str(tmp_path)).output_path
    with zipfile.ZipFile(prepared) as z:
        settings = json.loads(
            z.read("Metadata/project_settings.config").decode("utf-8"))
    assert len(settings["filament_settings_id"]) == 5
    assert len(settings["filament_colour"]) == 5
    assert len(settings["flush_volumes_matrix"]) == 25, "the flush table is square in it"
    assert len(settings["flush_volumes_vector"]) == 10
    assert len(settings["nozzle_diameter"]) == 4, "a fifth toolhead was not invented"
    assert len(settings["printable_area"]) == 4, "the bed is not a filament array"


def test_no_warning_when_every_slot_is_declared(rows):
    """The row is about a slot the project does not declare, not about slots."""
    row = one(rows, "Filament for each part")
    assert not (row["reason"] or ""), row["reason"]


def test_a_slot_the_copy_does_not_declare_is_still_named(tmp_path):
    """Shrink the declaration back to four and the audit must notice."""
    prepared = Path(convert_to_u1(str(TWO_VOLUMES), out_dir=str(tmp_path)).output_path)
    shrunk = tmp_path / "shrunk.3mf"
    with zipfile.ZipFile(prepared) as src, zipfile.ZipFile(shrunk, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "Metadata/project_settings.config":
                settings = json.loads(data.decode("utf-8"))
                for key, value in list(settings.items()):
                    if isinstance(value, list) and len(value) == 5:
                        settings[key] = value[:4]
                data = json.dumps(settings).encode("utf-8")
            dst.writestr(item, data)

    row = one(audit(str(TWO_VOLUMES), str(shrunk))["rows"], "Filament for each part")
    assert row["reason"] and "filament 5" in row["reason"]
    assert "declares 4" in row["reason"]
    assert "unassigned" in row["reason"], "say what Orca does, not only that it differs"


def test_painting_crosses_in_the_targets_own_dialect(rows):
    """The copy no longer carries a name Snapmaker Orca does not read."""
    row = one(rows, "Painted colour")
    assert row["status"] == "preserved_semantic"
    assert "Orca's own vocabulary" in (row["reason"] or "")
    assert "no painting" not in (row["reason"] or ""), (
        "the warning about painting that does not arrive must be gone")


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
