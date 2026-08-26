"""Break the crossing on purpose, and check the audit notices.

A fidelity audit that only ever runs against correct output proves nothing. Each
test here takes a real assignment reading and damages exactly one thing in the
"prepared" side, then asserts the comparison names that damage — not a general
unease, and not a broad "objects preserved" row with the change hidden underneath
it.

The damages are the ones that would actually happen: a default becoming a stated
slot, a slot quietly renumbered to fit four toolheads, two objects' assignments
swapped, a part's filament lost, a modifier turned into printable geometry, a
copy vanishing. Every one of them leaves the geometry intact and the file
openable, which is exactly why they need a test rather than an eye.
"""
from __future__ import annotations

import copy

import pytest

from snapstudio_core import assignments as A


def obj(index=0, name="cube", slot=None, source=A.DEFAULT, volumes=None,
        instances=1, overrides=None) -> dict:
    volumes = volumes if volumes is not None else [
        {"index": 0, "name": name, "slot": slot, "role": A.PART, "role_word": "ModelPart"}]
    return {"object_id": str(index + 1), "index": index, "name": name, "slot": slot,
            "source": source, "volume_slots": [v["slot"] for v in volumes],
            "volumes": volumes, "instances": instances,
            "overrides": dict(overrides or {})}


def side(*objects) -> dict:
    return {"available": True, "dialect": A.DIALECT_PRUSA, "objects": list(objects)}


def statuses(result, kind=None):
    if kind is None:
        return [row["status"] for row in result["rows"]]
    return [row["status"] for row in result["semantics"] if row["kind"] == kind]


# --- 1. default becomes a stated slot ---------------------------------------

def test_a_default_turned_into_slot_one_is_detected():
    before = side(obj(slot=None, source=A.DEFAULT))
    after = side(obj(slot=1, source=A.EXPLICIT))
    result = A.compare(before, after)
    assert statuses(result) == [A.CHANGED]
    assert "never made" in result["rows"][0]["detail"]


def test_a_default_kept_as_a_default_is_preserved():
    before = side(obj(slot=None, source=A.DEFAULT))
    after = side(obj(slot=None, source=A.DEFAULT))
    assert statuses(A.compare(before, after)) == [A.PRESERVED]


def test_an_explicit_slot_one_turned_into_a_default_is_detected():
    before = side(obj(slot=1, source=A.EXPLICIT))
    after = side(obj(slot=None, source=A.DEFAULT))
    assert statuses(A.compare(before, after)) == [A.LOST]


# --- 2. a slot quietly renumbered -------------------------------------------

def test_slot_three_becoming_slot_two_is_detected():
    before = side(obj(slot=3, source=A.EXPLICIT))
    after = side(obj(slot=2, source=A.EXPLICIT))
    result = A.compare(before, after)
    assert statuses(result) == [A.CHANGED]
    assert "3" in result["rows"][0]["detail"] and "2" in result["rows"][0]["detail"]


def test_a_slot_beyond_four_collapsed_into_range_is_detected():
    """The renumbering Studio must never do, and must always notice."""
    before = side(obj(slot=6, source=A.EXPLICIT))
    after = side(obj(slot=4, source=A.EXPLICIT))
    assert statuses(A.compare(before, after)) == [A.CHANGED]


# --- 3. assignments swapped between objects ---------------------------------

def test_two_objects_with_their_assignments_swapped_are_both_detected():
    before = side(obj(0, "left", slot=2, source=A.EXPLICIT),
                  obj(1, "right", slot=3, source=A.EXPLICIT))
    after = side(obj(0, "left", slot=3, source=A.EXPLICIT),
                 obj(1, "right", slot=2, source=A.EXPLICIT))
    assert statuses(A.compare(before, after)) == [A.CHANGED, A.CHANGED]


# --- 4. one part's filament changed or lost ---------------------------------

def volumes(*slots, role=A.PART):
    return [{"index": i, "name": f"part{i}", "slot": s, "role": role,
             "role_word": "ModelPart"} for i, s in enumerate(slots)]


def test_a_changed_volume_filament_is_detected():
    before = side(obj(volumes=volumes(2, 5)))
    after = side(obj(volumes=volumes(2, 4)))
    assert statuses(A.compare(before, after), "volume_filament") == [A.CHANGED]


def test_volumes_flattened_to_one_part_are_reported_as_unsupported():
    """The real crossing: two parts on different filaments, one part written."""
    before = side(obj(volumes=volumes(2, 5)))
    after = side(obj(volumes=volumes(2)))
    rows = [r for r in A.compare(before, after)["semantics"]
            if r["kind"] == "volume_filament"]
    assert rows and rows[0]["status"] == A.UNSUPPORTED
    # The user is told both filaments, not just the survivor.
    assert "filament 2" in rows[0]["detail"] and "filament 5" in rows[0]["detail"]
    assert "does not choose one for you" in rows[0]["detail"]


def test_matching_volume_filaments_are_preserved_exactly():
    before = side(obj(volumes=volumes(2, 5)))
    after = side(obj(volumes=volumes(2, 5)))
    assert statuses(A.compare(before, after), "volume_filament") == [A.PRESERVED_EXACT]


# --- 5. a modifier turned into printable geometry ---------------------------

def test_a_modifier_becoming_a_normal_part_is_detected():
    """The worst quiet failure: a modifier prints as solid plastic."""
    before = side(obj(volumes=[
        {"index": 0, "name": "body", "slot": None, "role": A.PART, "role_word": "ModelPart"},
        {"index": 1, "name": "mod", "slot": None, "role": A.MODIFIER,
         "role_word": "ParameterModifier"}]))
    after = side(obj(volumes=volumes(None, None)))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "volume_role"]
    assert rows and rows[0]["status"] == A.UNSUPPORTED
    assert "modifier" in rows[0]["detail"]
    # And the warning has to say what actually happens. The modifier's shape is
    # still in the object — measured, not assumed — so it prints as solid unless
    # the user removes it. An earlier version of this row claimed the opposite.
    assert "will treat it as solid and print it" in rows[0]["detail"]


def test_a_carried_modifier_is_preserved():
    modifier = [{"index": 0, "name": "body", "slot": None, "role": A.PART,
                 "role_word": "ModelPart"},
                {"index": 1, "name": "mod", "slot": None, "role": A.MODIFIER,
                 "role_word": "ParameterModifier"}]
    result = A.compare(side(obj(volumes=modifier)), side(obj(volumes=copy.deepcopy(modifier))))
    assert statuses(result, "volume_role") == [A.PRESERVED_EXACT]


@pytest.mark.parametrize("role", [A.NEGATIVE, A.SUPPORT_ENFORCER, A.SUPPORT_BLOCKER])
def test_every_special_role_is_watched_not_just_modifiers(role):
    before = side(obj(volumes=[
        {"index": 0, "name": "body", "slot": None, "role": A.PART, "role_word": "ModelPart"},
        {"index": 1, "name": "x", "slot": None, "role": role, "role_word": role}]))
    after = side(obj(volumes=volumes(None, None)))
    assert statuses(A.compare(before, after), "volume_role") == [A.UNSUPPORTED]


# --- 6 & 7. instances lost or multiplied ------------------------------------

def test_a_lost_instance_is_detected():
    before = side(obj(instances=3))
    after = side(obj(instances=2))
    assert statuses(A.compare(before, after), "instances") == [A.CHANGED]


def test_a_duplicated_instance_is_detected():
    before = side(obj(instances=2))
    after = side(obj(instances=4))
    assert statuses(A.compare(before, after), "instances") == [A.CHANGED]


def test_instances_flattened_into_separate_objects_are_preserved_semantically():
    """Every copy is still on the plate; only the relationship is gone."""
    before = side(obj(instances=3))
    after = side(obj(0, "cube_1", instances=1), obj(1, "cube_2", instances=1),
                 obj(2, "cube_3", instances=1))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "instances"]
    assert rows and rows[0]["status"] == A.PRESERVED_SEMANTIC
    assert "all on the plate" in rows[0]["detail"]


def test_an_uncountable_instance_side_is_unverified_not_a_detected_change():
    """Not knowing is not the same as knowing something broke."""
    before = side(obj(instances=3))
    after = side(obj(instances=None))
    assert statuses(A.compare(before, after), "instances") == [A.UNVERIFIED]


# --- 8 & 9. overrides dropped, moved, invented or mistranslated -------------
#
# Two of the three settings Studio carries are spelled differently on each side —
# PrusaSlicer's `fill_density` is Snapmaker Orca's `sparse_infill_density`, and
# `support_material` is `enable_support`. So the copy carrying the source's own
# word is not the copy carrying the setting: Orca discards `fill_density` exactly
# as it discards a key invented for the experiment. Every case below is written
# in the two vocabularies rather than one.

def test_a_dropped_per_object_override_is_named():
    """A setting Studio can carry, and the copy has not. That is a fault."""
    before = side(obj(overrides={"layer_height": "0.3"}))
    after = side(obj(overrides={}))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "override"]
    assert rows and rows[0]["status"] == A.CHANGED
    assert "layer_height" in rows[0]["detail"]


def test_a_setting_studio_cannot_carry_is_unsupported_not_changed():
    """Not carrying what was never carryable is a limit, not a bug."""
    before = side(obj(overrides={"brim_width": "5"}))
    after = side(obj(overrides={}))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "override"]
    assert rows and rows[0]["status"] == A.UNSUPPORTED
    assert "brim_width" in rows[0]["detail"]


def test_an_override_silently_given_a_different_value_is_detected():
    before = side(obj(overrides={"fill_density": "15%"}))
    after = side(obj(overrides={"sparse_infill_density": "40%"}))
    assert A.CHANGED in statuses(A.compare(before, after), "override")


def test_a_carried_override_is_preserved_in_the_targets_own_word():
    before = side(obj(overrides={"fill_density": "15%"}))
    after = side(obj(overrides={"sparse_infill_density": "15%"}))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "override"]
    assert [r["status"] for r in rows] == [A.PRESERVED_SEMANTIC]
    assert "sparse_infill_density" in rows[0]["detail"]


def test_an_override_carried_in_the_sources_own_word_is_not_preserved():
    """`fill_density` in an Orca project is discarded like a nonsense key."""
    before = side(obj(overrides={"fill_density": "15%"}))
    after = side(obj(overrides={"fill_density": "15%"}))
    assert A.CHANGED in statuses(A.compare(before, after), "override")


def test_a_carried_override_keeps_exact_when_both_sides_use_the_word():
    before = side(obj(overrides={"layer_height": "0.3"}))
    after = side(obj(overrides={"layer_height": "0.3"}))
    assert statuses(A.compare(before, after), "override") == [A.PRESERVED_EXACT]


def test_an_override_the_copy_invented_is_detected():
    """A prepared copy stating a setting nobody chose changes what prints."""
    before = side(obj(overrides={}))
    after = side(obj(overrides={"enable_support": "1"}))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "override"]
    assert [r["status"] for r in rows] == [A.CHANGED]
    assert "source never did" in rows[0]["detail"]


def test_an_override_copied_onto_another_object_is_detected():
    before = side(obj(index=0, name="a", overrides={"layer_height": "0.3"}),
                  obj(index=1, name="b"))
    after = side(obj(index=0, name="a", overrides={"layer_height": "0.3"}),
                 obj(index=1, name="b", overrides={"layer_height": "0.3"}))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "override"]
    assert [(r["object"], r["status"]) for r in rows] == [
        ("a", A.PRESERVED_EXACT), ("b", A.CHANGED)]


def test_an_override_moved_to_the_wrong_object_is_detected():
    before = side(obj(index=0, name="a", overrides={"layer_height": "0.3"}),
                  obj(index=1, name="b"))
    after = side(obj(index=0, name="a"),
                 obj(index=1, name="b", overrides={"layer_height": "0.3"}))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "override"]
    assert [(r["object"], r["status"]) for r in rows] == [
        ("a", A.CHANGED), ("b", A.CHANGED)]


def test_an_inherited_setting_turned_explicit_is_detected():
    """The source left it to the process profile; the copy states a number."""
    before = side(obj(overrides={}))
    after = side(obj(overrides={"layer_height": "0.2"}))
    assert statuses(A.compare(before, after), "override") == [A.CHANGED]


def test_a_malformed_source_value_is_not_carried_and_says_why():
    """Orca deletes the object when it cannot read a per-object value."""
    before = side(obj(overrides={"layer_height": "not-a-number"}))
    after = side(obj(overrides={}))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "override"]
    assert [r["status"] for r in rows] == [A.UNSUPPORTED]
    assert "not a plain number" in rows[0]["detail"]


def test_carrying_a_malformed_value_anyway_is_a_fault_not_a_bonus():
    before = side(obj(overrides={"layer_height": "0"}))
    after = side(obj(overrides={"layer_height": "0"}))
    rows = [r for r in A.compare(before, after)["semantics"] if r["kind"] == "override"]
    assert [r["status"] for r in rows] == [A.CHANGED]
    assert "was not carried" in rows[0]["detail"]


# --- 11. painting kept while the assignment underneath is lost --------------

def test_an_assignment_lost_under_intact_geometry_is_still_reported():
    """Everything else about the object survives; the audit still says so."""
    before = side(obj(name="painted", slot=3, source=A.EXPLICIT, volumes=volumes(3)))
    after = side(obj(name="painted", slot=None, source=A.DEFAULT, volumes=volumes(None)))
    result = A.compare(before, after)
    assert statuses(result) == [A.LOST]
    assert result["rows"][0]["object"] == "painted"


# --- the audit must not cry wolf --------------------------------------------

def test_an_untouched_project_produces_no_semantic_complaints():
    before = side(obj(slot=3, source=A.EXPLICIT, volumes=volumes(3), instances=2,
                      overrides={"layer_height": "0.3"}))
    after = copy.deepcopy(before)
    result = A.compare(before, after)
    assert statuses(result) == [A.PRESERVED]
    assert all(row["status"] == A.PRESERVED_EXACT for row in result["semantics"])


def test_an_object_with_nothing_special_produces_no_rows_at_all():
    before = side(obj())
    after = side(obj())
    assert A.compare(before, after)["semantics"] == []
