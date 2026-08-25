"""The paint encoding, decoded — including the files that are trying to break it.

Two kinds of test live here. The first kind proves the format is understood:
encode a known intent, decode it, and get the intent back, with the geometry
tiling the original triangle exactly. The second kind is adversarial, because
this decoder runs on files a user downloaded from the internet: every malformed,
truncated, over-deep or over-wide attribute must produce a refusal, not a crash
and not an allocation.

The genuine cross-check — that real slicers write exactly these strings — is in
test_painted_real_slicers.py, which needs a real slicer present.
"""
from __future__ import annotations

import pytest

from snapstudio_core import paint_codec as codec

TRIANGLE = ((0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (0.0, 10.0, 0.0))


def states(attribute):
    leaves, _ = codec.decode(attribute)
    return sorted({leaf.state for leaf in leaves})


# --- the format itself -------------------------------------------------------

@pytest.mark.parametrize("state", [0, 1, 2, 3, 4, 15, 16, 17, 100, 255])
def test_a_whole_painted_triangle_round_trips(state):
    attribute = codec.encode_leaf(state)
    leaves, truncated = codec.decode(attribute)
    assert not truncated
    assert [leaf.state for leaf in leaves] == [state]
    assert leaves[0].fraction == 1.0


def test_the_three_short_states_cost_one_hex_digit():
    # The classic encoding is what the Bambu/Orca dialect writes, and its
    # compactness is the reason a painted mesh does not double a project's size.
    assert len(codec.encode_leaf(0)) == 1
    assert len(codec.encode_leaf(2)) == 1
    assert len(codec.encode_leaf(16)) == 2
    assert len(codec.encode_leaf(17)) == 4


def test_a_split_triangle_round_trips_with_its_children_in_order():
    tree = (0, [1, 2, 3, 4])
    attribute = codec.encode_tree(tree)
    leaves, _ = codec.decode(attribute, TRIANGLE)
    assert [leaf.state for leaf in leaves] == [4, 3, 2, 1]
    assert all(leaf.fraction == 0.25 for leaf in leaves)


@pytest.mark.parametrize("children,shares", [
    ([1, 2], [0.5, 0.5]),
    ([1, 2, 3], [0.5, 0.25, 0.25]),
    ([1, 2, 3, 4], [0.25, 0.25, 0.25, 0.25]),
])
def test_every_split_type_tiles_the_triangle_exactly(children, shares):
    leaves, _ = codec.decode(codec.encode_tree((0, children)), TRIANGLE)
    assert [leaf.fraction for leaf in leaves] == shares
    assert sum(leaf.fraction for leaf in leaves) == 1.0
    whole = codec.area(TRIANGLE)
    assert sum(codec.area(leaf.points) for leaf in leaves) == pytest.approx(whole)


def test_nested_splits_still_tile_and_still_carry_their_own_corners():
    tree = (0, [1, (1, [2, (2, [3, 4, 5])]), 0, 6])
    leaves, truncated = codec.decode(codec.encode_tree(tree), TRIANGLE)
    assert not truncated
    assert sum(leaf.fraction for leaf in leaves) == pytest.approx(1.0)
    assert sum(codec.area(leaf.points) for leaf in leaves) == pytest.approx(
        codec.area(TRIANGLE))
    assert states(codec.encode_tree(tree)) == [0, 1, 2, 3, 4, 5, 6]


def test_every_special_side_is_decoded_the_way_it_was_encoded():
    for side in range(3):
        leaves, _ = codec.decode(codec.encode_tree((side, [1, 2])), TRIANGLE)
        assert sum(codec.area(leaf.points) for leaf in leaves) == pytest.approx(
            codec.area(TRIANGLE))


def test_an_empty_attribute_is_not_painted_rather_than_an_error():
    assert codec.decode("") == ([], False)
    assert codec.states("") == set()


def test_lower_case_hex_is_read_because_it_is_unambiguous():
    upper = codec.encode_leaf(16)
    assert upper == upper.upper() and any(ch.isalpha() for ch in upper)
    assert states(upper.lower()) == states(upper) == [16]


def test_states_helper_skips_geometry_and_agrees_with_the_full_decode():
    attribute = codec.encode_tree((0, [1, 2, 3, 4]))
    assert codec.states(attribute) == {1, 2, 3, 4}
    leaves, _ = codec.decode(attribute)
    assert all(leaf.points == () for leaf in leaves)


def test_a_degenerate_triangle_still_reports_its_shares():
    flat = ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (2.0, 2.0, 2.0))
    leaves, _ = codec.decode(codec.encode_tree((0, [1, 2])), flat)
    # No area to divide, but "half of it" is still true and still reported.
    assert [leaf.fraction for leaf in leaves] == [0.5, 0.5]
    assert codec.area(flat) == pytest.approx(0.0)


# --- files that are trying to break it ---------------------------------------

def test_a_non_hex_character_is_refused():
    with pytest.raises(codec.PaintFormatError):
        codec.decode("4Z")


def test_a_truncated_attribute_is_refused_rather_than_half_read():
    # A split promising four children, with the children missing.
    with pytest.raises(codec.PaintFormatError):
        codec.decode("3")


def test_trailing_data_beyond_the_triangle_is_refused():
    attribute = codec.encode_leaf(1) + "4"
    with pytest.raises(codec.PaintFormatError):
        codec.decode(attribute)


def test_an_over_long_attribute_is_refused_before_it_is_decoded():
    with pytest.raises(codec.PaintFormatError) as excinfo:
        codec.decode("0" * (codec.MAX_ATTRIBUTE_CHARS + 1))
    assert "more than" in str(excinfo.value)


def test_a_deeply_nested_attribute_stops_at_the_depth_bound():
    node = 1
    for _ in range(codec.MAX_DEPTH + 4):
        node = (0, [node, 0])
    with pytest.raises(codec.PaintFormatError) as excinfo:
        codec.decode(codec.encode_tree(node), TRIANGLE)
    assert "deeper than" in str(excinfo.value)


def test_a_very_wide_attribute_stops_at_the_leaf_bound_and_says_so():
    # Five levels of four-way splits is 1024 leaves, well inside the attribute
    # length bound and well past a caller asking for 64.
    node = 1
    for _ in range(5):
        node = (0, [node, node, node, node])
    leaves, truncated = codec.decode(codec.encode_tree(node), TRIANGLE,
                                     max_leaves=64)
    assert truncated
    assert len(leaves) == 64


def test_the_decoder_does_not_recurse_into_the_interpreter_limit():
    # Depth is refused by the bound, not by a RecursionError: the difference
    # matters because one is a diagnosis and the other is a crash.
    node = 1
    for _ in range(400):
        node = (0, [node, 0])
    with pytest.raises(codec.PaintFormatError):
        codec.decode(codec.encode_tree(node), TRIANGLE)


def test_encoding_a_state_the_format_cannot_hold_is_refused():
    with pytest.raises(codec.PaintFormatError):
        codec.encode_leaf(256)
    with pytest.raises(codec.PaintFormatError):
        codec.encode_leaf(-1)


def test_a_split_into_one_child_is_not_a_split():
    with pytest.raises(codec.PaintFormatError):
        codec.encode_tree((0, [1]))


# --- what a real brush actually writes ---------------------------------------

def test_an_attribute_far_longer_than_the_old_cap_decodes():
    """Studio refused any attribute over 4,096 characters. A single facet of a
    180 mm slab, painted with Snapmaker Orca's own round brush, is 35,460 — so
    the cap made a real project partly undecodable. The bound that matters is the
    work per project, not the length of one string."""
    node = 1
    for _ in range(7):
        node = (0, [node, node, node, node])
    attribute = codec.encode_tree(node)
    assert len(attribute) > 20_000
    leaves, truncated = codec.decode(attribute, TRIANGLE)
    assert not truncated
    assert len(leaves) == 4 ** 7
    assert sum(leaf.fraction for leaf in leaves) == pytest.approx(1.0)


def test_the_length_bound_still_exists_and_is_reported():
    with pytest.raises(codec.PaintFormatError) as excinfo:
        codec.decode("0" * (codec.MAX_ATTRIBUTE_CHARS + 1))
    assert "more than" in str(excinfo.value)


def test_a_long_attribute_costs_no_memory_before_it_is_read():
    # The reader walks the string; it does not turn it into a list of bits. A
    # 35,000-character attribute became 140,000 list entries under the old
    # reader, for a facet that might be discarded a moment later.
    reader = codec._Reader("0" * 30_000)
    assert reader.length == 120_000
    assert not hasattr(reader, "bits")
