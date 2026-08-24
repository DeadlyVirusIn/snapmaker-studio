"""Studio's paint decoder against files two real slicers actually wrote.

The synthetic suite proves the decoder is self-consistent. These prove it is
*right*: both fixtures were round-tripped through the slicer itself, so the
attribute strings in them were written by PrusaSlicer and OrcaSlicer from their
own decoded models. See PROVENANCE.md beside the fixtures for how they were made
and what each one is evidence of.

These fixtures are committed, so this runs everywhere. Regenerating them needs a
slicer, which CI does not have — that is `tools/fixtures/make_painted.py`.
"""
from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

import pytest

from snapstudio_core import paint_codec as codec
from snapstudio_core import painted_color as painted

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "painted"
PRUSA = FIXTURES / "prusaslicer-2.9.6-painted-cube.3mf"
ORCA = FIXTURES / "orcaslicer-2.4.2-painted-cube.3mf"
EVIDENCE = FIXTURES / "slice-evidence.json"

# What was painted onto the cube before either slicer saw it.
EXPECTED_SLOTS = [1, 2, 3, 4, 5]
EXPECTED_PAINTED_TRIANGLES = 8
# The subdivided triangle, as both slicers wrote it back.
SUBDIVIDED = "480C501C3"


def attributes(path: Path) -> list[str]:
    out = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(".model"):
                continue
            text = archive.read(name).decode("utf-8", "ignore")
            out += re.findall(r'(?:paint_color|slic3rpe:mmu_segmentation)="([^"]*)"',
                              text)
    return out


@pytest.mark.parametrize("path", [PRUSA, ORCA], ids=["prusaslicer", "orcaslicer"])
def test_the_fixture_is_the_one_the_provenance_record_describes(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest in (Path(FIXTURES / "PROVENANCE.md").read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", [PRUSA, ORCA], ids=["prusaslicer", "orcaslicer"])
def test_a_real_slicers_own_output_decodes_to_what_was_painted(path):
    result = painted.read(str(path))
    assert result["available"] is True
    assert result["slots_referenced"] == EXPECTED_SLOTS
    assert result["painted_triangle_count"] == EXPECTED_PAINTED_TRIANGLES
    assert result["confidence"] == painted.CONFIRMED
    assert result["malformed_triangle_count"] == 0


def test_the_two_dialects_are_the_same_encoding_under_different_names():
    prusa, orca = painted.read(str(PRUSA)), painted.read(str(ORCA))
    assert prusa["dialect"] == painted.DIALECT_PRUSA
    assert orca["dialect"] == painted.DIALECT_BAMBU
    assert prusa["attribute"] != orca["attribute"]
    assert attributes(PRUSA) == attributes(ORCA)
    assert prusa["slots_referenced"] == orca["slots_referenced"]
    assert prusa["painted_triangle_count"] == orca["painted_triangle_count"]


@pytest.mark.parametrize("path", [PRUSA, ORCA], ids=["prusaslicer", "orcaslicer"])
def test_a_subdivided_triangle_survived_the_slicer_byte_for_byte(path):
    # The slicer re-serialised this from its own decoded model. Getting the same
    # string back is what proves Studio and the slicer read it the same way.
    assert SUBDIVIDED in attributes(path)
    leaves, truncated = codec.decode(SUBDIVIDED, ((0, 0, 0), (10, 0, 0), (0, 10, 0)))
    assert not truncated
    assert sorted({leaf.state for leaf in leaves}) == [0, 1, 2, 3, 4]
    assert sum(leaf.fraction for leaf in leaves) == pytest.approx(1.0)


def test_the_areas_add_up_to_the_cube_that_was_painted():
    result = painted.read(str(PRUSA))
    obj = result["objects"][0]
    # A 20 mm cube: six faces of 400 mm².
    assert obj["mesh_area_mm2"] == pytest.approx(2400.0)
    painted_area = sum(a["area_mm2"] for a in result["slots"])
    assert 0 < painted_area < obj["mesh_area_mm2"]


def test_the_slice_evidence_matches_what_the_fixture_paints():
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    result = painted.read(str(PRUSA))
    assert evidence["painted_states_in_fixture"] == result["slots_referenced"]
    # A state names filament N; the G-code tool for it is N-1. Both statements
    # are checked against the tools the real slice actually used.
    tools = sorted(int(name[1:]) for name in evidence["tool_changes_in_gcode"])
    assert tools == [slot - 1 for slot in result["slots_referenced"]]
    assert len(evidence["filament_used_mm"]) == len(result["slots_referenced"])


def test_orcaslicer_declares_no_painting_version_and_studio_does_not_invent_one():
    result = painted.read(str(ORCA))
    assert result["format_version"] is None
    assert result["format_version_known"] is False
    # The Prusa dialect does declare one, and it is read rather than assumed.
    assert painted.read(str(PRUSA))["format_version"] == 1


@pytest.mark.parametrize("path", [PRUSA, ORCA], ids=["prusaslicer", "orcaslicer"])
def test_preparing_a_copy_of_a_real_painted_project_keeps_the_painting(path, tmp_path):
    # The end-to-end claim: a genuine painted project, through Studio's own
    # prepare, and the painting is still there — checked against the painting
    # itself rather than against the mesh surviving.
    import shutil

    from snapstudio_core import fidelity
    from snapstudio_core.convert import convert_to_u1

    # Preparing leaves a .orig backup beside its *source*, so the fixture is
    # copied out of the repository first. A test must not write into the tree it
    # is testing.
    source = tmp_path / path.name
    shutil.copy2(path, source)
    result = convert_to_u1(str(source), out_dir=str(tmp_path / "prepared"))
    assert result.output_path

    after = painted.read(result.output_path)
    assert after["slots_referenced"] == EXPECTED_SLOTS
    assert after["painted_triangle_count"] == EXPECTED_PAINTED_TRIANGLES

    report = fidelity.audit(str(source), result.output_path)
    row = [r for r in report["rows"] if r["element"] == "Painted colour"][0]
    assert row["status"] == fidelity.PRESERVED_EXACT, row
