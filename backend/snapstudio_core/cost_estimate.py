"""Material Cost Estimation — real grams x the user's filament price.

Turns a REAL material-weight estimate (from design geometry, or the slicer's own
metadata already on the printer) into an at-a-glance filament cost. Honest by
design: it states the basis, uses the weight it's given, and returns unavailable
rather than inventing a number when there's no weight to work from.
"""
from __future__ import annotations

SCHEMA_VERSION = "cost/1"

# A typical 1 kg PLA spool. Only a fallback — the user's configured price wins.
DEFAULT_PRICE_PER_KG = 20.0


def estimate(grams, price_per_kg: float = DEFAULT_PRICE_PER_KG,
             currency: str = "$", basis: str = "design estimate") -> dict:
    """Filament cost for a print.

    grams: material weight (g) — from geometry estimate or slicer metadata.
    price_per_kg: the user's filament price; falls back to a typical PLA spool.
    basis: human-readable source of the weight (shown so the user knows what it is).
    """
    if grams is None or grams <= 0:
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "no material weight available for this design"}
    price = price_per_kg if (price_per_kg and price_per_kg > 0) else DEFAULT_PRICE_PER_KG
    cost = (grams / 1000.0) * price
    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "grams": round(float(grams), 1),
        "price_per_kg": round(float(price), 2),
        "currency": currency or "$",
        "cost": round(cost, 2),
        "basis": basis,
    }
