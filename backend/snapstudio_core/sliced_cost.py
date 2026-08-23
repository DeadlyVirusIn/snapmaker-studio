"""Cost a job from what the slicer actually measured, not from an estimate.

Studio's existing Cost Doctor reads a *project* and works from whatever figures it
carries — often none, in which case it says so rather than inventing a number.
Once a file has been sliced, that guessing stops being necessary: the slicer wrote
down grams per slot and a print-time estimate, and those are measurements.

What this deliberately does **not** do is split that filament into model, support
and purge. Snapmaker Orca's summary reports one total per slot. Dividing it by a
plausible-looking ratio would produce a number that looks more precise and is less
true, so where the file does not separate them, neither does this.

Every line carries where it came from:

* ``measured``    — the slicer wrote this figure into the file
* ``derived``     — arithmetic on measured figures and the user's own prices
* ``assumption``  — a default the user can change
* ``unknown``     — not stated, and not guessed
"""
from __future__ import annotations

from .pricing import (
    DEFAULT_ELECTRICITY_PER_KWH, DEFAULT_LABOR_HOURS, DEFAULT_LABOR_RATE,
    DEFAULT_MACHINE_LIFE_HOURS, DEFAULT_MACHINE_PRICE, DEFAULT_POWER_W,
    DEFAULT_PRICE_PER_KG,
)

SCHEMA_VERSION = "slicedcost/1"

MEASURED = "measured"
DERIVED = "derived"
ASSUMPTION = "assumption"
UNKNOWN = "unknown"


def _line(label: str, amount: float | None, evidence: str, source: str,
          detail: str | None = None) -> dict:
    return {
        "label": label,
        "amount": None if amount is None else round(amount, 4),
        "evidence": evidence,
        "source": source,
        "detail": detail,
    }


def estimate(gcode_facts: dict, *,
             price_per_kg: float = DEFAULT_PRICE_PER_KG,
             prices: dict | None = None,
             currency: str = "$",
             power_w: float = DEFAULT_POWER_W,
             electricity_per_kwh: float = DEFAULT_ELECTRICITY_PER_KWH,
             machine_price: float = DEFAULT_MACHINE_PRICE,
             machine_life_hours: float = DEFAULT_MACHINE_LIFE_HOURS,
             labor_hours: float = DEFAULT_LABOR_HOURS,
             labor_rate: float = DEFAULT_LABOR_RATE) -> dict:
    """Cost a sliced job. Never raises; missing figures stay missing."""
    if not gcode_facts.get("available"):
        return {
            "schema_version": SCHEMA_VERSION,
            "available": False,
            "summary": gcode_facts.get("error", "Studio could not read that G-code file."),
        }

    filament = gcode_facts.get("filament") or {}
    slots = gcode_facts.get("slots") or []
    seconds = gcode_facts.get("estimated_seconds")
    hours = (seconds / 3600.0) if seconds else None

    per_slot = []
    material_cost = 0.0
    have_material = False
    for slot in slots:
        grams = slot.get("grams")
        if grams is None or grams <= 0:
            continue
        have_material = True
        material = slot.get("type")
        rate = (prices or {}).get(material or "", price_per_kg) if prices else price_per_kg
        cost = grams / 1000.0 * float(rate)
        material_cost += cost
        per_slot.append({
            "tool": slot["tool"],
            "material": material,
            "name": slot.get("name"),
            "grams": grams,
            "mm": slot.get("mm"),
            "price_per_kg": float(rate),
            "cost": round(cost, 4),
            "source": MEASURED,
        })

    total_grams = filament.get("total_g")
    if total_grams is None and have_material:
        total_grams = round(sum(s["grams"] for s in per_slot), 3)

    lines = []
    if have_material:
        lines.append(_line(
            "Filament", material_cost,
            f"{total_grams:g} g measured by the slicer, across {len(per_slot)} slot(s)",
            DERIVED,
            "grams come from the file; the price per kilogram is yours to set"))
    else:
        lines.append(_line(
            "Filament", None,
            "the file does not state how much filament the job uses",
            UNKNOWN))

    if hours:
        energy = power_w / 1000.0 * hours * electricity_per_kwh
        lines.append(_line(
            "Electricity", energy,
            f"{hours:.2f} h at {power_w:g} W and {currency}{electricity_per_kwh:g}/kWh",
            DERIVED,
            "print time is measured by the slicer; the power draw and rate are assumptions you can change"))

        wear = (machine_price / machine_life_hours) * hours if machine_life_hours else None
        lines.append(_line(
            "Machine wear", wear,
            f"{hours:.2f} h of a {currency}{machine_price:g} machine over {machine_life_hours:g} h",
            ASSUMPTION))
    else:
        lines.append(_line("Electricity", None,
                           "the file does not state an estimated print time", UNKNOWN))
        lines.append(_line("Machine wear", None,
                           "the file does not state an estimated print time", UNKNOWN))

    labour = labor_hours * labor_rate if labor_rate else 0.0
    lines.append(_line(
        "Your time", labour,
        (f"{labor_hours:g} h at {currency}{labor_rate:g}/h" if labor_rate
         else "not counted — set an hourly rate to include it"),
        ASSUMPTION))

    known = [line["amount"] for line in lines if line["amount"] is not None]
    total = round(sum(known), 4) if known else None
    incomplete = [line["label"] for line in lines if line["amount"] is None]

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "currency": currency,
        "per_slot": per_slot,
        "total_grams": total_grams,
        "print_seconds": seconds,
        "lines": lines,
        "total": total,
        "incomplete": incomplete,
        "waste": _waste(gcode_facts, per_slot),
        "summary": _summary(currency, total, total_grams, seconds, incomplete),
    }


def _waste(gcode_facts: dict, per_slot: list) -> dict:
    """What can be said about waste — which, for this slicer, is mostly 'not separable'."""
    purge = gcode_facts.get("purge") or {}
    if not purge.get("expected"):
        return {
            "separable": False,
            "expected": False,
            "detail": "Single-tool job: no tool-change purge, so the filament figure is all print.",
            "source": MEASURED,
        }
    return {
        "separable": False,
        "expected": True,
        "prime_tower": purge.get("prime_tower"),
        "detail": ("This job changes tools, so part of the filament above is purged rather than "
                   "printed. The slicer reports one total per slot and does not separate them, so "
                   "Studio will not split the number — the total is right, the breakdown is not "
                   "available from this file."),
        "source": UNKNOWN,
    }


def _summary(currency: str, total: float | None, grams, seconds, incomplete: list) -> str:
    if total is None:
        return "Studio could not cost this job — the file states none of the figures it needs."
    bits = [f"About {currency}{total:.2f}"]
    if grams:
        bits.append(f"for {grams:g} g")
    if seconds:
        bits.append(f"and {seconds // 3600}h {(seconds % 3600) // 60}m of printing")
    text = " ".join(bits)
    if incomplete:
        text += f", not counting {', '.join(i.lower() for i in incomplete)} — the file does not state it"
    return text + "."
