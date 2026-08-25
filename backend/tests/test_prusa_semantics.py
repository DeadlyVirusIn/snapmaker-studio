"""What PrusaSlicer actually means, proved by making PrusaSlicer write the file.

Every fixture these tests read was authored by PrusaSlicer 2.9.6. A candidate
model config went into a genuine PrusaSlicer project, the project went back to
`prusa-slicer-console.exe --export-3mf`, and whatever the slicer wrote is what is
stored. One variable per file. That is the difference between knowing the format
and guessing from tag names, and it overturned two things Studio believed:

* **An absent extruder and an explicit `extruder="1"` are different facts.**
  PrusaSlicer round-trips each faithfully and separately — it does not normalise
  the absence into a 1, and it does not drop an explicit 1 as redundant. Studio
  used to write slot 1 for an unassigned object and the fidelity audit called that
  *preserved*.
* **One object with volumes on different filaments is ordinary and fully
  representable.** Two volumes on filaments 2 and 5 came back exactly as written.

Snapmaker Orca's side of the crossing is evidenced the same way, from a project
Snapmaker Orca 2.3.5 wrote itself: an object nobody assigned carries
`extruder="0"`, and parts carry `subtype="normal_part"`.

See `fixtures/prusa-semantics/MANIFEST.json` for the hash and the note on each.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from snapstudio_core import assignments as A
from snapstudio_core.container import ThreeMF

FIXTURES = Path(__file__).parent / "fixtures" / "prusa-semantics"
ORCA_AUTHORED = (Path(__file__).parent / "fixtures" / "painted"
                 / "snapmaker-orca-2.3.5-authored.3mf")


def read(name: str) -> dict:
    return A.read(ThreeMF.open(str(FIXTURES / name)))


def only_object(name: str) -> dict:
    objects = read(name)["objects"]
    assert len(objects) == 1, f"{name} should hold one object"
    return objects[0]


# --- the fixtures say what they are -----------------------------------------

def test_the_fixtures_record_that_the_slicer_authored_them():
    manifest = json.loads((FIXTURES / "MANIFEST.json").read_text("utf-8"))
    assert manifest["_provenance"]["kind"] == "authored_by_the_slicer"
    assert "2.9.6" in manifest["_provenance"]["slicer"]
    assert len(manifest["files"]) >= 10


def test_every_fixture_still_hashes_to_what_was_captured():
    import hashlib

    manifest = json.loads((FIXTURES / "MANIFEST.json").read_text("utf-8"))
    for name, meta in manifest["files"].items():
        if "sha256" not in meta:
            continue
        data = (FIXTURES / name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == meta["sha256"], name


# --- default is not slot one -------------------------------------------------

def test_prusaslicer_writes_no_extruder_when_nobody_assigned_one():
    entry = only_object("A_no_assignment_out.3mf")
    assert entry["slot"] is None
    assert entry["source"] == A.DEFAULT


def test_prusaslicer_keeps_an_explicit_slot_one_explicit():
    """The whole reason the two states cannot be flattened."""
    entry = only_object("B_object_slot1_out.3mf")
    assert entry["slot"] == 1
    assert entry["source"] == A.EXPLICIT


def test_snapmaker_orca_writes_zero_for_an_object_nobody_assigned():
    """The target dialect's own word for the same absence."""
    entry = A.read(ThreeMF.open(str(ORCA_AUTHORED)))["objects"][0]
    assert entry["slot"] is None
    assert entry["source"] == A.DEFAULT


@pytest.mark.parametrize("name, slot", [
    ("C_object_slot3_out.3mf", 3),
    ("M_object_slot6_out.3mf", 6),
])
def test_an_explicit_slot_survives_the_slicer_unchanged(name, slot):
    entry = only_object(name)
    assert entry["slot"] == slot and entry["source"] == A.EXPLICIT


def test_a_slot_beyond_the_filament_count_is_not_clamped_by_the_slicer():
    """PrusaSlicer keeps slot 6 on a machine with fewer filaments, so Studio must."""
    assert only_object("M_object_slot6_out.3mf")["slot"] == 6


# --- structure the reader used to be blind to --------------------------------

def test_instances_are_counted_from_the_build_items():
    """Three build items came back as instances_count=3.

    The count in the model config mirrors the build section rather than owning it:
    setting it to 3 while leaving one build item produced a 1 back from the
    slicer, so the build items are the fact.
    """
    assert only_object("inst3_out.3mf")["instances"] == 3
    assert only_object("A_no_assignment_out.3mf")["instances"] == 1


def test_one_object_may_hold_volumes_on_different_filaments():
    entry = only_object("H_two_volumes_different_slots_out.3mf")
    assert [v["slot"] for v in entry["volumes"]] == [2, 5]
    assert entry["volume_slots"] == [2, 5]
    # No object-level slot: the object itself never claimed one.
    assert entry["slot"] is None


def test_a_volume_role_is_read_rather_than_assumed_to_be_geometry():
    entry = only_object("vt_ParameterModifier_out.3mf")
    assert [v["role"] for v in entry["volumes"]] == [A.PART, A.MODIFIER]


def test_an_unrecognised_role_word_is_unknown_not_quietly_a_part():
    """PrusaSlicer turns a role it does not know into printable geometry.

    Handed `volume_type="ModifierMesh"` — the old Slic3r spelling — 2.9.6 wrote
    back `ModelPart`. A modifier became a solid part, silently. Studio must not
    repeat that: an unknown word is unknown.
    """
    assert A.role_of("ModifierMesh") == A.ROLE_UNKNOWN
    assert A.role_of("SomethingPrusaAddsIn2027") == A.ROLE_UNKNOWN
    # And the file the slicer produced is what it is: two plain parts.
    entry = only_object("vt_ModifierMesh_out.3mf")
    assert [v["role"] for v in entry["volumes"]] == [A.PART, A.PART]


def test_object_and_volume_assignments_coexist_independently():
    entry = only_object("N_object_and_volume_disagree_out.3mf")
    assert entry["slot"] == 2 and entry["source"] == A.EXPLICIT
    assert entry["volume_slots"] == [4]


def test_per_object_overrides_are_read_as_facts():
    entry = only_object("J_per_object_override_out.3mf")
    assert set(entry["overrides"]) == {"layer_height", "fill_density", "support_material"}
    assert entry["overrides"]["layer_height"] == "0.3"
    # And an object with none has none, rather than an invented empty setting.
    assert only_object("A_no_assignment_out.3mf")["overrides"] == {}


def test_the_readers_agree_on_shape_across_dialects():
    """Both dialects produce the same keys, so nothing downstream branches."""
    prusa = only_object("C_object_slot3_out.3mf")
    orca = A.read(ThreeMF.open(str(ORCA_AUTHORED)))["objects"][0]
    assert set(prusa) == set(orca)
    for entry in (prusa, orca):
        assert isinstance(entry["volumes"], list)
        assert isinstance(entry["overrides"], dict)
