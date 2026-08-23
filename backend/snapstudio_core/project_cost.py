"""Project cost — real numbers when the file has them, honesty when it does not.

Most cost estimates in 3D printing are guesses dressed up as figures: a volume
times a density times a price. Studio prefers a better source when one exists.

A project 3MF that has been sliced records what the author's own slicer actually
computed — per plate, the predicted print time and material weight, and per
filament slot, the grams and metres used. That is the output of a real slicing
run. When it is in the file, Studio uses it and says so. When it is not, Studio
says the project has not been sliced yet rather than inventing a number.

This is the difference between "roughly $2.40, probably" and "$2.41 for plate 1,
from the slicing result stored in this project, 78 g across two materials".
"""
from __future__ import annotations

SCHEMA_VERSION = "projectcost/1"

DEFAULT_PRICE_PER_KG = 20.0

# What the "basis" field can say. The UI shows this verbatim so a user always
# knows whether they are looking at a measurement or an estimate.
BASIS_SLICED = "the slicing result stored in this project"
BASIS_NONE = "not available"


def _positive(value):
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if f > 0 else None


def _price_for(material: str | None, prices: dict | None, default: float) -> float:
    """Per-material price when the user configured one, else their single price."""
    if prices and material:
        for key, value in prices.items():
            if str(key).strip().upper() == str(material).strip().upper():
                got = _positive(value)
                if got:
                    return got
    return default


def _plate_cost(plate: dict, price_per_kg: float, prices: dict | None) -> dict:
    filaments = []
    filament_total_g = 0.0
    cost_total = 0.0
    for f in plate.get("filaments") or []:
        grams = _positive(f.get("used_g"))
        if grams is None:
            continue
        material = f.get("type")
        unit_price = _price_for(material, prices, price_per_kg)
        cost = (grams / 1000.0) * unit_price
        filament_total_g += grams
        cost_total += cost
        filaments.append({
            "slot": f.get("id"),
            "material": material,
            "color": f.get("color"),
            "grams": round(grams, 1),
            "metres": round(_positive(f.get("used_m")) or 0.0, 2),
            "price_per_kg": round(unit_price, 2),
            "cost": round(cost, 2),
        })

    # The plate's own recorded weight is the authority; the per-slot grams are a
    # breakdown of it. If they disagree, report the recorded weight and let the
    # breakdown explain where it went, rather than silently preferring one.
    recorded_g = _positive(plate.get("predicted_weight_g"))
    grams = recorded_g if recorded_g is not None else (filament_total_g or None)
    seconds = _positive(plate.get("predicted_seconds"))

    return {
        "index": plate.get("index"),
        "grams": round(grams, 1) if grams else None,
        "seconds": int(seconds) if seconds else None,
        "hours": round(seconds / 3600.0, 2) if seconds else None,
        "cost": round(cost_total, 2) if cost_total else None,
        "filaments": filaments,
        "material_count": len(filaments),
    }


def from_traits(traits: dict, price_per_kg: float = DEFAULT_PRICE_PER_KG,
                currency: str = "$", prices: dict | None = None) -> dict:
    """Cost for a project, computed from its own recorded slicing result.

    ``traits`` is the dict from ``project_traits.extract``. ``prices`` optionally
    maps a material name (``"PLA"``, ``"PETG"``) to a price per kg, so a plate
    that mixes an expensive support material with cheap PLA is costed correctly.
    """
    unit_price = _positive(price_per_kg) or DEFAULT_PRICE_PER_KG
    plates_raw = (traits or {}).get("plate_predictions") or []

    plates = [_plate_cost(p, unit_price, prices) for p in plates_raw]
    priced = [p for p in plates if p["cost"] is not None]

    if not priced:
        sliced = ((traits or {}).get("is_sliced") or {}).get("value")
        if sliced:
            reason = ("This project is sliced, but it does not record how much "
                      "material each plate uses, so Studio has no real weight to "
                      "cost. Enter your own estimate, or re-slice it in Snapmaker "
                      "Orca and open the saved project again.")
        else:
            reason = ("This project has not been sliced yet, so no real material "
                      "figure exists in the file. Slice it in Snapmaker Orca and "
                      "open the saved project again, or enter your own estimate.")
        return {
            "schema_version": SCHEMA_VERSION,
            "available": False,
            "basis": BASIS_NONE,
            "reason": reason,
            "plates": [],
        }

    total_grams = sum(p["grams"] or 0.0 for p in priced)
    total_cost = sum(p["cost"] or 0.0 for p in priced)
    total_seconds = sum(p["seconds"] or 0 for p in priced)
    known_time = all(p["seconds"] for p in priced)

    materials: dict[str, dict] = {}
    for plate in priced:
        for f in plate["filaments"]:
            name = f["material"] or "unknown material"
            entry = materials.setdefault(name, {"material": name, "grams": 0.0, "cost": 0.0})
            entry["grams"] += f["grams"]
            entry["cost"] += f["cost"]
    by_material = sorted(
        ({"material": m["material"], "grams": round(m["grams"], 1),
          "cost": round(m["cost"], 2)} for m in materials.values()),
        key=lambda m: m["cost"], reverse=True)

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "basis": BASIS_SLICED,
        "currency": currency or "$",
        "price_per_kg": round(unit_price, 2),
        "plate_count": len(priced),
        "grams": round(total_grams, 1),
        "cost": round(total_cost, 2),
        "seconds": int(total_seconds) if known_time else None,
        "hours": round(total_seconds / 3600.0, 2) if known_time else None,
        "time_known": known_time,
        "plates": plates,
        "by_material": by_material,
        "summary": _summary(len(priced), total_grams, total_cost, total_seconds,
                            known_time, by_material, currency or "$"),
        "disclaimer": ("Material cost only, from the figures the slicer recorded in "
                       "this file. It does not include electricity, machine wear, "
                       "labour or failed prints — the Cost & Pricing Doctor adds "
                       "those from your own numbers."),
    }


def _summary(plate_count: int, grams: float, cost: float, seconds: float,
             time_known: bool, by_material: list[dict], currency: str) -> str:
    plate_txt = "plate" if plate_count == 1 else "plates"
    parts = [f"{plate_count} {plate_txt}", f"{grams:.0f} g", f"{currency}{cost:.2f} of filament"]
    if time_known and seconds:
        parts.append(f"{seconds / 3600.0:.1f} h of printing")
    if len(by_material) > 1:
        parts.append(f"{len(by_material)} materials")
    return ", ".join(parts) + " — from this project's own slicing result."


def estimate(path: str, price_per_kg: float = DEFAULT_PRICE_PER_KG,
             currency: str = "$", prices: dict | None = None) -> dict:
    """Read a project file and cost it. Never raises."""
    from . import project_traits

    return from_traits(project_traits.extract(path), price_per_kg=price_per_kg,
                       currency=currency, prices=prices)
