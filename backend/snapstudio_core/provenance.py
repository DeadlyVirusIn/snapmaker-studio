"""Is this G-code actually the slice of the project I just checked?

Studio can read a project and a sliced job, and it can compare either against a
printer. What it could not do until now is establish that the two belong
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

**Evidence is not all of one kind, and that distinction decides the verdict.**

*Identity* evidence describes the model: which objects the job prints, how many
of them. Two files that print the same set of objects are the same project.

*Profile* evidence describes the setup: the machine, the materials, the colours
in each slot. Every job sliced on the same printer with the same spools loaded
agrees on all of it — so profile evidence corroborates a match and can never
establish one. A run of jobs from one workshop would otherwise all look like each
other's projects, which is exactly the confident-but-wrong answer this module
exists to avoid. With no identity evidence at all, the honest verdict is
``ambiguous``, however much of the profile lines up.

**A filename is never proof.** `benchy.3mf` and `benchy_PLA_2h.gcode` agreeing
tells you what someone typed, not what was sliced. Filenames and timestamps count
here only as weak corroboration, and never move a verdict on their own.
"""
from __future__ import annotations

SCHEMA_VERSION = "provenance/2"

CONFIRMED = "confirmed"
LIKELY = "likely"
AMBIGUOUS = "ambiguous"
NO_MATCH = "no_match"
UNKNOWN = "unknown"

#: What a signal is capable of saying. Identity evidence is about the model;
#: profile evidence is about the setup it was sliced with.
IDENTITY = "identity"
PROFILE = "profile"
CIRCUMSTANTIAL = "circumstantial"

#: Evidence weights. Positive supports a match, negative contradicts it. The
#: object names are worth more than everything else combined because two files
#: naming the same set of objects are, in practice, the same project.
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


def _evidence(name: str, weight: int, detail: str, kind: str, label: str) -> dict:
    """One piece of evidence, in the two forms the UI needs.

    ``label`` is the phrase shown in a list — "object fingerprint matched" —
    and ``detail`` is the sentence shown when someone asks why.
    """
    return {"signal": name, "weight": weight, "detail": detail,
            "kind": kind, "label": label}


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
    ruled_out = False

    # --- which objects each side names --------------------------------------
    names_verdict = _compare_object_names(project_traits, gcode_facts)
    if names_verdict:
        evidence.append(names_verdict["evidence"])
        ruled_out = ruled_out or names_verdict["rules_it_out"]

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
                                          f"all {shared} filament colours line up",
                                          PROFILE, "colour assignments matched"))
            elif same == shared:
                evidence.append(_evidence("filament colours", MEDIUM,
                                          "the filament colour matches",
                                          PROFILE, "colour assignments matched"))
            elif same == 0:
                # A project and its own slice share filament colours — preparing a
                # U1 copy does not repaint anything. None matching is the strongest
                # ordinary contradiction available, but it is still about the
                # setup: a project re-sliced after a spool change looks like this.
                evidence.append(_evidence("filament colours", -MEDIUM * 2,
                                          "no filament colour matches",
                                          PROFILE, "colour assignments differed"))
            else:
                evidence.append(_evidence("filament colours", 0,
                                          f"{same} of {shared} filament colours match",
                                          PROFILE, "some colour assignments differed"))

        families_project = [_family(s.get("type")) for s in project_slots if s.get("type")]
        families_job = [_family(s.get("type")) for s in job_slots if s.get("type")]
        if families_project and families_job:
            shared = min(len(families_project), len(families_job))
            if families_project[:shared] == families_job[:shared]:
                evidence.append(_evidence("materials", MEDIUM,
                                          "the materials in each slot agree",
                                          PROFILE, "material slots matched"))
            else:
                evidence.append(_evidence("materials", -MEDIUM,
                                          "the materials in each slot differ",
                                          PROFILE, "material slots differed"))

    project_count = _trait(project_traits, "filament_count")
    job_count = len([s for s in job_slots if s.get("type")]) or None
    if project_count and job_count and project_count != job_count:
        evidence.append(_evidence("filament count", -MEDIUM,
                                  f"the project defines {project_count} filament slot(s), "
                                  f"the job {job_count}",
                                  PROFILE, "filament slot count differed"))

    # --- the machine ---------------------------------------------------------
    project_printer = _trait(project_traits, "target_printer")
    job_printer = gcode_facts.get("printer_model")
    if project_printer and job_printer:
        if str(project_printer).strip().lower() == str(job_printer).strip().lower():
            evidence.append(_evidence("printer", MEDIUM, f"both name {job_printer}",
                                      PROFILE, "target machine matched"))
        else:
            # Not contradiction: preparing a U1 copy deliberately changes this.
            evidence.append(_evidence("printer", WEAK,
                                      f"the project targets {project_printer}, "
                                      f"the job {job_printer} — expected if you prepared a U1 copy",
                                      CIRCUMSTANTIAL, "target machine differed"))

    # --- object count --------------------------------------------------------
    project_objects = _trait(project_traits, "object_count")
    job_objects = (gcode_facts.get("objects") or {}).get("count") \
        or (gcode_facts.get("exclude_object") or {}).get("objects") or 0
    named = bool((gcode_facts.get("objects") or {}).get("name_hashes"))
    if project_objects and job_objects and not named:
        # Only worth counting when the names themselves could not be compared —
        # otherwise it repeats what the names already said.
        if project_objects == job_objects:
            evidence.append(_evidence("object count", MEDIUM,
                                      f"both contain {job_objects} object(s)",
                                      IDENTITY, "object count matched"))
        else:
            evidence.append(_evidence("object count", -WEAK,
                                      f"the project has {project_objects} object(s), "
                                      f"the job {job_objects}",
                                      IDENTITY, "object count differed"))

    # --- the weak signals, which can never carry a verdict alone -------------
    if project_name and gcode_name:
        stem = _stem(project_name)
        if stem and stem in _stem(gcode_name):
            evidence.append(_evidence("file name", WEAK,
                                      "the file names look related — which proves nothing on its own",
                                      CIRCUMSTANTIAL, "filename only matched weakly"))

    verdict, score = _weigh(evidence, ruled_out)
    out.update({
        "verdict": verdict,
        "score": score,
        "evidence": evidence,
        "identity_evidence": [e for e in evidence if e["kind"] == IDENTITY],
        "summary": _summary(verdict, evidence),
        "why": _why(verdict, evidence),
    })
    return out


def _hashes(value) -> set:
    return {h for h in (value or []) if h}


def _compare_object_names(project_traits: dict, gcode_facts: dict) -> dict | None:
    """The one signal that identifies a model rather than a setup.

    Both sides carry hashes of their object names, never the names. Comparing them
    as sets rather than as a single digest is what lets a job that prints *some* of
    a project's objects — one plate of several, or a file Studio could only read
    the ends of — be recognised as part of that project instead of mistaken for a
    different one.
    """
    job_block = gcode_facts.get("objects") or {}
    job_hashes = _hashes(job_block.get("name_hashes"))
    project_hashes = _hashes(_trait(project_traits, "object_name_hashes"))
    job_complete = bool(job_block.get("complete", True))

    if job_hashes and project_hashes:
        if job_hashes == project_hashes:
            return {"rules_it_out": False,
                    "evidence": _evidence("object names", STRONG,
                                          "the job prints the same set of objects as the project",
                                          IDENTITY, "object fingerprint matched")}
        shared = job_hashes & project_hashes
        if shared and job_hashes <= project_hashes:
            return {"rules_it_out": False,
                    "evidence": _evidence(
                        "object names", MEDIUM * 3,
                        f"the job prints {len(shared)} of the project's {len(project_hashes)} "
                        "objects and nothing else — one plate of it, or part of it",
                        IDENTITY, "object fingerprint matched (part of the project)")}
        if shared:
            weight = MEDIUM if len(shared) * 2 >= len(job_hashes) else -MEDIUM
            return {"rules_it_out": False,
                    "evidence": _evidence(
                        "object names", weight,
                        f"{len(shared)} object name(s) are shared, "
                        f"{len(job_hashes - project_hashes)} in the job are not in the project",
                        IDENTITY, "object fingerprint partly matched")}
        if not job_complete:
            # Studio read only the ends of a very large job, so the objects it saw
            # may not be all of them. That is not evidence against the match.
            return {"rules_it_out": False,
                    "evidence": _evidence(
                        "object names", -MEDIUM,
                        "none of the object names Studio could read match — but this job is "
                        "too large to read in full, so that is not conclusive",
                        IDENTITY, "object fingerprint did not match (job read in part)")}
        return {"rules_it_out": True,
                "evidence": _evidence("object names", -STRONG,
                                      "the job prints a different set of objects",
                                      IDENTITY, "object fingerprint did not match")}

    # Older callers, and files where only a combined digest is available.
    project_digest = _trait(project_traits, "object_name_digest")
    job_digest = job_block.get("name_digest") or \
        (gcode_facts.get("exclude_object") or {}).get("name_digest")
    if project_digest and job_digest:
        if project_digest == job_digest:
            return {"rules_it_out": False,
                    "evidence": _evidence("object names", STRONG,
                                          "the job names the same set of objects as the project",
                                          IDENTITY, "object fingerprint matched")}
        if not job_complete:
            return {"rules_it_out": False,
                    "evidence": _evidence(
                        "object names", -MEDIUM,
                        "the object names do not match, but this job is too large to read "
                        "in full, so that is not conclusive",
                        IDENTITY, "object fingerprint did not match (job read in part)")}
        return {"rules_it_out": True,
                "evidence": _evidence("object names", -STRONG,
                                      "the job names a different set of objects",
                                      IDENTITY, "object fingerprint did not match")}
    return None


def _weigh(evidence: list[dict], ruled_out: bool) -> tuple[str, int]:
    """Turn the evidence into one of five answers.

    The order matters. Identity evidence decides first — a project re-sliced in a
    different material is still that project, and a job printing different objects
    is not, whatever the setup says. Only when nothing identifies the model does
    the setup get a say, and then it can never do better than "cannot tell".
    """
    score = sum(item["weight"] for item in evidence)
    identity = [e for e in evidence if e["kind"] == IDENTITY]
    identity_score = sum(e["weight"] for e in identity)
    profile = [e for e in evidence if e["kind"] == PROFILE]
    real_signals = [e for e in evidence if abs(e["weight"]) > WEAK]

    if ruled_out:
        return NO_MATCH, score
    if identity_score >= STRONG:
        return CONFIRMED, score
    if identity_score >= MEDIUM * 2:
        return LIKELY, score
    if identity_score <= -(MEDIUM * 2):
        return NO_MATCH, score
    if identity_score < 0:
        return AMBIGUOUS, score

    # Nothing identifies the model. Whatever the setup says, this is as far as
    # honesty goes: every job from the same printer with the same spools agrees.
    if not real_signals:
        return UNKNOWN, score
    # Profile evidence can still rule a match *out*: a project and its own slice
    # share the spools they were sliced with. Weigh only what contradicts, so a
    # matching printer cannot cancel out every colour being different.
    if sum(e["weight"] for e in profile if e["weight"] < 0) <= -(MEDIUM * 2):
        return NO_MATCH, score
    if identity_score > 0:
        return LIKELY, score
    return AMBIGUOUS, score


def _stem(name: str) -> str:
    base = str(name).rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
    base = base.rsplit(".", 1)[0].lower()
    for suffix in ("_snapmakeru1", "_u1", "_placed"):
        base = base.replace(suffix, "")
    return base.strip("_- ")


def _why(verdict: str, evidence: list[dict]) -> str:
    """One sentence answering "why not more certain than that?"."""
    identity = [e for e in evidence if e["kind"] == IDENTITY]
    if verdict == CONFIRMED:
        return "The job and the project name the same objects, which is hard to produce by accident."
    if verdict == LIKELY:
        if identity:
            return ("The objects line up but not exactly — enough to recognise the project, "
                    "not enough to call it certain.")
        return "Several things agree, but nothing in either file identifies the model itself."
    if verdict == AMBIGUOUS and not identity:
        return ("Nothing in either file identifies the model. The printer and the filaments "
                "agreeing is expected of every job sliced on this machine, so it cannot tell "
                "one project from another.")
    if verdict == AMBIGUOUS:
        return "The evidence points both ways."
    if verdict == NO_MATCH:
        return "Something here cannot be true of the same project."
    return "Neither file states enough to compare."


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
        identity = [e for e in evidence if e["kind"] == IDENTITY]
        if not identity:
            return ("Studio cannot tell whether this is the same project: the printer and the "
                    "filaments match, but nothing in either file identifies the model. Every "
                    "job sliced on this machine would look like this.")
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
