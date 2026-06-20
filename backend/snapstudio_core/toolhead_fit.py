"""Toolhead-Fit Intelligence — does this design's colour count fit the U1's toolheads?

Fuses the design's filament/colour count with the printer's REAL toolhead count
(from Moonraker when reachable, else the U1's known 4) into one plain-language
answer: "Can my printer print all these colours in a single run, or will it need
a filament swap / remap?" Pure + read-only; the service layer gathers the inputs.

This is insight, not telemetry: it turns two numbers the user already has into a
clear go / plan-a-swap recommendation, and never fabricates swap counts or times.
"""
from __future__ import annotations

SCHEMA_VERSION = "toolheadfit/1"

# The Snapmaker U1 ships with 4 independent toolheads (klipper extruder objects:
# extruder, extruder1, extruder2, extruder3). Used as the fallback when no printer
# is connected so the insight still works offline.
U1_TOOLHEADS = 4


def _f(level: str, text: str) -> dict:
    return {"level": level, "text": text}


def assess(color_count, toolhead_count=None, printer_known: bool = False) -> dict:
    """Return toolhead-fit findings.

    color_count: distinct filament/colour slots the design uses (int or None).
    toolhead_count: real toolhead count from a connected printer (int) or None.
    printer_known: True when toolhead_count came from a reachable printer.
    """
    heads = int(toolhead_count) if toolhead_count else U1_TOOLHEADS
    source = "your connected U1" if printer_known else "the U1"
    findings: list = []
    worst = "ok"

    def bump(level: str) -> None:
        nonlocal worst
        order = {"ok": 0, "warn": 1, "risk": 2}
        if order[level] > order[worst]:
            worst = level

    if color_count is None:
        return {
            "schema_version": SCHEMA_VERSION,
            "available": False,
            "reason": "colour count unavailable",
            "printer_aware": printer_known,
            "toolhead_count": heads,
        }

    n = int(color_count)
    if n <= 1:
        findings.append(_f("ok", f"Single colour — prints on any one of {source}'s {heads} toolheads, no colour setup needed."))
    elif n <= heads:
        spare = heads - n
        spare_txt = f" ({spare} toolhead{'' if spare == 1 else 's'} to spare)" if spare > 0 else ""
        findings.append(_f("ok", f"Uses {n} colours and {source} has {heads} toolheads{spare_txt} — load one filament per colour and it prints in a single run."))
    else:
        over = n - heads
        bump("risk")
        findings.append(_f("risk", f"This design uses {n} colours but {source} has only {heads} toolheads — {over} colour{'' if over == 1 else 's'} can't be loaded at the same time."))
        findings.append(_f("warn", f"To print it as designed, swap filament mid-print (pause-and-swap), or remap it down to {heads} colours in your slicer. Either way Studio keeps all {n} original colours in the file."))

    overall_text = {
        "ok": "Your toolheads cover this design's colours.",
        "warn": "Workable with a filament swap or remap (see below).",
        "risk": "More colours than toolheads — plan a swap or remap before printing.",
    }[worst]
    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "printer_aware": printer_known,
        "color_count": n,
        "toolhead_count": heads,
        "overall_level": worst,
        "overall_text": overall_text,
        "findings": findings,
    }
