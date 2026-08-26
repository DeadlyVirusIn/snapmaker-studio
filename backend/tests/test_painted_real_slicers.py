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
    if path is PRUSA:
        # The bits are the same string; the attribute's name is not. Snapmaker
        # Orca reads `paint_color` and opens a copy carrying PrusaSlicer's name
        # with nothing painted, so the copy states the painting in the target's
        # own vocabulary — the same painting, restated.
        assert row["status"] == fidelity.PRESERVED_SEMANTIC, row
        assert "Orca's own vocabulary" in (row["reason"] or ""), row
    else:
        assert row["status"] == fidelity.PRESERVED_EXACT, row


# --- paint the slicers authored themselves -----------------------------------
#
# The two fixtures above were round-tripped: Studio wrote the paint and a slicer
# wrote it back. These two were *painted in the slicer's own UI* — its gizmo, its
# brush, its filament palette — and saved by it. That is the difference between
# "the slicer agrees with our encoding" and "this is what the slicer produces",
# and it is what raised the Snapmaker Orca and BambuStudio rows in
# docs/PAINTED_COLOUR.md from PARTIAL.
#
# One of them found a real defect: a single facet of a 180 mm slab, painted with
# Snapmaker Orca's round brush, came back as a 35,460-character attribute, and
# Studio refused anything over 4,096. See test_the_longest_real_attribute_decodes.

SNAPMAKER_AUTHORED = FIXTURES / "snapmaker-orca-2.3.5-authored.3mf"
BAMBU_AUTHORED = FIXTURES / "bambustudio-2.08.02.61-authored.3mf"


@pytest.mark.parametrize("path", [SNAPMAKER_AUTHORED, BAMBU_AUTHORED],
                         ids=["snapmaker-orca", "bambustudio"])
def test_paint_authored_in_the_slicer_itself_is_read(path):
    result = painted.read(str(path))
    assert result["available"] is True
    assert result["dialect"] == painted.DIALECT_BAMBU
    assert result["painted_triangle_count"] >= 2
    assert result["slots_referenced"], "no filament slot was read"
    assert result["malformed_triangle_count"] == 0, \
        result["objects"][0]["malformed_examples"]
    assert result["facets_outside_mesh"] == 0
    assert result["confidence"] == painted.CONFIRMED


def test_snapmaker_orca_paints_with_more_than_one_filament():
    result = painted.read(str(SNAPMAKER_AUTHORED))
    assert result["slots_referenced"] == [2, 3, 4]
    for slot in result["slots"]:
        if not slot["from_painting"]:
            continue
        assert slot["area_mm2"] > 0
        assert slot["painted_z_min_mm"] is not None


def test_bambu_studio_paints_whole_facets_of_a_known_area():
    # Both triangles of the slab's 180 x 180 mm face: an exact number, which is
    # what makes this a test rather than an impression.
    result = painted.read(str(BAMBU_AUTHORED))
    slot = [s for s in result["slots"] if s["slot"] == 2][0]
    assert slot["triangles_touching"] == 2
    assert slot["area_mm2"] == pytest.approx(32_400.0)


def test_the_longest_real_attribute_decodes():
    """A brush stroke inside one large facet subdivides it thousands of times.

    Studio capped a paint attribute at 4,096 characters — a number chosen before
    any slicer-authored file had been seen. Snapmaker Orca's own brush produced
    35,460 characters for a single facet, and the cap turned a real project into
    a partly undecodable one.
    """
    longest = ""
    for attribute in attributes(SNAPMAKER_AUTHORED):
        if len(attribute) > len(longest):
            longest = attribute
    assert len(longest) > 10_000, f"longest attribute is only {len(longest)} characters"
    leaves, truncated = codec.decode(longest, ((0, 0, 0), (180, 0, 0), (0, 180, 0)))
    assert not truncated
    assert len(leaves) > 1_000
    assert sum(leaf.fraction for leaf in leaves) == pytest.approx(1.0)


@pytest.mark.parametrize("path", [SNAPMAKER_AUTHORED, BAMBU_AUTHORED],
                         ids=["snapmaker-orca", "bambustudio"])
def test_authored_paint_survives_preparing_a_copy(path, tmp_path):
    import shutil

    from snapstudio_core import fidelity
    from snapstudio_core.convert import convert_to_u1

    source = tmp_path / path.name
    shutil.copy2(path, source)
    result = convert_to_u1(str(source), out_dir=str(tmp_path / "prepared"))
    assert result.output_path

    before = painted.read(str(source))
    after = painted.read(result.output_path)
    assert after["slots_referenced"] == before["slots_referenced"]
    assert after["painted_triangle_count"] == before["painted_triangle_count"]

    report = fidelity.audit(str(source), result.output_path)
    row = [r for r in report["rows"] if r["element"] == "Painted colour"][0]
    if path is PRUSA:
        # The bits are the same string; the attribute's name is not. Snapmaker
        # Orca reads `paint_color` and opens a copy carrying PrusaSlicer's name
        # with nothing painted, so the copy states the painting in the target's
        # own vocabulary — the same painting, restated.
        assert row["status"] == fidelity.PRESERVED_SEMANTIC, row
        assert "Orca's own vocabulary" in (row["reason"] or ""), row
    else:
        assert row["status"] == fidelity.PRESERVED_EXACT, row


@pytest.mark.parametrize("path", [SNAPMAKER_AUTHORED, BAMBU_AUTHORED],
                         ids=["snapmaker-orca", "bambustudio"])
def test_damaging_authored_paint_is_caught_rather_than_excused(path, tmp_path):
    import shutil
    import zipfile

    from snapstudio_core import fidelity

    source = tmp_path / path.name
    shutil.copy2(path, source)
    damaged = tmp_path / "damaged.3mf"
    with zipfile.ZipFile(source) as archive:
        parts = {name: archive.read(name) for name in archive.namelist()}
    for name, blob in list(parts.items()):
        if name.lower().endswith(".model"):
            parts[name] = re.sub(rb'paint_color="[^"]*"', b'paint_color="4"', blob)
    with zipfile.ZipFile(damaged, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, blob in parts.items():
            archive.writestr(name, blob)

    report = fidelity.audit(str(source), str(damaged))
    row = [r for r in report["rows"] if r["element"] == "Painted colour"][0]
    assert row["status"] == fidelity.CHANGED, row
