"""Whether a fact Studio preserved is a fact Snapmaker Orca reads.

The fidelity audit compares two files and answers one question: *did the fact
Studio read out of the source end up in the copy?* That question can be answered
"yes" about a fact the slicer never looks at.

It happened. A prepared copy stated an object's filament correctly, the audit
called it preserved, and Orca — which had decided the file was foreign — loaded
the geometry and nothing else, so the object printed unassigned. The file was
right and the print was wrong, and nothing in the report could tell the
difference.

So a fact now carries two answers, kept apart:

* **file** — Studio's own comparison, which is what the fidelity status already is;
* **target** — whether Snapmaker Orca was measured to act on it.

Nothing here is inferred from a file format or a key name. Every row below is a
project handed to Snapmaker Orca 2.3.6, saved back by Orca, and read — with a
control that changes one thing, because a fact that survives when nonsense also
survives has not been shown to be read at all.
"""
from __future__ import annotations

#: Orca was measured to read this and act on it.
REACHES = "reaches_target"
#: Orca rewrites this from something else, so preserving it byte-for-byte is not
#: what makes it true — and changing it does not make it false.
RECONSTRUCTED = "reconstructed"
#: Orca ignores it entirely. Preserving it costs nothing and buys nothing.
IGNORED = "ignored"
#: Never measured. Not a complaint and not a promise.
NOT_ESTABLISHED = "not_established"

#: What each fact was measured to be, and the measurement that says so.
#:
#: Keyed by the start of the fidelity row's element text, longest match first.
MEASURED: dict[str, tuple[str, str]] = {
    "Objects": (
        REACHES,
        "Orca lists every object it was given; removing model_settings.config "
        "left it naming them Object_1, Object_2, Object_3 instead."),
    "Which filament each object uses": (
        REACHES,
        "an object written as filament 3 came back as filament 3, and came back "
        "as 0 when the same copy was made unreadable to Orca."),
    "Which colour each object uses": (
        REACHES,
        "same measurement — the per-object assignment is read from "
        "model_settings.config, which Orca needs in order to read any of it."),
    "Filament for each part of": (
        REACHES,
        "parts written on filaments 2 and 5 came back on 2 and 5."),
    "Part roles in": (
        REACHES,
        "the four helper roles round-trip and an invented role word does not."),
    "Settings set on": (
        REACHES,
        "a per-object setting Orca knows came back stated; an invented key, and "
        "PrusaSlicer's own words for the same settings, came back gone."),
    "Painted colour": (
        REACHES,
        "Orca re-encodes the painting rather than copying it — handed a paint "
        "tree it could not decode it wrote back an unpainted facet — and a "
        "painted plate slices to a wipe tower that an unpainted one does not."),
    "Copies of": (
        RECONSTRUCTED,
        "Orca rebuilds the plate's model_instance records: a copy with none was "
        "saved back with one per object."),
    "Filament colours": (
        REACHES,
        "colours written as #112233FF and friends came back exactly."),
    "Filament slots": (
        REACHES,
        "a part on a slot within the declared count keeps it; beyond the count "
        "it comes back unassigned."),
    "Plates": (
        REACHES,
        "the plate count survives; a project's plate block is read."),
    "Per-object settings and plate layout": (
        REACHES,
        "removing model_settings.config costs every per-object fact at once."),
    "Print settings": (
        NOT_ESTABLISHED,
        "a process value reaches the slicer only when it is declared in "
        "different_settings_to_system, and which of these are declared depends "
        "on what Studio changed. The declaration is measured; this row is a "
        "count of many settings and is not."),
    "Sliced output": (
        IGNORED,
        "Orca re-slices; the authoring slicer's toolpaths are removed."),
    "Filament for ": (
        REACHES,
        "an object written as filament 3 came back as filament 3."),
    "The painting on each part of": (
        REACHES,
        "Orca re-encodes the painting rather than copying it, and a painted "
        "plate slices to a wipe tower that an unpainted one does not."),
    "The shape of each part of": (
        REACHES,
        "geometry is the one thing Orca loads even when it refuses the rest of "
        "the project — the geometry-only mode is named for it."),
    "Where ": (
        REACHES,
        "the build item's transform came back unchanged while Orca renumbered "
        "the object ids around it."),
    "Model geometry and object placement": (
        REACHES,
        "same measurement: the transforms survive, the ids they hang off do not."),
    "Model relationships": (
        REACHES,
        "REQUIRED. Removing one object file's relationship left its object named "
        "in the metadata with zero parts, its geometry and its painting gone, and "
        "Orca said nothing."),
    "Archive relationships": (
        NOT_ESTABLISHED,
        "the package-level relationships were not varied one at a time."),
    "Archive index": (
        NOT_ESTABLISHED,
        "[Content_Types].xml was not varied one at a time."),
    "Slicing summary": (
        RECONSTRUCTED,
        "slice_info.config is Orca's own output. A copy with it deliberately "
        "wrong, and a copy with it removed, both opened identically, and Orca "
        "wrote an empty one back in every case."),
}


def of(element: str) -> tuple[str | None, str | None]:
    """The measured target verdict for a fidelity row, and why.

    Returns `(None, None)` for a row nobody has measured, which is different
    from a row measured to be ignored.
    """
    for prefix in sorted(MEASURED, key=len, reverse=True):
        if element.startswith(prefix):
            return MEASURED[prefix]
    return None, None


#: Rows whose file status is good but whose target status is not, in the words a
#: person reads. A status the slicer ignores must not be shown as a plain win.
def qualifies(status_target: str | None) -> bool:
    return status_target in (RECONSTRUCTED, IGNORED, NOT_ESTABLISHED)
