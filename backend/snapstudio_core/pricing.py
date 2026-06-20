"""Cost-to-Price Intelligence — what a print TRULY costs, and what to sell it for.

Material cost is only part of the story. A real maker's cost includes electricity,
machine wear, labour, and a buffer for failed prints; a real seller adds a margin
and absorbs marketplace fees. No slicer (Orca/Bambu/Prusa) and no host (Fluidd/
OctoPrint) computes this — they stop at "how long / how much filament".

This module turns a REAL material weight (and, when known, the slicer's OWN
print-time estimate already on the U1) into a full cost breakdown and a suggested
selling price with margin. Honest by design: it states what it included, zeroes
the costs it can't know rather than inventing them, and returns unavailable when
there's no weight to work from.
"""
from __future__ import annotations

SCHEMA_VERSION = "pricing/1"

# U1-aware defaults. Each is only a fallback — any value the user configures wins.
DEFAULT_PRICE_PER_KG = 20.0       # a typical 1 kg PLA spool ($)
DEFAULT_POWER_W = 120.0           # average draw of a U1 mid-print (W)
DEFAULT_ELECTRICITY_PER_KWH = 0.20  # a common household rate ($/kWh)
DEFAULT_MACHINE_PRICE = 600.0     # U1 purchase price ($)
DEFAULT_MACHINE_LIFE_HOURS = 5000.0  # expected service life before major wear
DEFAULT_LABOR_HOURS = 0.25        # hands-on time per print (setup + removal)
DEFAULT_LABOR_RATE = 0.0          # off unless the user values their time
DEFAULT_FAILURE_RATE_PCT = 5.0    # buffer on material+energy for failed prints
DEFAULT_MARKUP_PCT = 80.0         # seller margin (typical range 30–100%)
DEFAULT_MARKETPLACE_FEE_PCT = 0.0  # platform cut, grossed up into the price


def price(
    grams,
    print_hours=None,
    *,
    price_per_kg: float = DEFAULT_PRICE_PER_KG,
    currency: str = "$",
    power_w: float = DEFAULT_POWER_W,
    electricity_per_kwh: float = DEFAULT_ELECTRICITY_PER_KWH,
    machine_price: float = DEFAULT_MACHINE_PRICE,
    machine_life_hours: float = DEFAULT_MACHINE_LIFE_HOURS,
    labor_hours: float = DEFAULT_LABOR_HOURS,
    labor_rate: float = DEFAULT_LABOR_RATE,
    failure_rate_pct: float = DEFAULT_FAILURE_RATE_PCT,
    markup_pct: float = DEFAULT_MARKUP_PCT,
    marketplace_fee_pct: float = DEFAULT_MARKETPLACE_FEE_PCT,
    basis: str = "design estimate",
) -> dict:
    """Full cost breakdown + suggested selling price for one print.

    grams: material weight (g) — geometry estimate or the slicer's own metadata.
    print_hours: print duration (h). When None, time-based costs are zeroed and
      `time_known` is False (the result says so rather than guessing a duration).
    """
    if grams is None or grams <= 0:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "no material weight available for this design"}

    ppk = price_per_kg if (price_per_kg and price_per_kg > 0) else DEFAULT_PRICE_PER_KG
    hours = float(print_hours) if (print_hours and print_hours > 0) else 0.0
    time_known = hours > 0

    material = (grams / 1000.0) * ppk
    electricity = (power_w * hours / 1000.0) * electricity_per_kwh
    depreciation = (machine_price / machine_life_hours) * hours if machine_life_hours else 0.0
    labor = labor_hours * labor_rate
    failure_buffer = (failure_rate_pct / 100.0) * (material + electricity)

    true_cost = material + electricity + depreciation + labor + failure_buffer
    pre_fee_price = true_cost * (1.0 + markup_pct / 100.0)

    # Gross up so the seller still nets the markup after the platform takes its cut.
    fee_frac = max(0.0, min(marketplace_fee_pct / 100.0, 0.95))
    suggested_price = pre_fee_price / (1.0 - fee_frac) if fee_frac else pre_fee_price
    marketplace_fee = suggested_price * fee_frac

    profit = suggested_price - true_cost - marketplace_fee
    margin_pct = (profit / suggested_price * 100.0) if suggested_price > 0 else 0.0

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "time_known": time_known,
        "grams": round(float(grams), 1),
        "print_hours": round(hours, 2) if time_known else None,
        "currency": currency or "$",
        "breakdown": {
            "material": round(material, 2),
            "electricity": round(electricity, 2),
            "depreciation": round(depreciation, 2),
            "labor": round(labor, 2),
            "failure_buffer": round(failure_buffer, 2),
            "marketplace_fee": round(marketplace_fee, 2),
        },
        "true_cost": round(true_cost, 2),
        "markup_pct": round(float(markup_pct), 1),
        "suggested_price": round(suggested_price, 2),
        "margin": round(profit, 2),
        "margin_pct": round(margin_pct, 1),
        "basis": basis,
        "verdict": _verdict(round(true_cost, 2), round(suggested_price, 2),
                            round(profit, 2), currency or "$", time_known),
    }


def _verdict(cost: float, price_: float, profit: float, currency: str,
             time_known: bool) -> str:
    """One plain-language line a novice can act on."""
    tail = "" if time_known else " (material + margin only — no print time known yet)"
    return (f"Costs about {currency}{cost:.2f} to make; sell around "
            f"{currency}{price_:.2f} for ~{currency}{profit:.2f} profit.{tail}")


def aggregate(items) -> dict:
    """Business Mode: roll a batch of priced parts into one job P&L.

    items: a list of price() results. Unavailable parts are skipped (a missing
    weight for one model never voids the whole batch). Returns unavailable only
    when nothing in the batch could be priced.
    """
    priced = [i for i in (items or []) if i and i.get("available")]
    n = len(priced)
    if n == 0:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "no priceable parts in this batch"}

    currency = priced[0].get("currency") or "$"
    total_cost = sum(i.get("true_cost", 0.0) for i in priced)
    total_price = sum(i.get("suggested_price", 0.0) for i in priced)
    total_profit = sum(i.get("margin", 0.0) for i in priced)
    total_grams = sum(i.get("grams", 0.0) for i in priced)
    margin_pct = (total_profit / total_price * 100.0) if total_price > 0 else 0.0
    any_time_unknown = any(not i.get("time_known") for i in priced)

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "parts": n,
        "currency": currency,
        "total_grams": round(total_grams, 1),
        "total_cost": round(total_cost, 2),
        "total_price": round(total_price, 2),
        "total_profit": round(total_profit, 2),
        "margin_pct": round(margin_pct, 1),
        "avg_price": round(total_price / n, 2),
        "time_known": not any_time_unknown,
        "verdict": (f"{n} part{'s' if n != 1 else ''}: ~{currency}{total_cost:.2f} to make, "
                    f"sell for ~{currency}{total_price:.2f} → ~{currency}{total_profit:.2f} profit"
                    f"{'' if not any_time_unknown else ' (material + margin only)'}."),
    }
