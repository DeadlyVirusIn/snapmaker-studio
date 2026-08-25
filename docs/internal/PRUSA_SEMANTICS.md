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
| Modifier / negative / support volumes | **Not carried** — reported, and never turned into printable geometry |
| Per-object setting overrides | **Not carried** — each one named |

Nothing in the "not carried" column is silently dropped. Each produces its own
fidelity row naming the object, the part and the fact.

## Not established in this sprint

Stated plainly so the next session does not assume otherwise:

- **Multi-part output is not implemented.** The format can hold it and Studio's
  prepare path still writes one part per object. The boundary is now described
  correctly; it has not moved.
- **Modifier and override carrying are not implemented** — only reported.
- **No prepared output was opened in Snapmaker Orca** for this work. The
  target-side facts come from a file Orca wrote, not from Orca reading Studio's.
- **No slice proof.** File semantics were deterministic enough not to need one,
  and it was not attempted.
- **Per-object override categorisation** (which Prusa settings have a true U1
  equivalent) was not done. Everything is currently reported as not carried, which
  is true today and is the safe direction.
