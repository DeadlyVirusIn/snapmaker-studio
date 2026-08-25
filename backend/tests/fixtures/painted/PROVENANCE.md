# Painted 3MF fixtures — where they came from and what they prove

Studio's paint decoder is only worth trusting if it has been run against files a
real slicer wrote. These two were, and the exact route is below so anyone can
reproduce them.

Both files carry Studio's own `examples/sample_cube.stl` geometry — a 20 mm cube,
twelve triangles. Neither carries a model anyone else authored, a private path, a
username, or a printer address. The paint in them was authored by Studio's own
encoder and then **handed to a real slicer, which read it, re-serialised it from
its own internal model, and wrote it back**. That round trip is the point: the
strings in these files are the slicers' own output, not Studio's.

| File | Written by | Dialect | Size | SHA-256 |
|---|---|---|---|---|
| `prusaslicer-2.9.6-painted-cube.3mf` | PrusaSlicer 2.9.6 | `slic3rpe:mmu_segmentation` | 2,158 B | `624931e5de76a4eca0c52c031b3ac66f1972036034a2e883eb7ea81b670adf3a` |
| `orcaslicer-2.4.2-painted-cube.3mf` | OrcaSlicer 2.4.2 | `paint_color` | 11,245 B | `80f47acceabf578f35a42345dc2af98950a9910aa298ffe568ec127555ca57f9` |

## How to reproduce them

`tools/fixtures/make_painted.py` does all of this; it needs a slicer on the
machine and is not run in CI.

1. PrusaSlicer converts the STL to a project of its own:
   `prusa-slicer-console.exe --export-3mf -o cube.3mf sample_cube.stl`
2. Studio's encoder writes paint onto eight of the twelve triangles: four whole
   triangles in slot 1, two in slot 2, one subdivided into slots 1–4 plus an
   unpainted quarter, and one in slot 5.
3. The slicer is asked to read that file and write it out again:
   `prusa-slicer-console.exe --export-3mf -o painted.3mf painted-in.3mf`
4. For the other dialect, the same paint is written into Studio's own
   `examples/sample_cube_U1.3mf` and round-tripped through
   `orca-slicer.exe --export-3mf=out.3mf --outputdir <dir> in.3mf`.

## What each one proves

* **The encoding is understood in both directions.** Both slicers wrote the paint
  attributes back *byte for byte* as Studio encoded them, including the
  subdivided triangle `480C501C3`. A slicer re-serialises from its own decoded
  model, so identical output means Studio's reading and the slicer's agree.
* **One encoding, two dialects.** The two files differ in the attribute's name
  and in where the mesh lives, and in nothing else: the same eight strings appear
  in both, and Studio's reader returns the same five slots and the same eight
  painted facets from each.
* **A state names a filament slot, counting from one.** The painted project was
  sliced for a five-extruder printer:
  `prusa-slicer-console.exe --slice --nozzle-diameter 0.4,0.4,0.4,0.4,0.4 …`
  The resulting G-code changes tool 194 times across **T0–T4 and no others**, and
  reports filament used on all five. States 1–5 became tools 0–4, which is the
  same thing said twice: state *N* is the project's filament *N*.
  Recorded in `slice-evidence.json`.
* **OrcaSlicer 2.4.2 does not declare a painting version.** Its output carries no
  `BambuStudio:MmPaintingVersion`, and Studio reports the version as unknown
  rather than assuming one.

## What they do not prove

The slice was run by PrusaSlicer, so the state-to-slot mapping is proven *in that
dialect*. In the Bambu/Orca dialect Studio has proven the encoding and its
survival through the slicer, and inherits the mapping from the shared encoding —
recorded as PARTIAL in the cross-slicer matrix rather than as SUPPORTED.

Snapmaker Orca 2.3.5's own command line could not be used: it terminates with an
access violation on every project it was given, including BambuStudio's own
sample, before doing any work. That is a limitation of its CLI, not of the
format, and it is why the Orca-dialect file here was written by OrcaSlicer 2.4.2,
the upstream Snapmaker Orca is built from.


## Painted in the slicer itself

The two files above were round-tripped: Studio's encoder wrote the paint and the
slicer wrote it back. These two were **painted in the slicer's own interface** —
its gizmo, its brush, its filament palette — and saved by it, which is a stronger
claim and the one the cross-slicer matrix now rests on for these dialects.

| File | Painted in | Size | SHA-256 |
|---|---|---|---|
| `snapmaker-orca-2.3.5-authored.3mf` | Snapmaker Orca 2.3.5 | 62,302 B | `9c7fcdb92326f93268e3618c1a9c5c65b1f877626fc08d891d20f5a51b592201` |
| `bambustudio-2.08.02.61-authored.3mf` | Bambu Studio 02.08.02.61 | 30,410 B | `2f63792e6e1b864d0bf2b26c7223894301d7cc42e415cd03cb5bee358295ea2d` |

### How they were made

Both are a 180 x 180 x 8 mm slab — twelve triangles — loaded from a public
directory so that no user name reaches the project file, which is where the first
attempt failed: Snapmaker Orca records the model's source path in
`model_settings.config`.

The slicer was then driven through its own UI: select the object, open the
colour-painting gizmo (`N`), choose a filament from the gizmo's palette, and
paint — whole facets with the triangle tool, and a stroke *inside* a facet with
the round brush, which is what makes the format subdivide a triangle. The project
was saved with Ctrl+S. Nothing in either file was written by Studio.

Neither slicer's own command line could do this: Snapmaker Orca's terminates with
an access violation on every project it is given, and painting is not a
command-line operation in any of them. The interaction was sent with SendInput and
verified by the saved file rather than by reading the screen.

### What they prove

* **Snapmaker Orca 2.3.5 writes `paint_color` in the encoding Studio decodes.**
  Three filament slots — 2, 3 and 4 — across two facets, one of them subdivided by
  the brush into tens of thousands of patches. Studio reads all of it with nothing
  malformed.
* **Bambu Studio 02.08.02.61 writes the same attribute.** Both triangles of the
  slab's top face in filament 2, which Studio measures as exactly 32,400 mm² —
  the face's real area.
* **Neither declares a painting format version.** Studio reports the version as
  unknown rather than assuming one, in both.
* **A real brush produces attributes far longer than Studio used to accept.** One
  Snapmaker Orca facet came to 35,460 characters against a 4,096-character cap,
  so Studio reported a genuine project as partly undecodable. That defect was
  found by this fixture and fixed; the test that holds the line is
  `test_the_longest_real_attribute_decodes`.

### What they do not prove

Neither project was sliced, so the state-to-filament mapping in this dialect is
still inherited from the shared encoding and from the PrusaSlicer slice recorded
above — not demonstrated by a Bambu Studio or Snapmaker Orca slice. That row
stays PARTIAL.
