"""Failure-Pattern Learning — turn the printer's OWN print history into insight.

Reads the U1's Moonraker [history] (already fetched read-only elsewhere) and
surfaces the patterns a human would spot by scrolling the list: how often prints
fail, which files fail repeatedly, the most common failure type, and whether
failures are recent / clustered. This is insight + recommendations, not telemetry
re-display: it never fabricates causes it can't see in the history.
"""
from __future__ import annotations
from collections import Counter

SCHEMA_VERSION = "failurepatterns/1"

# Moonraker [history] statuses that mean a print did not finish cleanly.
_FAILURE_STATES = {"error", "cancelled", "klippy_shutdown", "klippy_disconnect", "interrupted"}

# Plain-language names for the raw klipper/moonraker failure statuses.
_CAUSE_LABEL = {
    "error": "errored mid-print",
    "cancelled": "cancelled by hand",
    "klippy_shutdown": "firmware shutdown (often a thermal or endstop fault)",
    "klippy_disconnect": "lost connection to the printer board",
    "interrupted": "interrupted (power loss or host restart)",
}


def _base(filename):
    if not filename:
        return None
    return filename.replace("\\", "/").split("/")[-1]


def assess(jobs, totals=None) -> dict:
    """Analyse a list of Moonraker history jobs (newest first) into failure insight.

    jobs: list of dicts with at least `filename` and `status`.
    totals: optional Moonraker job_totals (unused for now; reserved).
    """
    finished = [j for j in (jobs or []) if j.get("status")]
    n = len(finished)
    if n == 0:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "no completed prints in history yet"}

    fails = [j for j in finished if j.get("status") in _FAILURE_STATES]
    fcount = len(fails)
    rate = fcount / n
    findings: list = []
    worst = "ok"

    def bump(level: str) -> None:
        nonlocal worst
        order = {"ok": 0, "warn": 1, "risk": 2}
        if order[level] > order[worst]:
            worst = level

    # 1. Overall failure rate (over the visible window).
    pct = round(rate * 100)
    if fcount == 0:
        findings.append({"level": "ok", "text": f"All {n} recent prints finished cleanly — no failures in this history."})
    else:
        level = "risk" if rate >= 0.4 else "warn" if rate >= 0.15 else "ok"
        bump(level)
        findings.append({"level": level,
                         "text": f"{fcount} of the last {n} prints didn't finish ({pct}%). " +
                                 ("That's high — worth pinning down a cause below." if level != "ok"
                                  else "An occasional failure is normal.")})

    # 2. Repeat offenders — the same file failing more than once.
    by_file = Counter(_base(j.get("filename")) for j in fails if _base(j.get("filename")))
    repeat_offenders = [{"filename": f, "failures": c} for f, c in by_file.most_common() if c >= 2]
    if repeat_offenders:
        bump("warn")
        top = repeat_offenders[0]
        findings.append({"level": "warn",
                         "text": f"\"{top['filename']}\" failed {top['failures']} times — it's likely the model or its "
                                 f"settings, not bad luck. Re-check supports, adhesion, and orientation before reprinting."})

    # 3. Dominant failure cause.
    top_cause = None
    if fails:
        cause, ccount = Counter(j.get("status") for j in fails).most_common(1)[0]
        top_cause = cause
        if ccount >= 2:
            findings.append({"level": "warn" if worst == "ok" else worst,
                             "text": f"Most common failure: {_CAUSE_LABEL.get(cause, cause)} ({ccount}×)."})

    # 4. Recent streak — consecutive failures at the top of the (newest-first) list.
    streak = 0
    for j in finished:
        if j.get("status") in _FAILURE_STATES:
            streak += 1
        else:
            break
    if streak >= 2:
        bump("risk")
        findings.append({"level": "risk",
                         "text": f"Your last {streak} prints in a row failed — check the printer itself "
                                 f"(nozzle, bed level, filament) before starting another long print."})

    overall_text = {
        "ok": "Your print history looks healthy.",
        "warn": "A pattern worth addressing in your recent prints (see below).",
        "risk": "Repeated recent failures — worth a look before the next print.",
    }[worst]

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "overall_level": worst,
        "overall_text": overall_text,
        "total": n,
        "failed": fcount,
        "failure_rate": round(rate, 2),
        "recent_failure_streak": streak,
        "top_cause": top_cause,
        "repeat_offenders": repeat_offenders,
        "findings": findings,
    }
