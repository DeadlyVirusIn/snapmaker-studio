"""Feeding the assignment reader things no slicer would write.

The reader now carries four facts instead of one — the slot, the volumes and
their roles, the instance count and the per-object overrides — and every one of
them comes out of somebody else's file. A 3MF is an untrusted archive: it can be
truncated, hand-edited, written by a slicer that does not exist yet, or produced
by a tool with a bug.

The bar throughout is the same one the rest of Studio holds to. Unknown stays
unknown. Nothing crashes. Nothing is silently normalised into a confident answer,
because a confident wrong answer about which filament an object prints in is worse
than no answer at all.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from snapstudio_core import assignments as A
from snapstudio_core.container import ThreeMF

FIXTURE = (Path(__file__).parent / "fixtures" / "prusa-semantics"
           / "C_object_slot3_out.3mf")
CONFIG = "Metadata/Slic3r_PE_model.config"
MODEL = "3D/3dmodel.model"


def project(tmp_path: Path, config: str | None = None, model: str | None = None) -> str:
    """The genuine fixture with one part replaced by whatever is handed in."""
    out = tmp_path / "attack.3mf"
    with zipfile.ZipFile(FIXTURE) as src, zipfile.ZipFile(out, "w") as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == CONFIG and config is not None:
                data = config.encode("utf-8")
            if item.filename == MODEL and model is not None:
                data = model.encode("utf-8")
            dst.writestr(item.filename, data)
    return str(out)


def read(tmp_path, config=None, model=None) -> dict:
    return A.read(ThreeMF.open(project(tmp_path, config, model)))


def one(tmp_path, config=None, model=None) -> dict:
    objects = read(tmp_path, config, model)["objects"]
    return objects[0] if objects else {}


# --- the file itself is wrong ------------------------------------------------

@pytest.mark.parametrize("config", [
    "",
    "   ",
    "<config>",                                   # never closed
    "<config><object id=",                        # cut mid-attribute
    "not xml at all",
    "<config>" + "<object id='1'>" * 200 + "</config>",   # deeply repeated
    '<?xml version="1.0"?><config/>',
])
def test_a_broken_config_is_not_a_crash(tmp_path, config):
    result = read(tmp_path, config=config)
    assert isinstance(result, dict)
    assert isinstance(result.get("objects"), list)


def test_a_config_with_windows_line_endings_reads_the_same(tmp_path):
    with zipfile.ZipFile(FIXTURE) as z:
        text = z.read(CONFIG).decode("utf-8")
    assert one(tmp_path, config=text.replace("\n", "\r\n"))["slot"] == 3


def test_a_missing_model_config_is_reported_not_guessed(tmp_path):
    out = tmp_path / "bare.3mf"
    with zipfile.ZipFile(FIXTURE) as src, zipfile.ZipFile(out, "w") as dst:
        for item in src.infolist():
            if item.filename in (CONFIG, "Metadata/model_settings.config"):
                continue
            dst.writestr(item.filename, src.read(item.filename))
    result = A.read(ThreeMF.open(str(out)))
    assert result["available"] is False
    assert "records no per-object filament assignment" in result["reason"]


# --- the numbers are wrong ---------------------------------------------------

@pytest.mark.parametrize("value", ["0", "-1", "-3", "abc", "", "1.5", "1e3", " ",
                                   "999999999999999999999", "٣", "0x3", "+3"])
def test_an_extruder_that_is_not_a_slot_number_leaves_the_object_default(tmp_path, value):
    """Zero included: Snapmaker Orca uses it to mean nobody assigned this."""
    config = ('<config><object id="1" instances_count="1">'
              f'<metadata type="object" key="extruder" value="{value}"/>'
              '</object></config>')
    entry = one(tmp_path, config=config)
    assert entry["slot"] is None
    assert entry["source"] == A.DEFAULT


def test_a_slot_far_beyond_any_filament_list_is_still_carried(tmp_path):
    """Studio does not decide a project has too many colours."""
    config = ('<config><object id="1" instances_count="1">'
              '<metadata type="object" key="extruder" value="64"/>'
              '</object></config>')
    assert one(tmp_path, config=config)["slot"] == 64


@pytest.mark.parametrize("value", ["-2", "abc", "", "0"])
def test_a_nonsense_instance_count_does_not_become_a_number(tmp_path, value):
    config = (f'<config><object id="1" instances_count="{value}">'
              '<metadata type="object" key="name" value="x"/></object></config>')
    entry = one(tmp_path, config=config)
    # The build items are authoritative anyway, and this fixture has one.
    assert entry["instances"] in (None, 1)


# --- the structure is wrong --------------------------------------------------

def test_duplicate_object_ids_do_not_merge_into_one(tmp_path):
    config = ('<config>'
              '<object id="1" instances_count="1">'
              '<metadata type="object" key="extruder" value="2"/></object>'
              '<object id="1" instances_count="1">'
              '<metadata type="object" key="extruder" value="5"/></object>'
              '</config>')
    objects = read(tmp_path, config=config)["objects"]
    assert [o["slot"] for o in objects] == [2, 5]


def test_an_object_with_no_id_still_gets_a_position(tmp_path):
    config = ('<config><object instances_count="1">'
              '<metadata type="object" key="extruder" value="4"/></object></config>')
    entry = one(tmp_path, config=config)
    assert entry["slot"] == 4 and entry["index"] == 0


def test_an_object_with_no_volumes_reports_none_rather_than_inventing_one(tmp_path):
    config = ('<config><object id="1" instances_count="1">'
              '<metadata type="object" key="extruder" value="2"/></object></config>')
    entry = one(tmp_path, config=config)
    assert entry["volumes"] == [] and entry["volume_slots"] == []


def test_reordered_objects_are_compared_by_position_and_the_change_shows(tmp_path):
    """Position is what the crossing preserves; swapping is a real difference."""
    before = {"available": True, "dialect": A.DIALECT_PRUSA, "objects": [
        {"object_id": "1", "index": 0, "name": "a", "slot": 2, "source": A.EXPLICIT,
         "volume_slots": [], "volumes": [], "instances": 1, "overrides": {}},
        {"object_id": "2", "index": 1, "name": "b", "slot": 5, "source": A.EXPLICIT,
         "volume_slots": [], "volumes": [], "instances": 1, "overrides": {}}]}
    after = {"available": True, "dialect": A.DIALECT_BAMBU,
             "objects": list(reversed(before["objects"]))}
    assert [r["status"] for r in A.compare(before, after)["rows"]] == [A.CHANGED, A.CHANGED]


def test_a_build_that_disagrees_with_the_file_does_not_multiply_the_objects(tmp_path):
    """Five hundred placements against a project that states one.

    The slicer maintains `instances_count` against the build it actually has, so
    that statement is the one to believe; a build section saying something else is
    a damaged file, not five hundred copies. Either way the object count must not
    move, because that is what everything downstream iterates.
    """
    item = '<item objectid="1" transform="1 0 0 0 1 0 0 0 1 0 0 0" printable="1"/>'
    with zipfile.ZipFile(FIXTURE) as z:
        model = z.read(MODEL).decode("utf-8")
    head, _sep, _tail = model.partition("<build>")
    many = head + "<build>" + (item * 500) + "</build></model>"
    result = read(tmp_path, model=many)
    assert len(result["objects"]) == 1
    assert result["objects"][0]["instances"] == 1


# --- roles and overrides -----------------------------------------------------

@pytest.mark.parametrize("word", ["", "   ", "ModifierMesh", "PARAMETERMODIFIER",
                                  "SomethingPrusaAddsIn2030", "<script>", "0"])
def test_a_role_word_studio_does_not_know_is_unknown(word):
    expected = A.MODIFIER if word.strip().lower() == "parametermodifier" else A.ROLE_UNKNOWN
    assert A.role_of(word) == expected


def test_a_role_word_is_never_upgraded_to_a_printable_part():
    """PrusaSlicer does exactly this. Studio must not."""
    for word in ("ModifierMesh", "Modifier", "unknown_future_role", None):
        assert A.role_of(word) != A.PART


def test_identity_keys_are_not_mistaken_for_overrides(tmp_path):
    config = ('<config><object id="1" instances_count="1">'
              '<metadata type="object" key="name" value="cube"/>'
              '<metadata type="object" key="extruder" value="3"/>'
              '<metadata type="object" key="source_file" value="cube.stl"/>'
              '<metadata type="object" key="layer_height" value="0.3"/>'
              '</object></config>')
    assert set(one(tmp_path, config=config)["overrides"]) == {"layer_height"}


def test_an_override_with_an_empty_value_is_still_recorded(tmp_path):
    """Somebody cleared a setting on this object. That is a fact, not an absence."""
    config = ('<config><object id="1" instances_count="1">'
              '<metadata type="object" key="fill_density" value=""/></object></config>')
    assert one(tmp_path, config=config)["overrides"] == {"fill_density": ""}


# --- comparison against nothing ---------------------------------------------

@pytest.mark.parametrize("side", [
    {"available": False, "objects": []},
    {"available": True, "objects": []},
])
def test_comparing_against_an_empty_side_never_raises(side):
    good = {"available": True, "dialect": A.DIALECT_PRUSA, "objects": [
        {"object_id": "1", "index": 0, "name": "a", "slot": 3, "source": A.EXPLICIT,
         "volume_slots": [], "volumes": [], "instances": 1, "overrides": {}}]}
    for before, after in ((good, side), (side, good)):
        result = A.compare(before, after)
        assert isinstance(result, dict)
        assert isinstance(result.get("rows", []), list)


def test_objects_only_in_the_prepared_copy_are_unknown_not_invented(tmp_path):
    before = {"available": True, "dialect": A.DIALECT_PRUSA, "objects": []}
    after = {"available": True, "dialect": A.DIALECT_BAMBU, "objects": [
        {"object_id": "1", "index": 0, "name": "ghost", "slot": 2, "source": A.EXPLICIT,
         "volume_slots": [], "volumes": [], "instances": 1, "overrides": {}}]}
    rows = A.compare(before, after)["rows"]
    assert rows and rows[0]["status"] == A.UNKNOWN
