# What the two dialects actually mean — measured, not assumed

Established 2026-08-25 on `main`, after v0.8.0. **No release was made.**

## How this was established

Not by reading tag names. A candidate model config was placed inside a genuine
PrusaSlicer project and the project was handed back to
`prusa-slicer-console.exe --export-3mf` (PrusaSlicer **2.9.6**, the portable
build). Whatever the slicer wrote back is the answer, because the slicer wrote it.
One variable per run.

Target-side facts come from a project **Snapmaker Orca 2.3.5 authored itself**,
already in the repository as a painted-colour fixture. Snapmaker Orca's CLI
remains unusable, and no GUI automation was needed for any of this.

The resulting files are kept in `backend/tests/fixtures/prusa-semantics/` with a
manifest recording the slicer, the base project, a note on each case and a SHA256
that the test suite re-checks.

## What PrusaSlicer 2.9.6 said

| Question | Answer | Evidence |
|---|---|---|
| Is "no assignment" the same as "slot 1"? | **No.** A file with no `extruder` metadata comes back with none; a file saying `extruder="1"` comes back saying it explicitly. | `A_no_assignment_out.3mf`, `B_object_slot1_out.3mf` |
| Is a slot beyond the filament count clamped? | **No.** `extruder="6"` came back as 6. | `M_object_slot6_out.3mf` |
| Can one object hold volumes on different filaments? | **Yes, ordinarily.** Two volumes on filaments 2 and 5 round-tripped exactly. | `H_two_volumes_different_slots_out.3mf` |
| Do object-level and volume-level assignments coexist? | **Yes, independently.** Object 2 with a volume saying 4 kept both. | `N_object_and_volume_disagree_out.3mf` |
| Where do instances live? | **The build decides; the config states it.** A config claiming three instances against one build item came back claiming one, so the config cannot invent placements. But three build items came back as three *separate objects with their own ids*, not one object placed three times — so build object ids do not map onto config object ids. The slicer keeps `instances_count` true against the build it has, and that is the statement to read. | `inst3_out.3mf` |
| What are the volume roles? | `ModelPart`, `ParameterModifier`, `NegativeVolume`, `SupportEnforcer`, `SupportBlocker` — all round-trip. | `vt_*_out.3mf` |
| What happens to a role it does not recognise? | **It becomes printable geometry.** Handed the old Slic3r word `ModifierMesh`, 2.9.6 wrote back `ModelPart`. A modifier silently became solid. | `vt_ModifierMesh_out.3mf` |
| Do per-object setting overrides survive? | **Yes.** `layer_height`, `fill_density` and `support_material` all round-tripped. | `J_per_object_override_out.3mf` |

## What Snapmaker Orca 2.3.5 said

- An object nobody has assigned carries **`extruder="0"`** — the target dialect's
  own way of saying "no choice was made". Not slot zero.
- Parts carry **`subtype="normal_part"`**, the role field on that side.
- **A Snapmaker-Orca-family object can hold many parts on different filaments.**
  Two files already in the repository prove it: `orca-badge.3mf` has 39 parts
  across filaments 1–4, and `orca-pa-line-dual.3mf` has 16 parts across filaments
  up to 7.

That last row matters, because it moves a boundary. Studio had recorded that
"a prepared U1 object is a single part, so disagreeing volume filaments cannot be
represented". The **format** can represent them perfectly well. What cannot, today,
is Studio's own prepare path, which writes one part per object. That is a limit of
this tool and is now described as one.

## What Snapmaker Orca 2.3.5 did with a prepared project — measured 2026-08-25

The rows above read files Orca had written. These rows go the other way: Orca was
handed a prepared project, and the project **Orca saved back** was read. That file
is Orca's own account of what it understood, and it is machine-readable in a way
Orca's object list is not.

How: Studio starts its own Orca on the project (never touching one already
running), waits for it to load, drives **Save Project As** through the file
dialog — a standard Windows dialog, so its field and button are real UI Automation
elements — and reads the saved archive. Where the question was about printing
rather than about words, the plate is sliced first and the footprint Orca records
for it is read.

### How many filaments a project may declare

The slot Orca drops is not about the four nozzles. Measured across a ten-cell
matrix — declared filaments crossed with the slot one part asks for, one variable
per file:

| declared | part on 1 | part on 4 | part on 5 | part on 6 |
|---|---|---|---|---|
| 4 | kept | kept | **dropped to 0** | **dropped to 0** |
| 5 | — | kept | kept | **dropped to 0** |
| 6 | — | kept | kept | kept |

**Orca keeps a slot whenever the project declares that many filaments.** The four
physical nozzles never changed in any of the ten, and neither did the bed. Logical
filaments and toolheads are separate things, and a U1 project may declare more of
the first.

What grows with the count was measured the same way, by handing Orca a
six-filament project and reading which structures it held at six: the flush table
(square in the count), the flush vector (twice it), `filament_maps` (one entry per
filament, where Studio used to write a single `1`), and the per-filament rows of
`slice_info.config`. What stayed at four is every per-extruder option —
retraction, z-hop, wipe, nozzle diameter, extruder offset and colour, the
layer-height limits — and `printable_area`, which is the bed polygon and is four
entries long by coincidence. A naive "grow every four-element array" corrupts the
bed.

Studio's prepared copy now declares as many filaments as the source refers to,
across object assignments, volume assignments and painted colour. The extra
entries are padding and say so: the source gave no colour, vendor or material for
them.

### What Snapmaker Orca needs before it reads painted colour

Two things, and neither is optional. Measured by handing Orca one file at a time
and reading the project it saved back:

| the mesh is | the attribute is | painting after Orca |
|---|---|---|
| in the root model | `paint_color` | **none** |
| in its own object file, behind a component | `paint_color` | all 8 facets, same slots, same areas |
| in its own object file, behind a component | `slic3rpe:mmu_segmentation` | **none** |

So translating the attribute alone fixes nothing, and moving the geometry alone
fixes nothing. A prepared copy does both.

The encoded value is unchanged: the OrcaSlicer and PrusaSlicer painted-cube
fixtures carry byte-identical strings for the same eight facets. Crossing is a
rename and a move, not a re-encode.

**No painting version is invented.** PrusaSlicer declares
`slic3rpe:MmPaintingVersion`; Snapmaker Orca 2.3.5, OrcaSlicer 2.4.2 and
BambuStudio declare only `BambuStudio:3mfVersion`, and a copy carrying no painting
version at all opens correctly. Orca accepts `BambuStudio:MmPaintingVersion` if it
is there and does not need it, so Studio does not write one.

**Orca parses the attribute rather than copying it.** Handed a paint tree that
cannot be decoded, Orca 2.3.5 wrote back `00000000` — an unpainted facet. That
control is what makes the rows above evidence: a slicer that merely carried the
string across would have returned the broken one unchanged.

### What a volume's triangle range means

Pinned down by handing PrusaSlicer 2.9.6 projects and reading what it wrote back,
because a facet cannot be attributed to a volume until this is settled:

| Question | Answer |
|---|---|
| Are `firstid`/`lastid` inclusive? | **Yes.** 0 to 5 is six facets. |
| Can ranges leave a gap? | **Not from the slicer.** Handed 0–3 and 8–11 it re-laid the volumes contiguously as 0–3 and 4–7 and wrote an eight-facet mesh. |
| Can they overlap? | **Not from the slicer.** Handed 0–7 and 5–11 it duplicated the shared facets into the second volume and renumbered, writing a fifteen-facet mesh. |
| A reversed range? | **Refused.** "Found invalid triangle id", and no file written. |
| A range past the end of the mesh? | **Refused**, the same way. |

So a genuine file answers "which volume owns this facet" exactly once, and a file
that is not genuine may answer twice or not at all. Both of those are *unknown*.

**What Studio got wrong.** An unpainted patch prints in whatever its own volume is
assigned, and Studio answered that once per object — taking the first volume that
stated a slot as the answer for every facet. On the two-volume fixture that put
50 mm² under filament 2 that belongs to filament 5, and the *source* reading was
the wrong one: the prepared copy, which carries each part's own filament, had been
right all along. A facet is attributed to the volume whose range holds it now, and
the order is the volume's own assignment, then its object's where the volume is
silent, then unknown. Nothing inherits from a sibling volume.

Eight fixtures in `backend/tests/fixtures/prusa-volumes/`, each authored by the
slicer, pin the rule down. The two sharpest put the silence exactly where this
cube's only partly-painted facet is: its volume silent, its sibling on filament 5,
its object on 3. The answer is 3, and where the object is silent too the answer is
unknown. A reader leaking from a sibling would say 5 in both.

### A project of several objects

Snapmaker Orca's own badge project holds three objects. Each has its own object
file, its own relationship, its own composite object with its own components, its
own build item, and part ids that are unique across the whole project rather than
restarting per object; composite ids follow the parts rather than sharing their
numbers. That is the shape a prepared copy now takes for every logical object it
carries, and a project of three came back from Orca 2.3.5 with all three intact —
names, assignments, parts, filaments, geometry digests, painted-facet counts and
transforms.

One thing that is **not** a fault: two objects referencing the same mesh. The
`orca-pa-line-dual` fixture holds eight objects that all build from the same two
meshes, which is how it states eight copies of one pair. A validator check that
called that broken was written and removed again when the file disproved it.

### Orca prints the painting, not only reads it

The save round-trip shows Orca reading and rewriting a copy's painting. Slicing
shows what it does with it. A painted cube alone on the plate sliced to two
objects — the cube and a **wipe tower**. The same cube with its paint attributes
stripped sliced to the cube alone.

A wipe tower exists only for a print that changes filament, so its appearance is
Orca acting on the painting rather than carrying it, and its absence in the
control is what makes that a measurement rather than a coincidence.

### It reads two parts, and one of the two filaments

The prepared multi-part fixture — one object, parts on filaments 2 and 5 — came
back from Orca as:

| Claim | Result |
|---|---|
| One logical object holding two parts | **yes**, one composite object with two components |
| Part geometry | both part digests **identical** to what Studio wrote, 6 facets each |
| Part 1 filament | `extruder="2"` — **kept** |
| Part 2 filament | written as 5, came back **`0`** — not kept |
| The object's own assignment | `extruder="0"` — kept |
| Volume identity | Orca traced the two parts back as `source_volume_id` 0 and 1 |

So the multi-part structure is understood. **Filament 5 is not.** The U1 profile
configures four filaments, and a slot beyond that is discarded to "unassigned"
rather than clamped to the highest. Isolated by changing one number: the same file
with parts on filaments 2 and **4** came back with both kept exactly.

This does not change what Studio should write. PrusaSlicer round-trips slot 6
faithfully, so the source really does say 5 and a copy saying anything else would
be a different project. What it changes is what may be claimed: the *file* carries
filament 5; *Snapmaker Orca* does not act on it.

### The four helper roles are words it knows

Each role word was written into an otherwise identical project, and the project
Orca saved back was read. A deliberately invented word is the control.

| Studio writes | Orca writes back |
|---|---|
| `normal_part` | `normal_part` |
| `modifier_part` | `modifier_part` |
| `negative_part` | `negative_part` |
| `support_blocker` | `support_blocker` |
| `support_enforcer` | `support_enforcer` |
| `helper_thing` (invented) | **`normal_part`** |

The control is what makes the other five rows evidence. Orca does not pass unknown
words through — it does exactly what PrusaSlicer does with `ModifierMesh`, and
turns a role it does not recognise into printable geometry.

### And it treats them as things that do not print

Words are not behaviour. Two closed cubes that do not touch, written by Studio's
own multi-part writer, the second one carrying the role under test; the plate
sliced; the footprint Orca records for it read back.

| The second cube is a | Printed footprint | Plate thumbnail |
|---|---|---|
| `normal_part` | 500 mm² — both cubes | one image |
| `modifier_part` | **400 mm² — only the first cube** | a second image |
| `negative_part` | 400 mm² | byte-identical to the modifier's |
| `support_blocker` | 400 mm² | byte-identical |
| `support_enforcer` | 400 mm² | byte-identical |

400 mm² is the first cube alone; 500 is both. A helper volume that overlaps no
solid changes nothing, so this is the whole of the difference between a part that
prints and one that does not.

### Painting written in PrusaSlicer's dialect did not reach it, and now does

The prepared copy used to carry painted facets exactly as the source wrote them,
in PrusaSlicer's `slic3rpe:mmu_segmentation`, and Orca saved it back with **no
facet attributes at all**: 8 painted facets in, 0 out. Fixed — see *What Snapmaker
Orca needs before it reads painted colour* above for the two conditions and the
controls behind them.

The audit followed. Painting that crossed dialects is `preserved_semantic` with
the translation named rather than `preserved_exact`: the bits are the same string
and the statement is not. A copy that still carries the source's attribute name,
or whose painted mesh is in the root model, gets a row saying it opens with no
painting and what to do about it.

## What changed in Studio

**Unassigned crosses as unassigned.** Prepare wrote `extruder="1"` for an object
the source left alone, and the fidelity audit called that *preserved*. It now
writes `extruder="0"` — Orca's own vocabulary — and a copy that states a slot the
source never chose is reported as **changed**, with the reason spelled out: both
print from filament 1 today, but the copy now claims a choice the project never
made.

**The reader carries three facts it used to drop**: how many times an object is
placed (from the count the slicer maintains, with build items as a fallback for a
file that states none), what each volume is *for* in a normalised vocabulary, and
any per-object setting overrides.

That precedence was itself corrected mid-sprint. The first implementation counted
build items and preferred them — and a malformed-input test found that its regex
had never matched anything, so every count had silently come from the fallback it
was supposed to override. Fixing the regex then showed the build ids do not line
up with the config ids, which is what settled the precedence the other way. Both
the bug and the wrong assumption were invisible until something deliberately
hostile was fed in.

**Fidelity answers each fact for itself.** A volume's filament, a modifier's role,
the instance count and an overridden setting are four separate claims and get four
rows, classified `preserved_exact` / `preserved_semantic` / `changed` /
`unsupported` / `unverified`. One row saying "objects preserved" is how a copy
passes an audit while the structure underneath it changed.

**Instance flattening is named rather than mis-reported.** Prepare turns one
object placed three times into three objects placed once. Every copy is still on
the plate and the arrangement is identical; what is lost is the record that they
were copies of one thing. That is `preserved_semantic` — neither a clean pass nor
a loss. Before the reader could see instances at all it was reported as
`changed`, which is exactly the false alarm an audit must not raise.

**An unrecognised role is unknown, never a part.** Studio does not repeat
PrusaSlicer's own silent promotion of an unknown `volume_type` to `ModelPart`.

**A slot number is ASCII and bounded.** `str.isdigit()` is true for Unicode
digits, so a file containing `extruder="٣"` was arriving as slot 3 — a value no
slicer wrote, normalised silently. And an unbounded integer from someone else's
file was carried as an assignment. Both are now refused, and refused means
*unknown*, not slot 1.

## What is carried, and what is not

| Source fact | Crossing |
|---|---|
| Explicit object slot, any number | **Carried**, never renumbered |
| No assignment | **Carried as no assignment** (`extruder="0"`) |
| Volume slots that agree | **Carried** onto the object |
| Volume slots that disagree | **Not carried** — reported per part, with both filaments named, and Studio does not choose one |
| Instances | **Placements carried**, the copy-of-one relationship not |
| Modifier / negative / support volumes | **Carried** as their own parts, in the words Orca was measured to recognise |
| A volume role Studio does not recognise | **Not carried** — the object crosses whole, and the audit says its shape will print |
| Per-object setting overrides | **Not carried** — each one named |

Nothing in the "not carried" column is silently dropped. Each produces its own
fidelity row naming the object, the part and the fact.

## Multi-part output — implemented 2026-08-25

The boundary moved. A source object whose volumes carry facts of their own now
crosses as **real parts**, not as one mesh with metadata over it.

PrusaSlicer stores volumes as **triangle ranges inside one mesh**
(`<volume firstid="0" lastid="5">`). The prepared copy splits that mesh along those
ranges and emits the structure two genuine Orca-family projects proved:

    3D/3dmodel.model            one <object> holding one <component> per part,
                                zero meshes — it references geometry, never holds it
    3D/Objects/object_1.model   one mesh object per part, ids from 1
    3D/_rels/…rels              the object file declared as a relationship
    model_settings.config       <part id="N"> per component, each with its extruder

`part id` in the metadata, `objectid` on the component and the object id in the
Objects file are **the same number**. That identity is what makes the metadata
describe the geometry instead of decorating it.

Measured on the PrusaSlicer fixture with volumes on filaments 2 and 5:

| Claim | Result |
|---|---|
| Triangles | 12 in, 12 out, 6 per part, none duplicated anywhere in the archive |
| Geometry | the parts recombined hash **identical** to the source solid, facet by facet in winding order |
| Parts differ | the two part digests differ — a split that copied one mesh twice would not be a split |
| Filament | part 1 = 2, part 2 = 5; slot 5 **not** clamped to four |
| Object slot | still `extruder="0"`; the object's own assignment stays a separate fact |
| Painting | 8 painted facets in, 8 out, values identical, 6 on one part and 2 on the other |
| Fidelity | `volume_filament` flipped from `unsupported` to **`preserved_exact`** |

The split is deliberately narrow: one source object, one mesh, volumes as ranges
over it. Anything else declines and the object crosses whole, which is always
safe — the audit still reports what could not be carried. A single volume, or
volumes that all say the same thing, stay on the path that has been shipping.

A structural validator checks that the three descriptions agree, so Snapmaker Orca
is not the first thing to notice a disagreement. It catches a component pointing
at a missing mesh, a part record with no geometry, part ids that do not match
component ids, a duplicated part id, an object file that is not declared, a build
item placing the wrong object, and a malformed or non-numeric part matrix.

### Scale

100 parts over 10,000 triangles split in 25 ms, with the output vertex and
triangle counts equal to the source — the split shares nothing and duplicates
nothing.

### Modifiers — carried, once the target's words were measured

A modifier volume now crosses as its own part, with `subtype="modifier_part"` over
geometry typed `other`, and the audit reports the role as kept. The same is true
of a negative volume and of both support roles. What made that possible was not a
new idea about the format; it was measuring what those four words mean to Snapmaker
Orca, and having a control that shows an unknown word does not survive.

**The old behaviour was worse than "not carried" and the audit now says so.** When
a modifier was not emitted separately, its triangles stayed inside the single
prepared mesh — so the geometry crossed, as printable solid, and Orca printed it.
"Not carried" describes the role. It does not describe a modifier arriving as
plastic. A role Studio still cannot recognise takes exactly that path, and its
fidelity row says the shape is in the object and the slicer will print it.

A helper part states **no filament**. It prints nothing, so a material for it would
be a choice about nothing, and the eight modifier parts in a genuine Orca project
state none either. A slot the source did state is reported by the audit rather than
dropped quietly.

## Not established in this sprint

Stated plainly so the next session does not assume otherwise:

- **Orca's object list is still invisible to UI Automation.** It is custom-drawn:
  neither the control view nor the raw view exposes a row, at any depth. The list
  *was* reached and photographed — the earlier synthetic click failed because the
  script was DPI-unaware and Windows was handing it a virtualised desktop, so its
  coordinates were two thirds of the way to where it meant to click — but a
  photograph is not a value. Everything claimed above is read from a file Orca
  wrote, which is why the save route rather than the list is the method.
- **Slicing was used only as a yes-or-no.** The plate footprint Orca records after
  slicing answers "did this part contribute material"; no toolpath was compared,
  and no slice was sent anywhere.
- **Per-object overrides: all category D, not established.** The real
  Orca-family projects in the fixtures carry only `name` and `extruder` at object
  level — no per-object setting override appears in the sample at all. So nothing
  proves a target equivalent for `layer_height`, `fill_density` or
  `support_material`, and a matching name is not evidence of matching semantics.
  They stay reported as not carried.
- **Modifier and override carrying are not implemented** — only reported.
