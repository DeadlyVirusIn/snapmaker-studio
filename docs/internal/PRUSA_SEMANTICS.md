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
  neither the control view nor the raw view exposes a row, at any depth. It *can*
  be driven — the per-object settings this sprint measured were set by clicking
  into that panel at coordinates read off a screenshot — but a click is not a
  reading. Every value claimed anywhere in this document is read from a file Orca
  wrote, which is why the save route rather than the list is the method.
- **Slicing used to be a yes-or-no** — the plate footprint after slicing answered
  "did this part contribute material", and no toolpath was compared. That changed
  on 2026-08-26: G-code is now exported from Orca and read directly, so layer
  count, the Z sequence and per-object extrusion by feature are all measurable.
  Still nothing is sent anywhere.
- **Modifier carrying is implemented; see above.** The earlier note here saying
  it was "only reported" was already out of date when it was written.

Per-object overrides were on this list and are not any more. What settled them is
below.

## Per-object setting overrides — settled 2026-08-26

The previous instalment left these category D on the grounds that no real
Orca-family project in the fixtures carried one, so nothing proved a target
equivalent. That was a statement about the sample, not about the target. Asking
the target directly answered it.

### Orca's own words for them

Snapmaker Orca 2.3.6 has a per-object settings panel — **Process ▸ Objects**, then
the object in the tree, then the Frequent / Quality / Strength / Speed / Support
tabs beneath it. Three settings were changed there on a plain cube and Orca was
asked to Save Project As. Orca wrote, inside `<object>` in
`model_settings.config`:

| set in Orca's own panel | Orca wrote | level |
|---|---|---|
| Layer height 0.30 | `<metadata key="layer_height" value="0.3"/>` | **object** |
| Sparse infill density 45 | `<metadata key="sparse_infill_density" value="45%"/>` | **object** |
| Enable support ✓ | `<metadata key="enable_support" value="1"/>` | **object** |

Kept in `backend/tests/fixtures/orca-object-overrides/`, with a manifest the test
suite re-hashes. That file is the target stating its own vocabulary and its own
granularity, so nothing below rests on a name that happens to match.

### Recognition, with an invented key as the control

One key per file, everything else byte-identical, handed to Orca, saved back:

| written on the object | Orca wrote back |
|---|---|
| `layer_height="0.3"` | `layer_height="0.3"` |
| `sparse_infill_density="45%"` | `sparse_infill_density="45%"` |
| `enable_support="1"` | `enable_support="1"` |
| `snapstudio_nonsense_setting="0.3"` | **gone** |
| `object_layer_thickness="0.3"` | **gone** |
| **`fill_density="15%"`** — PrusaSlicer's own word | **gone** |
| **`support_material="1"`** — PrusaSlicer's own word | **gone** |

**The project Orca saved from the invented key is byte-identical to the project it
saved from `fill_density`, to the one it saved from `support_material`, and to the
one it saved from a project carrying no setting at all.** Copying the source's own
key across is not carrying the setting; it is writing nonsense with a straight
face. That single identity is why there is an allowlist rather than a copy loop.

Part level behaves the same way: the three real keys written on a `<part>` survive,
and an invented key or `fill_density` on a `<part>` does not. Studio writes at
object level regardless, because that is where Orca itself writes.

### What a value Orca cannot read costs

Not the setting. The object.

| written on the object | what Orca did |
|---|---|
| `layer_height="not-a-number"` | opened **with an empty plate** — no object, no build item, no geometry file |
| `layer_height="٠.٣"` (Arabic-Indic digits) | **object gone** |
| `enable_support="true"` | **object gone** |
| `enable_support="2"` | **object gone** |
| `layer_height="0"` | **Orca hung on load** — unresponsive, burning CPU, no clean close |
| `layer_height="-0.2"` | **Orca hung on load** |
| `layer_height="0.5"`, nozzle 0.4 | opened, then refused to slice: *"Layer height cannot exceed nozzle diameter"*, naming the object and the setting. Slice and Print greyed out. |
| `layer_height="99"` | kept in the file, **not clamped** |
| `sparse_infill_density="45"` | normalised to `45%` |
| `sparse_infill_density="0.45"` | normalised to `0.45%` — nought point four five percent, not forty-five |
| `sparse_infill_density="400%"` | kept, **not clamped** |
| `layer_height="0.300"` | normalised to `0.3` |

So every value Studio writes is checked first, and one that does not pass leaves
the setting uncarried and named rather than carried and broken.

### Behaviour, measured on both sides of the crossing

Two identical objects on one plate, A overridden and B not, sliced, and the
G-code read — layer count, Z sequence and per-object extrusion attributed through
the `; printing object <name>` markers both slicers emit.

| | PrusaSlicer 2.9.6 on the source | Snapmaker Orca 2.3.6 on Studio's copy |
|---|---|---|
| A layers / Z step | **41 at 0.3 mm** | **40 at 0.3 mm** |
| B layers / Z step | 60 at 0.2 mm | 60 at 0.2 mm |
| A infill | 641 mm — 3.0× B | 444 mm — 2.8× B |
| B infill | 214 mm | 159 mm |
| A support | 883 mm | 1819 mm |
| B support | **0** | **0** |

Every statement the source makes about A is a statement Orca acts on for A, and B
is untouched on both sides. The absolute lengths differ because the two slicers do
not draw infill or support the same way; what each setting *says* is the same. In
the single-variable isolation runs the non-overridden object's total extrusion was
identical to its own control to the last digit, in both slicers.

### The classification

| Source key | What PrusaSlicer means by it | Orca's key and level | Recognised? | Behaviour equivalent? | Classification |
|---|---|---|---|---|---|
| `layer_height` | this object's layers are this tall | `layer_height`, on `<object>` | yes — nonsense is dropped | yes — same layer count, same Z step, **on a single-filament plate only** | **EXACT**, conditional |
| `fill_density` | this object's sparse infill is this dense | `sparse_infill_density`, on `<object>` | **only after the rename** — the source's word is dropped like nonsense | yes — infill multiplies on that object alone | **PRESERVED_SEMANTIC** |
| `support_material` | generate support for this object | `enable_support`, on `<object>` | **only after the rename** | yes — support appears under that object alone | **PRESERVED_SEMANTIC** |

Everything else a source object can override stays **NOT_ESTABLISHED**, is not
carried, and is reported by name.

### The bug this sprint found on the way

> **Corrected 2026-08-26.** The rule stated below — that a foreign `Application`
> causes this — is too broad. It needs a foreign name **and** a flat root model,
> and only the case-sensitive substring `PrusaSlicer` counts. See *What Snapmaker
> Orca reads, and what it only stores* at the end of this document. The fix that
> shipped is unchanged and still correct; only the explanation was wrong.

Studio's prepared copy of a project it does not split keeps the source's root model
verbatim — including `<metadata name="Application">PrusaSlicer-2.9.6</metadata>`.
Handed that, Snapmaker Orca 2.3.6 says **"The 3mf is not supported by Snapmaker
Orca, loading geometry data only"** and then ignores `model_settings.config`
entirely.

What that cost, read from the project Orca saved back: object names replaced by the
file's own name, and **an object Studio had written as filament 3 came back as
filament 0, unassigned.** The per-object assignment this converter exists to
protect was correct in the file and never reached the slicer. The fidelity audit
compared the two files and called it preserved, because the file *was* right.

Isolated to that one line, one variable per file:

| the copy's root model says | Orca | object names | per-object settings |
|---|---|---|---|
| `Application = PrusaSlicer-2.9.6` | *"not supported… geometry data only"* | lost | dropped |
| the same file, `Application` replaced | opened as a project | kept | kept |
| the same file, `Application` removed | opened as a project | kept | kept |
| `BambuStudio:3mfVersion` added, `Application` untouched | *"not supported"* | lost | dropped |

The copy now states `SnapmakerStudio-u1convert`, which is true of it and is what
Studio's own writer already stamps on the projects it builds itself. Nothing else
in the root model is touched: a copy of a genuine PrusaSlicer root model differs
from its source in that one value and nowhere else, and a root model that claims
nothing is left exactly as it is.

### Still not established

- **Whether Orca applies a per-part override.** It stores one and does not drop it,
  and an invented key at part level *is* dropped, so it recognises the key there.
  Nothing was sliced to see whether it acts on it, and Studio writes at object
  level, so it did not need to be.
- **Every other per-object setting.** `ironing_type`, `seam_position`, `wall_loops`,
  `brim_width` and the rest are untested and uncarried.
- **`layer_height` between the profile's `max_layer_height` and the nozzle
  diameter** — 0.32 to 0.40 mm on the 0.4 nozzle. Orca refuses above the nozzle and
  accepts 0.3; the band between was not sliced. Studio's gate is the nozzle,
  because the nozzle is the refusal that was measured.

## What Snapmaker Orca reads, and what it only stores — measured 2026-08-26

Preserving a fact and the slicer using it are different things, and the previous
instalment found that out the hard way: a prepared copy stated an object's
filament correctly, the fidelity audit compared the two files and called it
preserved, and Orca — which had decided the file was foreign — loaded the geometry
and nothing else. The file was right and the print was wrong.

This section is that question asked of every load-bearing fact, one variable per
file, each answered from the project Orca saved back rather than from a warning.

### The Application gate — the previous instalment's rule was too broad

It said: *a foreign `Application` makes Orca load geometry only*. Measured
properly, the downgrade needs **two** things at once, and neither alone does it.

On a copy whose root model is **flat** — objects holding their meshes inline,
which is the shape Studio's verbatim path produces:

| `Application` | Orca |
|---|---|
| `SnapmakerStudio-u1convert` | full project |
| `PrusaSlicer-2.9.6` | **geometry only** |
| `PrusaSlicer` | **geometry only** |
| `MyTool (exported from PrusaSlicer)` | **geometry only** |
| `prusaslicer-2.9.6` (lower case) | full project |
| `SuperSlicer-2.5.59` | full project |
| `Slic3r-1.3.0` | full project |
| `SnapstudioNonsense-9.9.9` (invented) | full project |
| `BambuStudio-2.3.5` | full project |
| `OrcaSlicer-2.4.2` | full project |
| empty | full project |
| absent | full project |

So it is not "a foreign name". It is the **case-sensitive substring
`PrusaSlicer`**, anywhere in the value. An invented name is fine.

And on a copy whose root model uses **components into `3D/Objects/`** — the shape
Studio's multi-part path produces — `Application = PrusaSlicer-2.9.6` opened as a
**full project** with every name, assignment and per-object setting intact.

Crossing the two:

| root model | `Application` | slic3rpe traces | Orca |
|---|---|---|---|
| flat | `PrusaSlicer-2.9.6` | present | geometry only |
| flat | `PrusaSlicer-2.9.6` | **all removed** | **geometry only** |
| components | `PrusaSlicer-2.9.6` | **added** | **full project** |
| components | `PrusaSlicer-2.9.6` | absent | full project |

Adding the `BambuStudio` namespace, adding `BambuStudio:3mfVersion`, and removing
PrusaSlicer's own namespace all failed to lift it on the flat file. The fix that
shipped — never claiming to be PrusaSlicer — is still exactly right, and now for
the reason it actually works.

### The gates

**Required.** Without these the project is not read as a project:

| | what happens without it |
|---|---|
| `Metadata/model_settings.config` | **geometry only** — names become `Object_1`…, every object's filament reads 0, every per-object setting is gone |
| the same file, malformed | **rejected** — *"Snapmaker Orca error"*, nothing loads at all |
| `3D/_rels/3dmodel.model.rels` | remove one object file's relationship and that object survives **by name with zero parts**: its geometry and its painting are gone, 16 painted facets down to 8, 40 triangles down to 27, and Orca says nothing |
| `Application` not naming PrusaSlicer, on a flat root model | as above |

**Optional.** Absent or wrong, and nothing changed:

- `BambuStudio:3mfVersion` — absent, `not-a-number`, and `99` all opened as full projects
- `requiredextensions="p"` — removed, full project

**Reconstructed.** Orca rebuilds these from something else, so preserving them
byte-for-byte is not what makes them true:

| | measurement |
|---|---|
| `Metadata/slice_info.config` | removed *and* deliberately falsified (wrong types, wrong colours, wrong count): both opened identically, and Orca wrote an **empty** one back every time — including from the untouched control |
| `filament_maps` | written as `1` against five filaments; Orca wrote back `1 1 1 1 1` |
| `<model_instance>` records | all removed; Orca wrote back one per object |
| `<assemble>` | Studio writes none; Orca writes one entry per object, from the build transforms |
| `printer_model` | set to `Bambu Lab X1 Carbon` with everything else Snapmaker; came back `Snapmaker U1`, re-derived from `printer_settings_id` |
| object and component **ids** | renumbered on every save — 5/6/7 became 3/5/7 — while the transforms hanging off them came back unchanged |

**Consumed.** The file's value is honoured:

- `printer_settings_id`, `printer_variant`, `nozzle_diameter` — a 0.6-nozzle preset was kept
- `filament_colour` — `#112233FF` and friends came back exactly
- object and part `extruder`, object names, part `subtype`, part matrices, painting, per-object overrides
- `print_settings_id`

### The one that was silently discarding Studio's work

A project names a process preset and then lists that preset's values inline.
Studio assumed the inline values were the ones used. **They are not.**

| project_settings said | Orca kept |
|---|---|
| `layer_height="0.28"`, deviation **declared** | **0.28** |
| `layer_height="0.28"`, deviation **not declared** | **0.2** — the preset's |

The declaration is `different_settings_to_system`, and its shape is Orca's own.
Three values changed through Orca's own Global process panel and saved back:

```json
"different_settings_to_system": [
    "initial_layer_print_height;layer_height;seam_gap", "", "", "", "", ""
]
```

Entry 0 is the **process** preset, semicolon-joined and sorted. Entries 1..N are
the filaments, one each. The last is the printer. The list was six long for a
four-filament project and seven for a five-filament one.

The category matters, measured both ways: `nozzle_temperature` named in entry 0
was ignored and the value reset from 230 to 215; the same key named in the
filament entries was kept at 230. Naming a key Orca does not know costs nothing —
it keeps the real deviations and drops the invented name from what it writes back.

**What this was costing.** `u1_identity.normalize_presets` blanked every entry to
clear Orca's "Customized Preset" notice, and its comment said *"the customized
values themselves stay in the project (intent preserved)"*. Measured on a copy
Studio itself produced in optimize mode:

| Studio wrote | before the fix | after |
|---|---|---|
| `prime_tower_width` 60 | **30** | 60 |
| `prime_tower_brim_width` 2 | **5** | 2 |
| `brim_type` `no_brim` | **`auto_brim`** | `no_brim` |
| `exclude_object` 1 | **0** | 1 |
| `flush_multiplier` 0.2 | 0.2 | 0.2 |

`brim_type` and `exclude_object` are the shipping Snapmaker-Orca **compatibility
fixes**, applied on every Prepare in every mode and reported as applied. They had
never reached the slicer. Neither had any of optimize mode.

Studio now declares exactly the keys it changed, so a project that deviates in
nothing still imports without a notice. Its own U1 template used to state
`gap_fill_target: nowhere` where the preset it names says `topbottom` — undeclared,
so `nowhere` had never reached a print. The template now states `topbottom`, which
is what every Studio-prepared project has always printed with.

### A per-object layer height and a prime tower

The previous instalment proved a per-object `layer_height` reaches the slicer and
behaves, on a two-cube single-filament plate. On a multi-filament plate it does
not, and the plate does not slice at all:

| plate | override on one object | sliced |
|---|---|---|
| two filaments | none | **yes** |
| two filaments | `layer_height` | **no** |
| one filament | `layer_height` | **yes** |
| two filaments | `sparse_infill_density` | **yes** |

Orca says so by name and greys out Slice and Print:

> **Error: A prime tower requires that all objects have the same layer height.**
> *Jump to [B] (initial_layer_print_height)*

Carrying it would hand somebody a multi-colour plate that cannot be sliced, which
is worse than the object printing at the plate's layer height. So a per-object
layer height crosses only onto a plate that prints with one filament, and is
reported by name otherwise. Infill and support are unaffected.

The count that matters is the filaments the plate **prints with**, not the slots
it declares: every U1 project declares at least four, and the single-filament case
above declared four too.

### Still not established

- ~~`[Content_Types].xml` and the package-level `_rels/.rels`~~ — **settled
  2026-08-26**, see *The two package gates* below.
- **Which individual `project_settings` keys matter** beyond the ones above. The
  mechanism is settled — declared or reset — so the question is now which values
  Studio should be stating at all, not whether they arrive.
- **`layer_height` between the profile's `max_layer_height` and the nozzle
  diameter**, 0.32 to 0.40 mm on the 0.4 nozzle. Unchanged from the last
  instalment.

## The two package gates — measured 2026-08-26

The last instalment left these unmeasured. One variable per file, from a
known-good prepared project.

| `[Content_Types].xml` | Orca |
|---|---|
| correct | full project |
| **absent** | **full project** |
| stripped of its `png` declaration | full project |
| `.model` declared `text/plain` | full project |
| malformed XML | full project |

| `_rels/.rels` | Orca |
|---|---|
| correct | full project |
| **absent** | **rejected** — *"Snapmaker Orca error"*, nothing loads |
| target pointing at a file not in the archive | **rejected** |
| correct target, different relationship `Type` | **rejected** |
| malformed XML | **rejected** |

So `[Content_Types].xml` is **ignored** — Orca does not read it at all — and
`_rels/.rels` is **required**, down to the relationship `Type` URI and not merely
the target. Rejection here is harder than the geometry-only downgrade: nothing
loads, not even the mesh.

## The printer entry

`different_settings_to_system` has one entry per preset. The process entry and
the filament entries were established last instalment; the **last** entry is the
printer's.

| `nozzle_type` written as `stainless_steel` | Orca kept |
|---|---|
| not declared | **`hardened_steel`** — the preset's |
| declared in the last entry | **`stainless_steel`** |

The same file declared in the last entry also kept sentinel comments injected
into `machine_start_gcode` and `machine_end_gcode`, **and those sentinels reached
the exported G-code**. So the printer entry decides what the machine actually
runs.

`preset_deviation.PRINTER_KEYS` names the keys Studio has measured to belong
there. It is deliberately short: a key not on it is declared in the process
entry, where an unrecognised name costs nothing.

## What a prepared U1 project should state at all — settled 2026-08-26

A project names its presets and then lists most of their values inline. Studio's
template does that for 549 keys. Since a value is only used when it is also
declared, a restated preset default is not a setting — it is a comment the slicer
overwrites.

Classified against the effective Snapmaker Orca 2.3.6 U1 presets, inheritance
resolved, measured on the **prepared output** rather than the template (the
template's per-filament arrays are rewritten at prepare time, so the template
overstates the differences three-fold):

| | keys |
|---|---|
| equal to the effective preset — inherited in practice | **274** |
| no preset defines them — nothing to inherit from | **264** |
| genuinely different from the preset | **11** |

Of the eleven, two (`print_settings_id`, `printer_settings_id`) are the project
naming its own presets, and one (`gap_fill_target`) was fixed last instalment.
The remaining eight had no owning feature anywhere in Studio, and — being
undeclared — Orca replaced every one of them on load. **None had ever reached a
print.** They are removed:

| key | template said | preset says | owner |
|---|---|---|---|
| `machine_start_gcode` | dated `20251222` | dated `20260128` | printer |
| `machine_end_gcode` | ` PRINT_END\nTIMELAPSE_STOP` | the full by-object block | printer |
| `layer_change_gcode` | an older variant | the current one | printer |
| `nozzle_type` | `stainless_steel` | `hardened_steel` | printer |
| `default_print_profile` | `0.20mm Standard @Snapmaker` | a profile this Orca has not got | printer |
| `enable_pressure_advance` | `1` | `0` | filament |
| `supertack_plate_temp` | `35` | `40` | filament |
| `supertack_plate_temp_initial_layer` | `35` | `40` | filament |

The machine's own start and end G-code are the sharpest: they are what the
printer runs, they belong to the installed printer preset which tracks the
firmware, and Studio was shipping a five-week-old snapshot of them.

### The policy

**Inherit** — state nothing, let the installed preset supply it. For machine and
process defaults Studio did not choose. This is what the 274 identical keys
already do in effect, and what the eight removed keys now do in the file too.

**Pin and declare** — state the value *and* name it in the right entry of
`different_settings_to_system`. For source semantics Studio promised to carry,
Studio's compatibility fixes, and optimizations the user asked for. Undeclared,
none of these happens.

**Write structurally, never declare** — filament counts, colours, purge tables,
plate records. The project describing itself, which no preset owns.

**Remove** — a captured value with no owning feature that differs from the preset
for no reason. The eight above.

`backend/snapstudio_core/data/templates/PROVENANCE.md` records which group every
key belongs to, and `test_template_provenance` fails if one appears that belongs
to none.

### Version drift, 2.3.5 against 2.3.6

Both builds' U1 presets were resolved with inheritance flattened. The chains are
identical:

```
printer   Snapmaker U1 (0.4 nozzle) <- fdm_U1 <- fdm_toolchanger <- fdm_klipper
process   0.20 Standard @Snapmaker U1 (0.4 nozzle) <- fdm_process_U1_0.20
                                                   <- fdm_process_U1_common
                                                   <- fdm_process_U1
filament  Snapmaker PLA SnapSpeed @U1 <- Snapmaker PLA SnapSpeed @U1 base
```

The **process** preset is byte-identical between the two. Three inherited values
moved:

| key | 2.3.5 | 2.3.6 |
|---|---|---|
| `machine_start_gcode` | dated `20260128`, differing body | dated `20260128` |
| `supertack_plate_temp` | **absent** | `40` |
| `supertack_plate_temp_initial_layer` | **absent** | `40` |

Three of roughly 299 inherited values, and the two that appear are for a bed type
2.3.5 does not have. So inheriting is stable across the supported builds, and
pinning a machine G-code snapshot against a moving preset is the riskier of the
two — which is the case for removing it rather than declaring it.

**Studio does not read these preset files at runtime and must not start.** That
would be a second preset resolver to keep in step with every Orca release.
Studio knows what it changed because Studio made the change. The preset files are
audit evidence; `test_template_provenance` asserts no module reads them.

### The settings carried from a PrusaSlicer project

`prusa.CARRIED` translates five process values from the source — the layer
height, the first layer, the infill density, the wall count and the brim — so a
project sliced at 0.15 mm with four walls does not arrive at 0.2 mm with two.

They were not declared. Undeclared, every one is replaced by the U1 preset on
load: the whole promise, correct in the file and invisible to the slicer, exactly
the same defect as the compatibility fixes. They are declared now.

### Measured but not yet re-run through Orca

The desktop was in continuous use for the second half of this instalment and the
harness refuses to take the foreground from a window it does not own, so four
prepared fixtures are waiting rather than done:

* `N0_prusa_carry_undeclared` / `N1_prusa_carry_declared` — the source-carry pair;
* `M01_machine_gcode_undeclared` — an undeclared `machine_start_gcode` sentinel.
  The *category* is established by the pair above it (`nozzle_type` undeclared is
  reset, declared survives), but this specific control has not been run;
* `F1_everything_minimal` — three objects, a multi-part object, painting, five
  declared filaments, a per-object override and carried source settings, for the
  full-feature round-trip and the full-versus-minimal slice comparison.

Nothing above depends on them: the mechanism they would confirm was measured in
both directions on other files. They are named so the next session runs them
rather than assuming.
