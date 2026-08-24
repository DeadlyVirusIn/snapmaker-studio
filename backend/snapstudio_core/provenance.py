"""Is this G-code actually the slice of the project I just checked?

Studio can now read a project and a sliced job, and it can compare either against
a printer. What it could not do until now is establish that the two belong
together — and every conclusion in the post-slice half depends on that. Checking
the wrong file against your printer is worse than checking nothing, because it
looks like an answer.

There is no identifier linking a 3MF to the G-code a slicer produced from it, so
this weighs the evidence that does exist and says how sure it is. Five verdicts,
and "cannot determine" is a real one:

* ``confirmed`` — evidence that is hard to produce by coincidence
* ``likely``    — several agreeing signals, none decisive
* ``ambiguous`` — signals both ways, or too little to separate candidates
* ``no_match``  — something that cannot be true of the same project
* ``unknown``   — neither side stated enough to compare

**A filename is never proof.** `benchy.3mf` and `benchy_PLA_2h.gcode` agreeing
tells you what someone typed, not what was sliced. Filenames and timestamps count
here only as weak corroboration, and never move a verdict to ``confirmed`` on
their own.
"""
from __future__ import annotations

SCHEMA_VERSION = "provenance/1"

CONFIRMED = "confirmed"
LIKELY = "likely"
AMBIGUOUS = "ambiguous"
NO_MATCH = "no_match"
UNKNOWN = "unknown"

#: Evidence weights. Positive supports a match, negative contradicts it. The
#: object-name digest is worth more than everything else combined because two
#: files carrying the same set of object names are, in practice, the same project.
STRONG = 100
MEDIUM = 25
WEAK = 5


def _trait(traits: dict, key: str):
    entry = (traits or {}).get(key)
    if isinstance(entry, dict):
        return entry.get("value")
    return entry


def _family(value: str | None) -> str | None:
    if not value:
        return None
    parts = str(value).strip().split()
    return parts[0].upper() if parts else None


def _evidence(name: str, weight: int, detail: str) -> dict:
    return {"signal": name, "weight": weight, "detail": detail}


def compare(project_traits: dict, gcode_facts: dict, *,
            project_name: str | None = None,
            gcode_name: str | None = None) -> dict:
    """Weigh a project against a sliced job."""
    out: dict = {
        "schema_version": SCHEMA_VERSION,
        "verdict": UNKNOWN,
        "score": 0,
        "evidence": [],
        "summary": "",
    }
    if not gcode_facts.get("available"):
        out["summary"] = gcode_facts.get("error", "Studio could not read that G-code file.")
        return out
    if not (project_traits or {}).get("readable", True):
        out["summary"] = "Studio could not read that project."
        return out

    evidence: list[dict] = []
    contradicted = False

    # --- object names, as a digest ------------------------------------------
    project_digest = _trait(project_traits, "object_name_digest")
    job_digest = (gcode_facts.get("exclude_object") or {}).get("name_digest")
    if project_digest and job_digest:
        if project_digest == job_digest:
            evidence.append(_evidence("object names", STRONG,
                                      "the job names the same set of objects as the project"))
        else:
            evidence.append(_evidence("object names", -STRONG,
                                      "the job names a different set of objects"))
            contradicted = True

    # --- filament slots ------------------------------------------------------
    project_slots = _trait(project_traits, "filament_slots") or []
    job_slots = gcode_facts.get("slots") or []
    if project_slots and job_slots:
        colours_project = [s.get("color") for s in project_slots if s.get("color")]
        colours_job = [s.get("color") for s in job_slots if s.get("color")]
        if colours_project and colours_job:
            shared = min(len(colours_project), len(colours_job))
            same = sum(1 for a, b in zip(colours_project[:shared], colours_job[:shared]) if a == b)
            if same == shared and shared >= 2:
                evidence.append(_evidence("filament colours", MEDIUM * 2,
                                          f"all {shared} filament colours line up"))
            elif same == shared:
                evidence.append(_evidence("filament colours", MEDIUM,
                                          "the filament colour matches"))
            elif same == 0:
                # A project and its own slice always share filament colours —
                # preparing a U1 copy does not repaint anything. None matching is
                # the strongest ordinary contradiction available.
                evidence.append(_evidence("filament colours", -MEDIUM * 2,
                                          "no filament colour matches"))
            else:
                evidence.append(_evidence("filament colours", 0,
                                          f"{same} of {shared} filament colours match"))

        families_project = [_family(s.get("type")) for s in project_slots if s.get("type")]
        families_job = [_family(s.get("type")) for s in job_slots if s.get("type")]
        if families_project and families_job:
            shared = min(len(families_project), len(families_job))
            if families_project[:shared] == families_job[:shared]:
                evidence.append(_evidence("materials", MEDIUM,
                                          "the materials in each slot agree"))
            else:
                evidence.append(_evidence("materials", -MEDIUM,
                                          "the materials in each slot differ"))

    project_count = _trait(project_traits, "filament_count")
    job_count = len([s for s in job_slots if s.get("type")]) or None
    if project_count and job_count and project_count != job_count:
        evidence.append(_evidence("filament count", -MEDIUM,
                                  f"the project defines {project_count} filament slot(s), "
                                  f"the job {job_count}"))

    # --- the machine ---------------------------------------------------------
    project_printer = _trait(project_traits, "target_printer")
    job_printer = gcode_facts.get("printer_model")
    if project_printer and job_printer:
        if str(project_printer).strip().lower() == str(job_printer).strip().lower():
            evidence.append(_evidence("printer", MEDIUM,
                                      f"both name {job_printer}"))
        else:
            # Not contradiction: preparing a U1 copy deliberately changes this.
            evidence.append(_evidence("printer", WEAK,
                                      f"the project targets {project_printer}, "
                                      f"the job {job_printer} — expected if you prepared a U1 copy"))

    # --- object count --------------------------------------------------------
    project_objects = _trait(project_traits, "object_count")
    job_objects = (gcode_facts.get("exclude_object") or {}).get("objects") or 0
    if project_objects and job_objects:
        if project_objects == job_objects:
            evidence.append(_evidence("object count", MEDIUM,
                                      f"both contain {job_objects} object(s)"))
        else:
            evidence.append(_evidence("object count", -WEAK,
                                      f"the project has {project_objects} object(s), "
                                      f"the job {job_objects}"))

    # --- the weak signals, which can never carry a verdict alone -------------
    if project_name and gcode_name:
        stem = _stem(project_name)
        if stem and stem in _stem(gcode_name):
            evidence.append(_evidence("file name", WEAK,
                                      "the file names look related — which proves nothing on its own"))

    score = sum(item["weight"] for item in evidence)
    strong_positive = any(i["weight"] >= STRONG for i in evidence)
    # A project and its own slice always share filament colours, so "none of them
    # match" rules it out even when the materials and the printer still agree —
    # which they will, for any two jobs from the same machine.
    decisive_negative = any(i["weight"] <= -(MEDIUM * 2) for i in evidence)
    real_signals = [i for i in evidence if abs(i["weight"]) > WEAK]

    if decisive_negative or contradicted:
        verdict = NO_MATCH
    elif strong_positive:
        verdict = CONFIRMED
    elif not real_signals:
        verdict = UNKNOWN
    elif score >= MEDIUM * 2:
        verdict = LIKELY
    elif score <= -MEDIUM:
        verdict = NO_MATCH
    else:
        verdict = AMBIGUOUS

    out.update({
        "verdict": verdict,
        "score": score,
        "evidence": evidence,
        "summary": _summary(verdict, evidence),
    })
    return out


def _stem(name: str) -> str:
    base = str(name).rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    base = base.rsplit(".", 1)[0].lower()
    for suffix in ("_snapmakeru1", "_u1", "_placed"):
        base = base.replace(suffix, "")
    return base.strip("_- ")


def _summary(verdict: str, evidence: list[dict]) -> str:
    reasons = [i["detail"] for i in evidence if abs(i["weight"]) > WEAK]
    joined = "; ".join(reasons[:3])
    if verdict == CONFIRMED:
        return f"This is the sliced version of that project — {joined}."
    if verdict == LIKELY:
        return f"This looks like the sliced version of that project — {joined}."
    if verdict == NO_MATCH:
        return (f"This does not look like the sliced version of that project — {joined}."
                if reasons else "This does not look like the sliced version of that project.")
    if verdict == AMBIGUOUS:
        return ("Studio cannot tell whether this is the same project — the evidence points "
                "both ways. Check the file yourself before trusting the comparison.")
    return ("Studio cannot tell whether this is the same project: neither file states enough "
            "to compare. The checks below still describe the job itself.")


def best_of(candidates: list[dict]) -> dict | None:
    """Pick the strongest match from several, or nothing when two tie.

    A folder can contain several sliced jobs. Two candidates that score the same
    are not a match — they are a question for the user, and returning one of them
    would be a guess wearing a verdict's clothes.
    """
    scored = [c for c in candidates if c.get("provenance", {}).get("verdict") in (CONFIRMED, LIKELY)]
    if not scored:
        return None
    scored.sort(key=lambda c: c["provenance"]["score"], reverse=True)
    if len(scored) > 1 and scored[0]["provenance"]["score"] == scored[1]["provenance"]["score"]:
        return None
    return scored[0]
