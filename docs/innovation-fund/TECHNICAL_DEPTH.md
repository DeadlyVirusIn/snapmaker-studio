# Technical depth — the interesting problems, and how they are solved

Written for a reviewer who wants to know whether there is real engineering here or
a wrapper around a slicer. Every claim points at a module and a test.

---

## 1. Telling the truth about a file you did not write

**Problem.** A 3MF is an OPC/ZIP container with a small standard core and a large
amount of de-facto slicer convention layered on top. Two slicers write the same
data in different places, the same slicer writes it differently across versions,
and a project downloaded from a model site may be truncated, hostile, or produced
by a tool nobody has heard of. A tool that reports facts from such a file will,
sooner or later, report a fact that is not true.

**Approach.** `snapstudio_core/project_traits.py` returns every trait as a triple:

```python
{"value": True, "confidence": "confirmed",
 "evidence": "Metadata/project_settings.config printer_model"}
```

with four tiers — `confirmed`, `likely`, `informational`, `unknown`. Rules:

- A trait Studio could not measure is `None` at `unknown`, never `False`.
- Plate count from the project's own `<plate>` records is `confirmed`; the same
  number inferred from plate thumbnails is only `likely`, and the code says so.
- "This came from MakerWorld" is `likely` at best, because two signals that
  correlate with MakerWorld do not prove it.
- An unreadable file returns every documented key at `unknown` with a reason, so
  no caller can `KeyError`, and no caller can mistake silence for a negative.

**Why it is hard.** The temptation is to normalise unknowns to `False` because it
makes downstream code simpler. Doing so is what produces confident wrong answers.
The tests exist to hold the line: `test_generic_3mf_claims_nothing_it_cannot_see`,
`test_plate_count_from_thumbnails_is_only_likely`,
`test_likely_makerworld_stays_likely`.

**Performance.** The model part can be hundreds of megabytes. Studio reads a
bounded 96 KiB prefix for the `<model>` attributes and document metadata, and a
bounded suffix for the `<build>` items, because that is where those live. Trait
extraction on a large project is a constant-time read, not a full XML parse.

---

## 2. Knowing when not to ship the clever thing

**Problem.** A multi-plate project lays every plate's objects out on a single
coordinate grid, and the stride between plates is not recorded anywhere in the
file. Studio derived it — from each plate's object-cluster centre — and used it to
reposition every plate onto a U1 grid.

**What happened.** An independent adversarial review reproduced the failure: for
two plates whose parts sat off-centre, a true 370 mm stride was measured as
690 mm and the second plate was placed 745 mm along X, entirely off the bed, while
the result reported success. Two compounding mistakes: the measurement was of the
*parts*, not of the grid; and the "does this stride explain every plate" guard is
a tautology when there are only two plates, so the commonest case had no
validation at all. The derived gap was also unbounded, so a negative gap could put
two plates on the same physical plate.

**What was done.** The feature was withdrawn rather than patched. Studio cannot
observe the plate spacing, and a number it cannot observe should not drive a file
rewrite. `git log` carries the removal; `docs/innovation-fund/CHANGE_SUMMARY.md`
records it as withdrawn rather than shipped.

**What survived, because it never depended on the grid.** Each plate is judged on
whether its *own contents* fit a U1 plate — a size question, not a position one.
A plate's absolute coordinates on a multi-plate grid are an artefact of the
authoring slicer, so an object at X=900 on plate 3 is no longer reported as "off
the plate", which it never was. Multi-plate projects get a clear refusal that says
why, and Snapmaker Orca's Arrange is the right answer.

This is the most useful thing in this document. Every project can list what it
built; a project's judgement shows in what it took back out.

## 3. Placement, for the case that is decidable

For a single plate the question is fully determined by the file: where each object
sits, where the bed is, and whether one translation brings the whole arrangement
on. Studio reports the object, the edge and the millimetres, writes a
translation-only copy, and re-runs the same assessment against the file it
actually wrote — not against what the code intended to write — reporting failure
if the promise was not kept.

Rotation, scale and shear are copied through untouched; an item with no transform
is *given* one so it travels with the plate rather than being left behind.
`test_fix_only_touches_the_model_part` byte-diffs input against output and asserts
`3D/3dmodel.model` is the only entry that differs.

## 4. Costing from a measurement instead of a model

**Problem.** Most 3D-printing cost estimates are a volume times a density times a
price, presented with two decimal places it has not earned.

**Approach.** A sliced project records what the author's own slicer computed: per
plate, a predicted time and weight, and per filament slot, grams and metres. That
is the output of a real slicing run. `snapstudio_core/project_cost.py` costs from
it, supports a per-material price map so a plate mixing PLA with an expensive
support material is costed correctly, and states its basis in the result: *"the
slicing result stored in this project"*.

When the file has no such figures, it returns `available: false` with an
explanation — and distinguishes *"this project has not been sliced yet"* from
*"this project is sliced but records no material figures"*, because the fix is
different. It never substitutes an estimate.

---

## 5. Recommending a tool from evidence

**Problem.** Naming the right community tool for a file is a matching problem with
a strong failure mode: a plausible recommendation that is wrong is worse than no
recommendation, because it costs the user a download and their trust.

**Approach.** `snapstudio_core/ecosystem.py` scores a plain-data registry
(`data/ecosystem.json`) against measured traits with a deliberately tiny operator
vocabulary — `is_true`, `is_false`, `equals`, `at_least`. Constraints:

- A rule keyed on a trait whose value is unknown **never fires**.
- `at_least` rejects booleans, so `True` cannot sneak through a numeric comparison
  as `1`.
- Every recommendation carries the rule's own reason text, shown to the user.
- A tool is "installed" only when the shell passed in a path it found on disk.
- With nothing special detected, the answer is the official slicer and nothing
  clever.
- A registry test rejects any rule referencing a trait the engine does not
  measure, so a data-only contribution cannot silently never fire.

**Security boundary.** The webview can only ask to open a tool *by id*. The table
of install locations lives in Rust, and a launch resolves the id against that
table. There is no path through which the front end can ask the shell to execute
an arbitrary binary.

---

## 6. Compatibility corrections that do not become opinions

**Problem.** A foreign project needs a handful of settings corrected to open
cleanly in Snapmaker Orca on a U1. The risk is scope creep: once a converter is
allowed to change settings, it drifts into changing settings it merely disagrees
with, and the creator's tuning is lost.

**Approach.** `snapstudio_core/orca_import.py` draws one line: **compatibility is
not intent**. It corrects only values that make Snapmaker Orca misbehave on a U1
regardless of what the creator wanted, and it applies in every prepare mode
including Preserve, because these are not choices.

The brim rule shows the discipline. Snapmaker Orca's automatic-brim heuristic
differs from the authoring slicer's, so a project that printed without a brim can
acquire one. Studio overrides `auto_brim` — "let the slicer decide" — and leaves
`outer_brim`, `inner_brim`, `brim_ears` and an explicit width alone, because
those are decisions. `test_a_brim_the_creator_chose_is_left_alone` is the guard.

The filament self-index rule shows the other half. A short array can be padded
from its neighbours; `filament_self_index` cannot, because slot N must say N.
Padding it would be silently wrong, so it is rebuilt positionally.

**Accountability.** Every change carries its old value, a short reason and a
plain-language explanation, and flows into the conversion summary through the
existing preservation guard — which rejects any changed setting that the pipeline
did not explain. That guard caught this feature during development, which is
exactly what it is for.

---

## 7. Surviving a hostile file

Studio opens files people downloaded from the internet.

- `ThreeMF.open` meters every part through a hard byte budget (1 GiB total,
  512 MiB per part, 20,000 entries, all env-overridable) rather than trusting the
  ZIP header, so a decompression bomb is refused with a plain-language message
  instead of exhausting memory. Parts are never extracted to disk, which removes
  path-traversal from the threat model entirely.
- XML is parsed with entity resolution, network access and DTDs disabled.
- Printer addresses go through `validate_host()` before becoming a URL: hostnames,
  IPv4 and bracketed IPv6 accepted; schemes, credentials, paths, queries and
  embedded newlines rejected. Control POSTs use the same gate, so they are not a
  bypass.
- The loopback API refuses bodies over 1 MiB *before* allocating, ahead of the
  token check.
- The sidecar is bound to a Windows job object that dies with the app, so no
  orphan process survives a crash or a force-kill.

---

## 8. Where the engineering deliberately stops

- Studio does not slice, and will not.
- Studio does not modify firmware, printer configuration, or start prints.
- Studio does not fabricate a number it cannot measure.
- Studio does not claim a capability it has not detected — including "extended
  firmware is not installed", which it cannot prove.
- Studio does not half-apply a fix.

Each of these is a place where more features would be easy and less honest.
