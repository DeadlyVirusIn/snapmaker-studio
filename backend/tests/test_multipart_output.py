"""Real parts, and the ways a file can lie about having them.

A prepared multi-part project makes the same claim in three places: the root
model's `<components>`, the mesh objects those point at, and the `<part>` records
in `model_settings.config`. All three have to describe one structure. A `<part>`
row over a single mesh is a claim, not a part, and that is exactly what Studio
used to write.

The first half of this file proves the structure is real against a project
PrusaSlicer authored — one object, two volumes on filaments 2 and 5, expressed by
PrusaSlicer as triangle ranges inside one mesh. The second half damages that
output twelve different ways and requires the validator or the fidelity audit to
catch each one.
"""
from __future__ import annotations

import re
import tempfile
import zipfile
from pathlib import Path

import pytest

from snapstudio_core import assignments as A, multipart as MP
from snapstudio_core.container import ThreeMF
from snapstudio_core.convert import convert_to_u1

FIXTURES = Path(__file__).parent / "fixtures" / "prusa-semantics"
TWO_VOLUMES = FIXTURES / "H_two_volumes_different_slots_out.3mf"
ONE_VOLUME = FIXTURES / "A_no_assignment_out.3mf"
ROOT = "3D/3dmodel.model"
OBJECTS = "3D/Objects/object_1.model"
SETTINGS = "Metadata/model_settings.config"


@pytest.fixture(scope="module")
def prepared() -> str:
    return convert_to_u1(str(TWO_VOLUMES), out_dir=tempfile.mkdtemp()).output_path


def read(path: str, name: str) -> str:
    with zipfile.ZipFile(path) as z:
        return z.read(name).decode("utf-8")


def damaged(prepared: str, tmp_path: Path, name: str, change) -> str:
    """The prepared archive with one part rewritten."""
    out = tmp_path / "damaged.3mf"
    with zipfile.ZipFile(prepared) as src, zipfile.ZipFile(out, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == name:
                data = change(data.decode("utf-8")).encode("utf-8")
            dst.writestr(item.filename, data)
    return str(out)


# --- the structure is real ---------------------------------------------------

def test_the_geometry_moves_out_of_the_root_into_object_files(prepared):
    root = read(prepared, ROOT)
    assert root.count("<mesh>") == 0, "the root must reference geometry, not hold it"
    assert read(prepared, OBJECTS).count("<mesh>") == 2


def test_one_component_per_part_and_the_ids_line_up(prepared):
    components = re.findall(r'<component[^>]*objectid="(\d+)"', read(prepared, ROOT))
    meshes = re.findall(r'<object id="(\d+)"', read(prepared, OBJECTS))
    parts = re.findall(r'<part id="(\d+)"', read(prepared, SETTINGS))
    assert components == ["1", "2"]
    assert meshes == components == parts, (
        "component objectid, mesh object id and part id are the same number — that "
        "identity is what makes the metadata describe the geometry")


def test_the_build_places_the_composite_object(prepared):
    root = read(prepared, ROOT)
    composite = re.search(r'<object id="(\d+)"[^>]*>\s*<components>', root).group(1)
    assert re.findall(r'<item[^>]*objectid="(\d+)"', root) == [composite]


def test_the_object_file_is_declared_as_a_relationship(prepared):
    assert "/3D/Objects/object_1.model" in read(prepared, "3D/_rels/3dmodel.model.rels")


def test_the_validator_passes_its_own_output(prepared):
    result = MP.validate_archive(ThreeMF.open(prepared))
    assert result["multipart"] is True and result["parts"] == 2
    assert result["ok"] and result["problems"] == []


# --- geometry -----------------------------------------------------------------

def source_mesh() -> tuple[list[str], list[str]]:
    root = read(str(TWO_VOLUMES), ROOT)
    body = re.search(r"<object[^>]*>.*?</object>", root, re.S).group(0)
    return MP.read_mesh(body)


def test_no_triangle_is_lost_or_duplicated(prepared):
    _v, triangles = source_mesh()
    assert read(prepared, OBJECTS).count("<triangle ") == len(triangles) == 12


def test_each_part_carries_exactly_its_own_facets(prepared):
    body = read(prepared, OBJECTS)
    for object_id, expected in (("1", 6), ("2", 6)):
        block = re.search(rf'<object id="{object_id}".*?</object>', body, re.S).group(0)
        assert block.count("<triangle ") == expected


def test_the_parts_recombine_into_the_source_geometry_exactly(prepared):
    """Not a bounding box — the actual solid, facet by facet, in winding order."""
    vertices, triangles = source_mesh()
    whole = MP.geometry_digest(vertices, triangles)

    body = read(prepared, OBJECTS)
    combined_vertices: list[str] = []
    combined_triangles: list[str] = []
    for object_id in ("1", "2"):
        block = re.search(rf'<object id="{object_id}".*?</object>', body, re.S).group(0)
        part_vertices, part_triangles = MP.read_mesh(block)
        base = len(combined_vertices)
        combined_vertices.extend(part_vertices)
        combined_triangles.extend(
            re.sub(r'v([123])="(\d+)"',
                   lambda m: f'v{m.group(1)}="{int(m.group(2)) + base}"', tag)
            for tag in part_triangles)
    assert MP.geometry_digest(combined_vertices, combined_triangles) == whole


def test_the_two_parts_are_different_solids(prepared):
    body = read(prepared, OBJECTS)
    digests = []
    for object_id in ("1", "2"):
        block = re.search(rf'<object id="{object_id}".*?</object>', body, re.S).group(0)
        digests.append(MP.geometry_digest(*MP.read_mesh(block)))
    assert digests[0] != digests[1], "a split that copies the same mesh twice is not a split"


def test_no_geometry_is_duplicated_across_the_archive(prepared):
    with zipfile.ZipFile(prepared) as z:
        total = sum(z.read(n).decode("utf-8", "ignore").count("<triangle ")
                    for n in z.namelist() if n.endswith(".model"))
    assert total == 12


# --- filament -----------------------------------------------------------------

def test_each_part_keeps_its_own_filament(prepared):
    settings = read(prepared, SETTINGS)
    parts = re.findall(r'<part id="(\d+)".*?</part>', settings, re.S)
    slots = re.findall(r'<part id="\d+".*?key="extruder" value="(\d+)".*?</part>',
                       settings, re.S)
    assert parts == ["1", "2"]
    assert slots == ["2", "5"], "slot 5 must not be clamped to fit four toolheads"


def test_the_objects_own_assignment_stays_separate(prepared):
    """The source object assigned nothing; that is still true of the copy."""
    head = read(prepared, SETTINGS).split("<part", 1)[0]
    assert re.search(r'key="extruder" value="0"', head)


def test_the_audit_now_reports_the_parts_as_preserved(prepared):
    before = A.read(ThreeMF.open(str(TWO_VOLUMES)))
    after = A.read(ThreeMF.open(prepared))
    result = A.compare(before, after)
    rows = [r for r in result["semantics"] if r["kind"] == "volume_filament"]
    assert rows and rows[0]["status"] == A.PRESERVED_EXACT
    assert result["rows"][0]["status"] != A.NOT_REPRESENTABLE


def unpainted(source: Path, tmp_path: Path) -> Path:
    """The fixture with every painted facet stripped.

    Every project in this fixture family is painted, and painting now earns the
    target layout on its own, so the plain path needs a plain file to be shown on.
    """
    target = tmp_path / "unpainted.3mf"
    with zipfile.ZipFile(source) as src, zipfile.ZipFile(target, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename.endswith(".model"):
                data = re.sub(rb'\s*slic3rpe:mmu_segmentation="[^"]*"', b"", data)
            dst.writestr(item, data)
    return target


def test_a_single_unpainted_volume_still_takes_the_simple_path(tmp_path):
    """The change is narrow on purpose: nothing splits that has nothing to split."""
    source = unpainted(ONE_VOLUME, tmp_path)
    out = convert_to_u1(str(source), out_dir=tempfile.mkdtemp()).output_path
    with zipfile.ZipFile(out) as z:
        assert OBJECTS not in z.namelist()
    assert MP.validate_archive(ThreeMF.open(out))["multipart"] is False


def test_painting_alone_earns_the_target_layout():
    """One volume, no roles, nothing to split — and it still moves.

    Measured against Snapmaker Orca 2.3.5: the identical painting in the root
    model opens with nothing painted, and behind a component in its own object
    file opens complete. So a painted object crosses in the shape Orca reads.
    """
    out = convert_to_u1(str(ONE_VOLUME), out_dir=tempfile.mkdtemp()).output_path
    with zipfile.ZipFile(out) as z:
        assert OBJECTS in z.namelist()
        assert z.read(ROOT).decode("utf-8").count("<mesh>") == 0
        assert z.read(OBJECTS).decode("utf-8").count('paint_color="') == 8


# --- twelve ways to lie about it ---------------------------------------------

def problems(path: str) -> list[str]:
    return MP.validate_archive(ThreeMF.open(path))["problems"]


def test_1_a_dropped_part_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, SETTINGS,
                     lambda t: re.sub(r'<part id="2".*?</part>', "", t, flags=re.S))
    assert any("part" in p for p in problems(broken))


def test_2_a_duplicated_part_record_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, SETTINGS, lambda t: t.replace(
        '<part id="2"', '<part id="1"', 1))
    assert any("twice" in p or "do not match" in p for p in problems(broken))


def test_3_swapped_part_filaments_are_caught_by_the_audit(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, SETTINGS,
                     lambda t: t.replace('value="2"', "@A@").replace('value="5"', 'value="2"')
                                .replace("@A@", 'value="5"'))
    after = A.read(ThreeMF.open(broken))
    assert [v["slot"] for v in after["objects"][0]["volumes"]] == [5, 2]


def test_4_collapsing_both_slots_onto_the_object_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, SETTINGS, lambda t: re.sub(
        r'\s*<metadata key="extruder" value="[25]"/>', "", t))
    result = A.compare(A.read(ThreeMF.open(str(TWO_VOLUMES))), A.read(ThreeMF.open(broken)))
    rows = [r for r in result["semantics"] if r["kind"] == "volume_filament"]
    assert rows and rows[0]["status"] != A.PRESERVED_EXACT


def test_5_a_broken_part_matrix_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, SETTINGS,
                     lambda t: t.replace('key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"',
                                         'key="matrix" value="1 0 0"', 1))
    assert any("matrix" in p for p in problems(broken))


def test_5b_a_non_numeric_matrix_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, SETTINGS,
                     lambda t: t.replace('value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"',
                                         'value="a b c d e f g h i j k l m n o p"', 1))
    assert any("matrix" in p for p in problems(broken))


def test_6_swapped_part_geometry_changes_the_digests(prepared, tmp_path):
    """Geometry is compared by what it is, so swapping the meshes is visible."""
    body = read(prepared, OBJECTS)
    first = re.search(r'<object id="1".*?</object>', body, re.S).group(0)
    second = re.search(r'<object id="2".*?</object>', body, re.S).group(0)
    swapped = body.replace(first, "@1@").replace(second, first.replace('id="1"', 'id="2"'))
    swapped = swapped.replace("@1@", second.replace('id="2"', 'id="1"'))
    broken = damaged(prepared, tmp_path, OBJECTS, lambda _t: swapped)
    original = MP.geometry_digest(*MP.read_mesh(first))
    now = re.search(r'<object id="1".*?</object>', read(broken, OBJECTS), re.S).group(0)
    assert MP.geometry_digest(*MP.read_mesh(now)) != original


def test_7_a_component_pointing_at_a_missing_mesh_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, ROOT,
                     lambda t: t.replace('objectid="2"', 'objectid="9"', 1))
    assert any("no file defines" in p for p in problems(broken))


def test_8_metadata_claiming_more_parts_than_geometry_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, ROOT, lambda t: re.sub(
        r'<component[^>]*objectid="2"[^>]*/>', "", t))
    found = problems(broken)
    assert any("part" in p for p in found)


def test_9_geometry_with_no_part_record_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, SETTINGS,
                     lambda t: re.sub(r'<part id="2".*?</part>', "", t, flags=re.S))
    assert any("1 part" in p or "do not match" in p for p in problems(broken))


def test_10_an_object_file_that_is_not_declared_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, "3D/_rels/3dmodel.model.rels",
                     lambda t: t.replace("/3D/Objects/object_1.model", "/3D/Objects/other.model"))
    assert any("relationships" in p for p in problems(broken))


def test_11_a_build_item_placing_the_wrong_object_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, ROOT, lambda t: re.sub(
        r'(<item[^>]*objectid=")\d+', r"\g<1>7", t))
    assert any("build places" in p for p in problems(broken))


def test_12_a_part_record_with_no_geometry_is_caught(prepared, tmp_path):
    broken = damaged(prepared, tmp_path, OBJECTS, lambda t: re.sub(
        r'(<object id="2"[^>]*>).*?(</object>)', r"\1<mesh></mesh>\2", t, flags=re.S))
    assert any("carries no geometry" in p for p in problems(broken))


# --- roles: carry what is proven, refuse the rest ----------------------------

def unknown_role_source(tmp_path: Path) -> Path:
    """The modifier fixture with a role word no slicer defines.

    PrusaSlicer promotes a word it does not recognise to `ModelPart`, turning a
    modifier into solid plastic. Studio meets the same word here and must not.
    """
    target = tmp_path / "unknown_role.3mf"
    with zipfile.ZipFile(FIXTURES / "vt_ParameterModifier_out.3mf") as src, \
            zipfile.ZipFile(target, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "Metadata/Slic3r_PE_model.config":
                data = data.decode("utf-8").replace(
                    'value="ParameterModifier"', 'value="SomeRoleNobodyDefined"'
                ).encode("utf-8")
            dst.writestr(item, data)
    return target


def test_an_unknown_role_is_never_written_as_a_part(tmp_path):
    """No proven target meaning, so no split — and never a normal_part.

    Writing an unrecognised role as `normal_part` is how a modifier becomes solid
    plastic with the file claiming everything is fine. Studio declines instead:
    the object crosses whole and the audit says what that means.
    """
    source = unknown_role_source(tmp_path)
    out = convert_to_u1(str(source), out_dir=tempfile.mkdtemp()).output_path
    with zipfile.ZipFile(out) as z:
        assert OBJECTS not in z.namelist()
        settings = z.read(SETTINGS).decode("utf-8")
    assert re.findall(r'<part id="\d+" subtype="([^"]+)"', settings) == ["normal_part"]

    result = A.compare(A.read(ThreeMF.open(str(source))), A.read(ThreeMF.open(out)))
    rows = [r for r in result["semantics"] if r["kind"] == "volume_role"]
    assert rows and rows[0]["status"] == A.UNSUPPORTED


def test_the_unknown_role_warning_says_what_actually_happens(tmp_path):
    """Its geometry does cross, and it will print. Measured, not assumed."""
    source = unknown_role_source(tmp_path)
    out = convert_to_u1(str(source), out_dir=tempfile.mkdtemp()).output_path
    before = read(str(source), ROOT).count("<triangle ")
    after = read(out, ROOT).count("<triangle ")
    assert before == after == 12, "the volume's facets cross with the object"

    result = A.compare(A.read(ThreeMF.open(str(source))), A.read(ThreeMF.open(out)))
    detail = [r for r in result["semantics"] if r["kind"] == "volume_role"][0]["detail"]
    assert "will treat it as solid and print it" in detail


# --- painting -----------------------------------------------------------------

def test_painting_survives_the_split_facet_for_facet(prepared):
    """The values cross unchanged; only the attribute's name is the target's."""
    before = sorted(re.findall(r'mmu_segmentation="([^"]*)"', read(str(TWO_VOLUMES), ROOT)))
    after = sorted(re.findall(r'paint_color="([^"]*)"', read(prepared, OBJECTS)))
    assert before == after and len(after) == 8
    assert "mmu_segmentation" not in read(prepared, OBJECTS), (
        "the source's attribute name means nothing to Snapmaker Orca")


def test_each_part_keeps_the_painting_of_its_own_facets(prepared):
    body = read(prepared, OBJECTS)
    counts = []
    for object_id in ("1", "2"):
        block = re.search(rf'<object id="{object_id}".*?</object>', body, re.S).group(0)
        counts.append(block.count("paint_color"))
    assert sum(counts) == 8 and all(counts), "painting must not pile onto one part"
