"""The per-triangle paint encoding used by the PrusaSlicer/Orca 3MF family.

A slicer that lets you *paint* a model with a second filament has to record that
paint somewhere, and the whole family — PrusaSlicer, and the BambuStudio and
OrcaSlicer forks that Snapmaker Orca descends from — records it the same way: as
one short string of hexadecimal digits per mesh triangle, carried on the
``<triangle>`` element itself. An unpainted triangle carries nothing.

The string is not a colour. It is a *subdivision tree*: a painted triangle is
split at its edge midpoints, recursively, until the paint boundary is fine
enough, and each leaf of that tree carries a state. State 0 means "not painted,
use whatever this part already uses"; state N means "filament N".

This module is the format, and nothing else: bits in, subdivided triangles out.
It knows no 3MF and no project — :mod:`painted_color` does that — which is what
makes it directly testable against a real slicer's output.

What it recovers, and why that matters:

* **Which filaments a painted region references.** The states are exact. This is
  the fact that turns "this project has painting somewhere" into "this project
  paints with slots 1, 2 and 4".
* **Where the paint physically is.** Because every split is at an edge midpoint,
  the subdivision can be replayed on the triangle's own vertices, which gives the
  real position of every painted patch — and therefore real areas and real Z
  ranges, not a triangle count standing in for them.

Two limits are deliberate. Facet counts and areas are different facts and are
reported separately: 40% of a mesh's triangles is not 40% of its surface, and
Studio never lets one wear the other's name. And the decoder is bounded — a
hostile file can declare a subdivision far deeper than any real paint stroke, so
the work is capped and the result says it was capped rather than quietly
returning a smaller answer.

The format is understood from the public behaviour of files these slicers write
and from their published, long-stable interchange contract, which they document
as fixed for backwards compatibility. This is an independent implementation:
Studio's decoder shares no code with any slicer.
"""
from __future__ import annotations

from dataclasses import dataclass

SCHEMA_VERSION = "paintcodec/1"

# State 0 is "not painted here". Anything above it names a filament, counting
# from one — state 1 is the project's first filament.
STATE_UNPAINTED = 0

# The classic encoding reaches filament 16. The extended one reaches 255 through
# an escape, and Studio decodes both: reading a file it cannot write is exactly
# what a reader is for.
MAX_CLASSIC_STATE = 16
MAX_EXTENDED_STATE = 255

# The escape nibble that introduces an extended state. It cannot collide with a
# classic state, because the classic range stops before it.
_EXTENDED_ESCAPE = 0b1110

# Bounds. A real paint stroke on a real model subdivides a handful of levels; a
# file claiming far more is either broken or hostile, and either way Studio stops
# and says so instead of allocating.
MAX_DEPTH = 24
# A facet painted with a fine brush subdivides a long way: a single facet of a
# 180 mm slab, painted in Snapmaker Orca itself, came back as 35,460 characters
# and some ten thousand patches. The old caps here were 4096 of each, chosen
# before any slicer-authored file had been seen, and they made Studio report a
# real project as partly undecodable. The bound that matters is the total work
# per project, which painted_color enforces; these only stop one facet from
# consuming all of it.
MAX_LEAVES_PER_TRIANGLE = 65_536
MAX_ATTRIBUTE_CHARS = 1_000_000


class PaintFormatError(ValueError):
    """The attribute is not a well-formed paint string.

    Raised rather than guessed at. Callers count the triangle as malformed and
    carry on: one bad triangle must not cost the reader the rest of the file.
    """


@dataclass(frozen=True)
class Leaf:
    """One painted (or deliberately unpainted) patch of an original triangle.

    ``fraction`` is the patch's share of the original triangle's area, which is
    exact — every split is at edge midpoints, so every child's share is a power
    of two. ``points`` are the patch's own corners in the mesh's coordinates.
    """
    state: int
    fraction: float
    points: tuple[tuple[float, float, float], ...]


_HEX = {}
for _index, _char in enumerate("0123456789ABCDEF"):
    _HEX[_char] = _index
    _HEX[_char.lower()] = _index


class _Reader:
    """Bits of a paint attribute, read straight off the string.

    The string is written most-significant nibble first and each nibble is
    least-significant bit first, so the stream runs backwards through the
    characters. Nothing is materialised: a real slicer writes attributes tens of
    thousands of characters long for a finely painted facet — one of Snapmaker
    Orca's own came to 35,460 — and turning those into a list of bits was both
    unnecessary and the reason Studio used to refuse them.
    """

    __slots__ = ("text", "length", "pos")

    def __init__(self, attribute: str):
        if len(attribute) > MAX_ATTRIBUTE_CHARS:
            raise PaintFormatError(
                f"paint attribute is {len(attribute)} characters, "
                f"more than the {MAX_ATTRIBUTE_CHARS} Studio will decode")
        self.text = attribute
        self.length = len(attribute) * 4
        self.pos = 0

    def _bit(self, index: int) -> int:
        char = self.text[len(self.text) - 1 - (index >> 2)]
        nibble = _HEX.get(char)
        if nibble is None:
            raise PaintFormatError(
                f"paint attribute contains {char!r}, which is not a hex digit")
        return (nibble >> (index & 3)) & 1

    def take(self, count: int) -> int:
        """`count` bits, least significant first."""
        end = self.pos + count
        if end > self.length:
            raise PaintFormatError(
                "paint attribute ends part-way through a triangle")
        value = 0
        for offset in range(count):
            value |= self._bit(self.pos + offset) << offset
        self.pos = end
        return value

    def exhausted(self) -> bool:
        # A trailing partial nibble is normal: the stream is padded up to whole
        # hex digits, so leftover zero bits mean "nothing more", not a fault.
        return all(self._bit(index) == 0 for index in range(self.pos, self.length))


def validate(attribute: str) -> None:
    """Refuse an attribute that is not hexadecimal, before anything is decoded."""
    for char in attribute:
        if char not in _HEX:
            raise PaintFormatError(
                f"paint attribute contains {char!r}, which is not a hex digit")


def _midpoint(a: tuple[float, float, float],
              b: tuple[float, float, float]) -> tuple[float, float, float]:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0, (a[2] + b[2]) / 2.0)


# Each child's exact share of its parent, by split type. See `_children`.
_SHARES = {1: (0.5, 0.5), 2: (0.25, 0.25, 0.5), 3: (0.25, 0.25, 0.25, 0.25)}

# Every attribute that means "this whole facet is one colour", precomputed. The
# table is the decoder's own output, built once at import from the encoder, so it
# cannot drift away from the general path — the tests decode both ways and
# compare.
_WHOLE_FACET: dict[str, int] = {}


def _children(points: tuple, split_sides: int, special_side: int) -> list[tuple]:
    """The sub-triangles one split produces, in the order the format numbers them.

    A split cuts one, two or three sides at their midpoints. Which sides are cut
    is expressed relative to a *special side*, so the triangle's own corners are
    first rotated to start there. The resulting children tile the parent exactly:
    one split gives two halves, two splits give a quarter, a quarter and a half,
    and three splits give four quarters.
    """
    a, b, c = (points[special_side % 3],
               points[(special_side + 1) % 3],
               points[(special_side + 2) % 3])
    if split_sides == 1:
        m_bc = _midpoint(b, c)
        return [(a, b, m_bc), (m_bc, c, a)]
    if split_sides == 2:
        m_ab = _midpoint(a, b)
        m_ca = _midpoint(c, a)
        return [(a, m_ab, m_ca), (m_ab, b, m_ca), (b, c, m_ca)]
    if split_sides == 3:
        m_ab = _midpoint(a, b)
        m_bc = _midpoint(b, c)
        m_ca = _midpoint(c, a)
        return [(a, m_ab, m_ca), (m_ab, b, m_bc), (m_bc, c, m_ca),
                (m_ab, m_bc, m_ca)]
    raise PaintFormatError(f"a triangle cannot be split on {split_sides} sides")


def _read_state(reader: _Reader) -> int:
    """One leaf's state, from the prefix code the format uses.

    Small states cost two bits; filaments 3 to 16 cost six; the rest cost
    fourteen through an escape. Studio reads all three even though the dialect it
    most often meets only writes the first two.
    """
    head = reader.take(2)
    if head < 3:
        return head
    extra = reader.take(4)
    if extra != _EXTENDED_ESCAPE:
        return extra + 3
    return reader.take(8) + 17


def decode(attribute: str,
           points: tuple[tuple[float, float, float], ...] | None = None,
           *,
           max_leaves: int = MAX_LEAVES_PER_TRIANGLE) -> tuple[list[Leaf], bool]:
    """Decode one triangle's paint attribute.

    Returns the leaves and whether the decode was cut short by the leaf bound.
    ``points`` may be omitted when only the states matter; the leaves then carry
    the triangle's fractional shares with no coordinates.

    An empty attribute is not an error — it is how the format says "not painted".
    """
    if not attribute:
        return [], False
    # The overwhelmingly common case is a facet painted in one colour, written as
    # one or two hex digits. A real painted model has hundreds of thousands of
    # those, so it gets a path that allocates nothing: a fully general decode of
    # every facet is the difference between a card that appears and one a user
    # waits for.
    whole = _WHOLE_FACET.get(attribute)
    if whole is not None:
        return [Leaf(whole, 1.0, tuple(points) if points is not None else ())], False
    reader = _Reader(attribute)
    geometry = points is not None
    if geometry and len(points) != 3:
        raise PaintFormatError("a triangle needs exactly three corners")

    leaves: list[Leaf] = []
    truncated = False
    # An explicit stack, because a hostile file can nest far deeper than Python
    # will recurse, and hitting the interpreter's limit is not a diagnosis.
    stack: list[tuple[tuple | None, float, int]] = [(points, 1.0, 0)]
    while stack:
        node_points, fraction, depth = stack.pop()
        if depth > MAX_DEPTH:
            raise PaintFormatError(
                f"paint subdivision is deeper than the {MAX_DEPTH} levels "
                "Studio will follow")
        split_sides = reader.take(2)
        if split_sides == 0:
            state = _read_state(reader)
            leaves.append(Leaf(state, fraction,
                               tuple(node_points) if geometry else ()))
            if len(leaves) >= max_leaves and stack:
                truncated = True
                break
            continue
        special_side = reader.take(2)
        # Every split cuts sides at their midpoints, so each child's share of its
        # parent is fixed by the split type — exactly, for any triangle. The
        # shares are arithmetic, not measurement, and hold even where a mesh
        # carries a degenerate face with no area to measure.
        shares = _SHARES.get(split_sides)
        if shares is None:
            raise PaintFormatError(f"a triangle cannot be split on {split_sides} sides")
        kids = (_children(tuple(node_points), split_sides, special_side) if geometry
                else [None] * (split_sides + 1))
        # Children are written last-first, so they are pushed in forward order to
        # be popped in the order the stream presents them.
        for index in range(len(kids)):
            stack.append((kids[index], fraction * shares[index], depth + 1))
    if not truncated and not reader.exhausted():
        raise PaintFormatError(
            "paint attribute carries more data than its triangle accounts for")
    return leaves, truncated


def area(points: tuple[tuple[float, float, float], ...]) -> float:
    """Area of a triangle in space."""
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = points
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    return 0.5 * (nx * nx + ny * ny + nz * nz) ** 0.5


def states(attribute: str, *, max_leaves: int = MAX_LEAVES_PER_TRIANGLE) -> set[int]:
    """Just the states one attribute references — the cheap path.

    Used where the question is "which filaments does this project paint with",
    which needs no geometry and must stay fast on a mesh with a million painted
    triangles.
    """
    leaves, _ = decode(attribute, None, max_leaves=max_leaves)
    return {leaf.state for leaf in leaves}


# ---------------------------------------------------------------------------
# Encoding.
#
# Studio does not paint models and has no reason to write paint into a project.
# The encoder exists so the decoder can be tested against data whose intent is
# known, and so Fidelity can build a deliberately damaged copy and prove it is
# caught. It is the inverse of the decoder, and the round-trip is a test.
# ---------------------------------------------------------------------------
def encode_leaf(state: int) -> str:
    """The attribute for a whole triangle painted with one state."""
    return encode_tree(state)


def encode_tree(node) -> str:
    """Encode a subdivision tree.

    A node is either an integer state, or a tuple
    ``(special_side, [child, ...])`` whose child count is two, three or four.
    """
    bits: list[int] = []
    _encode_node(node, bits)
    # Pad to whole nibbles, then emit most significant nibble first.
    while len(bits) % 4:
        bits.append(0)
    digits = []
    for start in range(0, len(bits), 4):
        nibble = sum(bit << offset for offset, bit in enumerate(bits[start:start + 4]))
        digits.append("0123456789ABCDEF"[nibble])
    return "".join(reversed(digits))


def _encode_node(node, bits: list[int]) -> None:
    if isinstance(node, int):
        _push(bits, 0, 2)
        state = node
        if state < 0 or state > MAX_EXTENDED_STATE:
            raise PaintFormatError(f"state {state} is outside the format")
        if state < 3:
            _push(bits, state, 2)
        elif state <= MAX_CLASSIC_STATE:
            _push(bits, 3, 2)
            _push(bits, state - 3, 4)
        else:
            _push(bits, 3, 2)
            _push(bits, _EXTENDED_ESCAPE, 4)
            _push(bits, state - 17, 8)
        return
    special_side, children = node
    split_sides = len(children) - 1
    if split_sides not in (1, 2, 3):
        raise PaintFormatError("a split produces two, three or four children")
    _push(bits, split_sides, 2)
    _push(bits, special_side, 2)
    for child in reversed(children):
        _encode_node(child, bits)


def _push(bits: list[int], value: int, count: int) -> None:
    for shift in range(count):
        bits.append((value >> shift) & 1)


def _build_whole_facet_table() -> None:
    """Fill the single-colour lookup from the encoder itself."""
    for state in range(MAX_EXTENDED_STATE + 1):
        attribute = encode_leaf(state)
        _WHOLE_FACET[attribute] = state
        # A file may pad an attribute with a leading zero nibble; it means the
        # same thing and is worth the same shortcut.
        _WHOLE_FACET.setdefault("0" + attribute, state)


_build_whole_facet_table()
