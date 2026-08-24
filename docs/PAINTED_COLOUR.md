# Painted colour — what Studio reads, and where it stops

Multi-material painting is the part of a project most tools treat as opaque. A
model painted in four filaments looks, to a converter, like a mesh: the paint is
there in the file, but reading it means decoding a per-facet format nobody
documents in a specification. Studio decodes it.

This page is the honest boundary of that: what is read, what is measured, what is
proven, and what still needs the slicer.

## What Studio reads from a painted project

Before anything is sliced, from the project's own facet data:

- **Which filament slots the painting uses.** Exact, including slots the project
  paints with but never lists — which is a defect in the project, reported rather
  than renumbered onto a filament that happens to exist.
- **How many facets carry each colour, and how much surface each covers.** These
  are two different facts and are shown as two. A mesh's triangles are not equal
  in size, so "40% of the facets" is not "40% of the surface"; Studio never lets
  one wear the other's name.
- **The height band each painted colour occupies**, reconstructed from the
  painted patches themselves and put through the object's own placement, so the
  heights are heights on the plate.
- **Which slot the unpainted parts print in**, from the part's own assignment —
  or `unknown`, when the project does not say.
- **The height band of the objects themselves**, so a colour assigned to a whole
  object can be compared with a painted one. Two facts are kept apart here: where
  a colour is *painted*, and where it *prints at all*. A slot painted near the
  base of an object whose body it also prints is used over that whole object, and
  it is the second fact that decides whether it can share a layer with anything.

## What that changes

A project with six colours and four toolheads used to produce one answer:
*Studio cannot classify this safely*. Now each colour gets a verdict with the
evidence behind it:

- a colour whose height band overlaps another's **needs a toolhead**, because the
  two can meet on a layer;
- a colour used only between, say, 38.2 mm and 61.0 mm, with every other colour
  ending below or starting above, **can be a planned swap**;
- a colour that cannot be compared — no readable height, or another colour's
  extent was never measured — stays **unclassified, with the reason**.

The same rule now decides for a colour assigned to a whole object, which used to
be answered with a safe assumption: *an object on the plate is assigned this
colour, and a plate prints layer by layer, so it needs a toolhead*. That was true
whenever Studio had not measured where the object sat — and now that it does, two
objects at heights that cannot meet are two colours that can be swapped. Where the
measurement is missing, the safe assumption is still what remains.

## Where Studio stops

**Overlapping heights do not prove a shared layer.** Two colours painted between
10 mm and 20 mm *can* meet on a printed layer; whether any given layer really
carries both depends on the slice, and Studio does not slice. It says "these can
meet", never "these do".

Also unknown, and reported as unknown:

- a painted facet that points outside its own mesh — its slot is a fact, its
  place is not;
- painting on a project whose placement tilts the object, where a facet's height
  depends on where it sits in X and Y as well as Z;
- anything past the decoding bounds, on a project painted more finely than Studio
  decodes in full. The figures are then a floor, and say so.

## The format, in one paragraph

The PrusaSlicer and BambuStudio/OrcaSlicer families record painting the same way:
a short string of hexadecimal digits on each painted `<triangle>`, encoding a
subdivision tree whose leaves each name a filament. A facet may be split at its
edge midpoints, recursively, so the paint boundary can fall inside a triangle.
State 0 means "not painted here"; state *N* means the project's filament *N*,
counting from one. The dialects differ in the attribute's name —
`slic3rpe:mmu_segmentation` and `paint_color` — and in nothing else.

Studio's implementation is independent: `paint_codec` decodes the bits and
replays the subdivision on the facet's own corners, and `painted_color` reads the
container around it. Neither shares code with any slicer.

## Cross-slicer support, from test results

Every SUPPORTED cell below is something a test asserts against a file a real
slicer wrote. PARTIAL and UNKNOWN mean the evidence is not there yet — never that
a dialect is unsupported.

| | Snapmaker Orca 2.3.5 | OrcaSlicer 2.4.2 | BambuStudio | PrusaSlicer 2.9.6 |
|---|---|---|---|---|
| Painting detected | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED |
| Slot assignments decoded | PARTIAL | SUPPORTED | PARTIAL | SUPPORTED |
| Slot mapping proven against a real slice | PARTIAL | PARTIAL | PARTIAL | SUPPORTED |
| Painted geometry and area mapped | PARTIAL | SUPPORTED | PARTIAL | SUPPORTED |
| Height evidence available | PARTIAL | SUPPORTED | PARTIAL | SUPPORTED |
| Preserved through Prepare | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED |
| Preservation verified by Fidelity | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED |

What the two non-obvious columns rest on:

- **Snapmaker Orca 2.3.5** writes the same dialect as OrcaSlicer, which it is
  built from, and Studio's prepare and fidelity paths are exercised against that
  dialect in every run of the self-check. What is missing is a painted project
  written by Snapmaker Orca *itself*: its command line terminates with an access
  violation on every project it is given, including BambuStudio's own sample, so
  no file could be produced from it headlessly.
- **BambuStudio** is the same dialect again, and real BambuStudio projects are in
  the test suite — but none of them is painted, so decoding its painting is
  inherited from the shared encoding rather than demonstrated.
- **Slot mapping** — that paint state *N* is filament *N* — was proven by
  slicing a painted fixture for a five-extruder printer and reading the tools the
  G-code actually used. That slice was run by PrusaSlicer, so the proof is direct
  in that dialect and inherited in the others.

The fixtures, the commands that produced them and the recorded slice are in
[`backend/tests/fixtures/painted/PROVENANCE.md`](../backend/tests/fixtures/painted/PROVENANCE.md).
`tools/fixtures/make_painted.py` regenerates them against any slicer on the
machine and refuses to install a fixture the slicer rewrote.

## Bounds

A project decides how much data it hands over, so it does not get to decide how
much work Studio does. Painting is read under hard caps — facets decoded, patches
decoded, subdivision depth, attribute length, vertices per mesh — and exceeding
one is reported in the result rather than silently truncating the answer.

Measured on the sprint machine: 60,000 painted facets read in about 0.4 s;
200,000 in about 1.2 s; a 500,000-facet mesh with half of it painted in about
3.1 s, peaking near 240 MB. The reader also costs almost nothing on a project
with no painting, which is the common case: the paint attribute is absent, so no
mesh is parsed at all.
