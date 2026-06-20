"""Cost-to-Price Intelligence — true cost + suggested selling price.

Validates the pricing engine that turns a real material weight (and, when known,
the slicer's own print-time estimate) into a full cost breakdown and a suggested
selling price with margin. No slicer, no network — pure compute on given numbers.
"""
from snapstudio_core import pricing


def test_unavailable_without_weight():
    out = pricing.price(grams=None, print_hours=2.0)
    assert out["available"] is False
    assert "reason" in out


def test_material_only_when_no_time():
    # Grams known, no print hours: still priced, but time-based costs are zero
    # and the result says so rather than inventing a duration.
    out = pricing.price(grams=50, print_hours=None, price_per_kg=20.0,
                        labor_rate=0.0, failure_rate_pct=0.0, markup_pct=0.0)
    assert out["available"] is True
    b = out["breakdown"]
    assert b["material"] == 1.0          # 50 g of a $20/kg spool
    assert b["electricity"] == 0.0
    assert b["depreciation"] == 0.0
    assert out["true_cost"] == 1.0
    assert out["time_known"] is False


def test_full_breakdown_and_margin():
    out = pricing.price(
        grams=100, print_hours=5.0,
        price_per_kg=20.0,            # material = 2.00
        power_w=120, electricity_per_kwh=0.20,   # 120*5/1000*0.20 = 0.12
        machine_price=600.0, machine_life_hours=5000,  # 600/5000*5 = 0.60
        labor_hours=0.25, labor_rate=20.0,       # 0.25*20 = 5.00
        failure_rate_pct=5.0,         # 5% of (2.00+0.12) = 0.106
        markup_pct=80.0,
    )
    b = out["breakdown"]
    assert b["material"] == 2.0
    assert b["electricity"] == 0.12
    assert b["depreciation"] == 0.6
    assert b["labor"] == 5.0
    assert b["failure_buffer"] == 0.11           # rounded
    # true cost = 2.0 + 0.12 + 0.6 + 5.0 + 0.106 = 7.826 -> 7.83
    assert out["true_cost"] == 7.83
    # suggested price = 7.826 * 1.8 = 14.0868 -> 14.09
    assert out["suggested_price"] == 14.09
    assert out["currency"] == "$"
    assert out["margin"] > 0
    assert 0 < out["margin_pct"] < 100


def test_marketplace_fee_grosses_up_price():
    # With a marketplace fee, the suggested price must rise so the seller still
    # nets the intended markup after the fee is taken.
    no_fee = pricing.price(grams=100, print_hours=2.0, marketplace_fee_pct=0.0)
    with_fee = pricing.price(grams=100, print_hours=2.0, marketplace_fee_pct=10.0)
    assert with_fee["suggested_price"] > no_fee["suggested_price"]
    assert with_fee["breakdown"]["marketplace_fee"] > 0


def test_u1_defaults_are_sane():
    # Called with only a weight + time, the U1-aware defaults still produce a
    # believable price (no zero, no absurd number).
    out = pricing.price(grams=30, print_hours=1.5)
    assert out["available"] is True
    assert out["true_cost"] > 0
    assert out["suggested_price"] > out["true_cost"]


def test_verdict_is_plain_language():
    out = pricing.price(grams=100, print_hours=5.0)
    assert isinstance(out["verdict"], str) and len(out["verdict"]) > 0
