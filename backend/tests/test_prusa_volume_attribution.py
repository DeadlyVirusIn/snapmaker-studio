"""Whose filament does an unpainted patch print in? Its own volume's.

An object's volumes may print in different filaments, and the area nobody painted
prints in whatever the volume holding it is assigned. Studio used to answer that
question once per object, taking the first volume that stated a slot as the
answer for every facet — so an object whose second volume printed in filament 5
had that volume's unpainted area counted under the first volume's filament. On
the two-volume fixture that was 50 mm² under the wrong colour.

What a volume's triangle range means was measured against PrusaSlicer 2.9.6
rather than assumed. `firstid`/`lastid` are **inclusive**, and the slicer writes
contiguous ascending ranges that partition the mesh:

* handed ranges with a gap, it re-laid the volumes contiguously and wrote a
  shorter mesh — the gap does not survive;
* handed overlapping ranges, it duplicated the shared triangles into the second
  volume and renumbered — the overlap does not survive either;
* handed a reversed range, or one past the end of the mesh, it refused to write
  a file at all: "Found invalid triangle id".

So a genuine file answers "which volume owns this facet" exactly once. A file
that is not genuine may answer twice or not at all, and both of those are
*unknown* — never a sibling volume's filament, because a sibling's filament is a
statement about the sibling.
"""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path

import pytest

from snapstudio_core import painted_color as PC
from snapstudio_core.container import ThreeMF

FIXTURES = Path(__file__).parent / "fixtures" / "prusa-volumes"
MANIFEST = FIXTURES / "MANIFEST.json"
CONFIG = "Metadata/Slic3r_PE_model.config"


def slots_of(path: Path) -> dict:
    """Every slot the project names, and the area attributed to each."""
    result = PC.read_container(ThreeMF.open(str(path)))
    assert result["available"], result
    return {entry["slot"]: round(entry.get("area_mm2") or 0.0, 4)
            for entry in result.get("slots", [])}


def unpainted(path: Path) -> list[dict]:
    """The unpainted assignments, one per volume, with the slot each resolved to."""
    result = PC.read_container(ThreeMF.open(str(path)))
    out = []
    for entry in result.get("objects") or ():
        for assignment in entry.get("assignments") or ():
            if not assignment.get("painted"):
                out.append({"volume": assignment.get("volume"),
                            "slot": assignment.get("slot"),
                            "area": round(assignment.get("area_mm2") or 0.0, 4),
                            "evidence": assignment.get("evidence")})
    return sorted(out, key=lambda row: (row["volume"] is None, row["volume"]))


# --- the fixtures are the slicer's own work -----------------------------------

def test_every_fixture_is_the_file_the_slicer_wrote():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["_provenance"]["slicer"].startswith("PrusaSlicer 2.9.6")
    import hashlib

    for name, entry in manifest["files"].items():
        path = FIXTURES / name
        assert path.exists(), name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], name


def test_the_ranges_are_inclusive_and_partition_the_mesh():
    """Six facets from 0 to 5, not five; and nothing between the volumes."""
    for name in ("A_two_volumes_same_slot", "B_two_volumes_slots_2_and_5",
                 "K_three_volumes_2_3_4"):
        with zipfile.ZipFile(FIXTURES / f"{name}.3mf") as z:
            config = z.read(CONFIG).decode("utf-8")
            root = z.read("3D/3dmodel.model").decode("utf-8")
        ranges = [(int(a), int(b)) for a, b in
                  re.findall(r'firstid="(\d+)"[^>]*lastid="(\d+)"', config)]
        covered = sum(last - first + 1 for first, last in ranges)
        assert covered == root.count("<triangle ") == 12, name
        for (first, last), (next_first, _next_last) in zip(ranges, ranges[1:]):
            assert first <= last and next_first == last + 1, name


# --- what each volume's unpainted area prints in ------------------------------
#
# This cube has exactly one partly-painted facet, and it sits in the **second**
# volume in every layout here. So the second volume is where silence is felt, and
# the fixtures put the silence there deliberately: a reader that leaked a slot
# from a sibling would answer with the *first* volume's filament, which these
# name and which is never the right answer.

def only_unpainted(name: str) -> dict:
    rows = unpainted(FIXTURES / f"{name}.3mf")
    assert len(rows) == 1, rows
    return rows[0]


def test_A_two_volumes_on_one_filament():
    assert only_unpainted("A_two_volumes_same_slot")["slot"] == 2


def test_B_the_patch_prints_in_its_own_volumes_filament():
    """The case the old reader got wrong: it answered 2, the first volume's."""
    row = only_unpainted("B_two_volumes_slots_2_and_5")
    assert (row["volume"], row["slot"]) == (1, 5)
    assert "volume 2 is assigned slot 5" in row["evidence"]


def test_C_an_explicit_volume_outranks_its_object():
    """Object on 3, the patch's volume on 5. The volume wins."""
    row = only_unpainted("C_object_3_volume_two_5")
    assert (row["volume"], row["slot"]) == (1, 5)


def test_D_an_explicit_volume_needs_no_object_to_agree():
    row = only_unpainted("D_object_silent_volume_two_4")
    assert (row["volume"], row["slot"]) == (1, 4)


def test_E_all_volumes_silent_is_unknown():
    row = only_unpainted("E_all_volumes_silent")
    assert row["slot"] is None and "cannot say" in row["evidence"]


def test_K_three_volumes_each_keep_their_own():
    """Three volumes; the patch is in the middle one, on filament 3."""
    row = only_unpainted("K_three_volumes_2_3_4")
    assert (row["volume"], row["slot"]) == (1, 3)


def test_F_a_silent_volume_falls_back_to_its_object_not_its_sibling():
    """The sharp one. The patch's volume is silent, its sibling says 5, the
    object says 3 — and the answer is 3."""
    row = only_unpainted("F_second_volume_silent_object_3")
    assert (row["volume"], row["slot"]) == (1, 3), "5 here would be the sibling's"
    assert "its object is assigned slot 3" in row["evidence"]


def test_G_a_silent_volume_under_a_silent_object_is_unknown_not_its_sibling():
    """Sibling on 5, nothing else stated. Unknown, and emphatically not 5."""
    row = only_unpainted("G_second_volume_silent_object_silent")
    assert row["slot"] is None, "5 here would be the sibling's"
    assert "cannot say" in row["evidence"]


def test_no_unpainted_area_ever_lands_under_a_siblings_filament():
    """Across every fixture, at once."""
    import zipfile as _zipfile

    for path in sorted(FIXTURES.glob("*.3mf")):
        with _zipfile.ZipFile(path) as z:
            config = z.read(CONFIG).decode("utf-8")
        volumes = re.findall(r"<volume\b.*?</volume>", config, re.S)
        object_slot = re.search(
            r'<metadata type="object" key="extruder" value="(\d+)"', config)
        for row in unpainted(path):
            if row["slot"] is None or row["volume"] is None:
                continue
            own = re.search(r'key="extruder" value="(\d+)"', volumes[row["volume"]])
            expected = int(own.group(1)) if own else (
                int(object_slot.group(1)) if object_slot else None)
            assert row["slot"] == expected, (path.name, row, expected)


# --- F to J: ranges the slicer refuses to write -------------------------------
#
# PrusaSlicer will not produce any of these, which is why they are built here
# rather than authored. They are what a file that is not genuine can contain, and
# the reader must answer them with "unknown" rather than with a neighbour's slot.

def hostile(tmp_path: Path, ranges: list[tuple[int, int]], slots: list) -> Path:
    source = FIXTURES / "B_two_volumes_slots_2_and_5.3mf"
    target = tmp_path / "hostile.3mf"
    volumes = "".join(
        f'  <volume firstid="{first}" lastid="{last}">\n'
        '   <metadata type="volume" key="volume_type" value="ModelPart"/>\n'
        + (f'   <metadata type="volume" key="extruder" value="{slot}"/>\n'
           if slot is not None else "")
        + "  </volume>\n"
        for (first, last), slot in zip(ranges, slots))
    config = ('<?xml version="1.0" encoding="UTF-8"?>\n<config>\n'
              ' <object id="1" instances_count="1">\n'
              '  <metadata type="object" key="name" value="cube.stl"/>\n'
              + volumes + " </object>\n</config>\n")
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(target, "w") as dst:
        for item in src.infolist():
            data = config.encode("utf-8") if item.filename == CONFIG else src.read(
                item.filename)
            dst.writestr(item.filename, data)
    return target


def test_F_a_facet_in_a_gap_belongs_to_no_volume(tmp_path):
    """0–3 and 8–11 leave facets 4–7 unclaimed. They are unknown, not slot 2."""
    path = hostile(tmp_path, [(0, 3), (8, 11)], ["2", "5"])
    rows = unpainted(path)
    orphans = [row for row in rows if row["volume"] is None]
    assert orphans, "a facet no volume claims must be reported"
    assert all(row["slot"] is None for row in orphans)
    assert "no volume of this object claims that facet" in orphans[0]["evidence"]


def test_G_a_facet_two_volumes_claim_is_unknown(tmp_path):
    """Overlapping ranges make ownership ambiguous, and ambiguous is not a slot."""
    path = hostile(tmp_path, [(0, 7), (5, 11)], ["2", "5"])
    rows = unpainted(path)
    assert any(row["volume"] is None and row["slot"] is None for row in rows)


def test_H_a_malformed_range_claims_nothing(tmp_path):
    path = hostile(tmp_path, [(0, 5), (6, 11)], ["2", "5"])
    with zipfile.ZipFile(path) as z:
        config = z.read(CONFIG).decode("utf-8")
    broken = config.replace('lastid="11"', 'lastid="not-a-number"')
    target = tmp_path / "malformed.3mf"
    with zipfile.ZipFile(path) as src, zipfile.ZipFile(target, "w") as dst:
        for item in src.infolist():
            data = broken.encode("utf-8") if item.filename == CONFIG else src.read(
                item.filename)
            dst.writestr(item.filename, data)
    rows = unpainted(target)
    assert any(row["slot"] is None for row in rows), rows


def test_I_a_reversed_range_owns_nothing(tmp_path):
    """`firstid` past `lastid` describes no facets, so it claims none.

    The volume is still in the file and still states filament 2; what it does not
    do is collect facets it never claimed. Every facet it would have covered had
    the range been the right way round belongs to nobody.
    """
    assert [PC.volume_of([(5, 0), (6, 11)], facet) for facet in range(6)] == [None] * 6
    path = hostile(tmp_path, [(5, 0), (6, 11)], ["2", "5"])
    rows = unpainted(path)
    assert all(row["volume"] != 0 for row in rows), rows
    assert all(row["slot"] != 2 for row in rows), "the reversed volume claimed a facet"


def test_J_a_range_past_the_mesh_claims_only_what_exists(tmp_path):
    path = hostile(tmp_path, [(0, 5), (6, 99)], ["2", "5"])
    rows = unpainted(path)
    assert [row["slot"] for row in rows if row["volume"] == 1] == [5]
    # Nothing outside the mesh is invented: the facet count is still the cube's.
    result = PC.read_container(ThreeMF.open(str(path)))
    assert result["painted_triangle_count"] == 8


@pytest.mark.parametrize("facet,expected", [(0, 0), (5, 0), (6, 1), (11, 1), (12, None)])
def test_the_ownership_rule_itself(facet, expected):
    assert PC.volume_of([(0, 5), (6, 11)], facet) == expected


# --- and the audit can compare the whole attribution again --------------------

def test_the_copy_and_the_source_agree_on_every_slot(tmp_path):
    """The 50 mm² that used to move, and no longer does.

    Preparing the two-volume fixture carries each part's own filament, so the
    unpainted patch prints in filament 5 in the copy. It always did — what was
    wrong was the *source* reading, which put it under filament 2 because that is
    what the object's first volume said. With both sides reading per volume the
    per-slot areas match exactly, which is why the audit compares them again
    rather than comparing painted area alone.
    """
    import tempfile

    from snapstudio_core.convert import convert_to_u1

    source = Path(__file__).parent / "fixtures" / "prusa-semantics" / (
        "H_two_volumes_different_slots_out.3mf")
    prepared = convert_to_u1(str(source), out_dir=tempfile.mkdtemp()).output_path
    before, after = slots_of(source), slots_of(Path(prepared))
    assert before == after, (before, after)
    assert before[5] == 250.0, "the patch belongs to the volume on filament 5"
    assert before[2] == 425.0
