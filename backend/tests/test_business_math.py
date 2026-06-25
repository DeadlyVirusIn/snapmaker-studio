"""Real business math (beta.17.2): grams x spool_price / spool_weight, packaging, shipping."""
from snapstudio_core import pricing


def test_material_cost_82g_24usd_1kg_is_1_97():
    # spool $24 / 1000 g -> price_per_kg = 24; 82 g used.
    r = pricing.price(82, price_per_kg=24.0)
    assert r["available"]
    assert r["breakdown"]["material"] == 1.97   # 82 * 24 / 1000 = 1.968


def test_spool_weight_changes_cost_per_gram():
    # a 750 g spool at $24 is pricier per gram: price_per_kg = 24/750*1000 = 32.
    r = pricing.price(82, price_per_kg=24.0 / 750.0 * 1000.0)
    assert r["breakdown"]["material"] == round(82 * 24 / 750.0, 2)  # 2.62


def test_changing_spool_price_changes_material():
    a = pricing.price(100, price_per_kg=20.0)["breakdown"]["material"]
    b = pricing.price(100, price_per_kg=40.0)["breakdown"]["material"]
    assert b == round(a * 2, 2)


def test_packaging_adds_to_true_cost():
    base = pricing.price(100, price_per_kg=20.0, markup_pct=0, failure_rate_pct=0)
    pack = pricing.price(100, price_per_kg=20.0, markup_pct=0, failure_rate_pct=0, packaging=1.50)
    assert round(pack["true_cost"] - base["true_cost"], 2) == 1.50
    assert pack["breakdown"]["packaging"] == 1.50


def test_shipping_net_affects_profit():
    # charge buyer $8, costs seller $5 -> +$3 to profit.
    a = pricing.price(100, price_per_kg=20.0)
    b = pricing.price(100, price_per_kg=20.0, shipping_charged=8.0, shipping_cost=5.0)
    assert round(b["margin"] - a["margin"], 2) == 3.0
    assert b["breakdown"]["shipping_net"] == 3.0


def test_no_grams_is_unavailable_not_faked():
    assert pricing.price(None)["available"] is False
    assert pricing.price(0)["available"] is False


def test_no_financial_guarantee_language():
    r = pricing.price(82, price_per_kg=24.0)
    assert "guarantee" not in r["verdict"].lower()
