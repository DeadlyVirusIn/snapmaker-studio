# Plate Remap — XML parser hardening (DEFERRED, plan + test backlog)

Status: **deferred.** The writer is unchanged. This documents the debt and the
work required to do the swap safely later.

## The debt
`snapstudio_core/plate_remap.py` parses and edits 3MF XML (`model_settings.config`)
with **regex** (`_parse_objects`, `_parse_plates`, `_set_object_extruder`,
`plate_remap.py:40-197`), while the rest of the engine uses a hardened **lxml**
parser (`config_io.py:6-10`, also used by `geometry.py`). Two XML strategies is
correctness debt: a valid-but-unusual `model_settings.config` (comments, CDATA,
nested/odd attribute order, namespaces) could be misparsed. The export is still
*safe* — `_verify_export` reopens the output and quarantines on any mismatch
(`plate_remap.py:207-277, 334-344`) — but a misparsed **dry-run** could silently
under-scope the change set shown to the user.

## Why it's deferred (not a quick fix)
Swapping to lxml means lxml **reserializes** `model_settings.config` on write. That
can change whitespace, attribute order, and quote style of that entry's bytes. The
current writer does a *scoped regex substitution* that touches only the target
`extruder` values and leaves the rest of the file's bytes intact. The top project
rule is: **do not change 3MF writer/export behavior unless the test suite proves
equivalence.** Proving Orca/other-slicer compatibility of a reserialized
`model_settings.config` is real work, not a drop-in. So the writer stays as-is.

## Plan (when picked up)
1. Use lxml for **parsing/inspection only** first (dry-run path): replace the regex
   `_parse_objects`/`_parse_plates` with lxml reads, keep the regex **writer**
   unchanged. This removes the misparse risk on the user-facing dry-run with zero
   change to written bytes. Lowest-risk first step.
2. Only if step 1 proves stable, consider an lxml-based writer — but gate it behind
   an equivalence proof (see tests).

## Required tests before any writer change
- **Byte-equivalence corpus:** for a set of real multicolor 3MFs, assert the
  lxml-written `model_settings.config` is accepted by Orca (manual) and that all
  non-`model_settings` entries remain byte-identical (extend `test_plate_remap.py`).
- **Parser parity:** lxml `_parse_objects`/`_parse_plates` produce identical object/
  plate/extruder maps to the current regex on the existing fixtures + new edge cases:
  XML comments, CDATA, namespaced tags, reordered attributes, single vs double quotes.
- **Dry-run scope parity:** lxml dry-run yields the same change set as regex on the
  real-fixture case (keep the env-gated `test_plate_remap_fixture.py`).
- **Quarantine still fires:** a deliberately corrupted write still lands in
  `.rejected` with the source untouched.
- Source-immutability + `out != src` refusal tests remain green.

## Constraints (unchanged, carried from the brief)
Source file never mutated · export writes a new file only · mesh/paint `.model`
entries byte-identical · only `Metadata/model_settings.config` may change · reopen/
reinspect verification + quarantine remain · the real-fixture conditional test remains.
