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

- a colour whose height band overlaps another's **has a toolhead reserved**,
  because Studio cannot prove the two avoid each other — the overlap shows they
  *can* meet on a layer, not that they do;
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
counting from one.

The dialects differ in the attribute's name — `slic3rpe:mmu_segmentation` and
`paint_color` — and in nothing Studio has found. That is a claim with two
different kinds of evidence behind it, and they are worth keeping apart. Files
painted in **Snapmaker Orca**, **Bambu Studio**, **OrcaSlicer** and
**PrusaSlicer** all decode with one decoder, and none has needed a special case:
that is demonstrated. The two families' published sources also describe the same
serialisation, which is corroboration rather than proof. What has *not* been
tested is every state range in every dialect — the extended encoding above
filament 16, for instance, has only been seen from PrusaSlicer — so "nothing
else" is what the files have shown so far, not a guarantee about files nobody has
looked at.

Studio's implementation is independent: `paint_codec` decodes the bits and
replays the subdivision on the facet's own corners, and `painted_color` reads the
container around it. Neither shares code with any slicer.

## Crossing into a prepared U1 project

Reading a dialect and writing one are different problems. A copy prepared for
Snapmaker Orca states its painting in Orca's own vocabulary — `paint_color` — with
the encoded value unchanged, and puts the painted mesh in its own object file
behind a component. Both were measured against Orca 2.3.5: the identical painting
under PrusaSlicer's attribute name opens with nothing painted, and so does the
identical painting left in the project's root model. Neither condition is
optional, and neither alone is enough.

Studio writes no painting version. PrusaSlicer declares
`slic3rpe:MmPaintingVersion`; no project in the Orca/Bambu family declares a
painting version at all, and a copy without one opens correctly.

The fidelity audit reports a crossing as *preserved semantically* rather than
exactly, because the two files no longer say it the same way, and names the
translation. It compares each part's facets in order, so colour that lands on the
wrong part is a finding rather than a matching set of values.

## Cross-slicer support, from test results

Every SUPPORTED cell below is something a test asserts against a file a real
slicer wrote. PARTIAL and UNKNOWN mean the evidence is not there yet — never that
a dialect is unsupported.

| | Snapmaker Orca 2.3.5 | OrcaSlicer 2.4.2 | Bambu Studio 02.08.02.61 | PrusaSlicer 2.9.6 |
|---|---|---|---|---|
| Painting detected | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED |
| Slot assignments decoded | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED |
| Slot mapping proven against a real slice | PARTIAL | PARTIAL | PARTIAL | SUPPORTED |
| Painted geometry and area mapped | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED |
| Height evidence available | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED |
| Preserved through Prepare | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED |
| Preservation verified by Fidelity | SUPPORTED | SUPPORTED | SUPPORTED | SUPPORTED |

What each column rests on:

- **Snapmaker Orca 2.3.5** and **Bambu Studio 02.08.02.61**: a project *painted in
  that slicer's own interface* — its gizmo, its brush, its filament palette — and
  saved by it. Studio reads three filament slots from the Snapmaker Orca file and
  the exact area of the painted face from the Bambu Studio one, with nothing
  malformed in either, and Fidelity proves the painting survives Prepare. Neither
  file was sliced, so the mapping row stays PARTIAL for both.
- **OrcaSlicer 2.4.2**: a round trip — Studio wrote the paint, the slicer read it
  and wrote it back byte for byte. Its own authorship was not needed once
  Snapmaker Orca, which is built from it, had been driven directly.
- **PrusaSlicer 2.9.6**: the same round trip, *and* a real slice. Painting states
  1–5 drove tools T0–T4 and no others, which is the only direct proof anywhere
  here that a paint state names filament *N* counting from one. The other three
  dialects inherit that mapping from the shared encoding, and say so.

Two things the matrix deliberately does not claim. No cell says UNSUPPORTED:
where evidence is missing the cell is PARTIAL and the paragraph above says what is
missing. And "slot mapping proven against a real slice" is PARTIAL in three
columns even though the decoded slots plainly line up, because lining up is not
the same as being demonstrated.

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
