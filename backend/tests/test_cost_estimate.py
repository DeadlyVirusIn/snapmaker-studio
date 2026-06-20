"""Material Cost Estimation — pure grams x price logic."""
from snapstudio_core import cost_estimate as ce


def test_no_weight_unavailable():
    assert ce.estimate(None)["available"] is False
    assert ce.estimate(0)["available"] is False


def test_basic_cost_math():
    out = ce.estimate(100, price_per_kg=20.0)
    assert out["available"] is True
    assert out["grams"] == 100.0
    assert out["cost"] == 2.0  # 0.1 kg * $20
    assert out["currency"] == "$"


def test_custom_price_and_currency():
    out = ce.estimate(250, price_per_kg=30.0, currency="€")
    assert out["cost"] == 7.5  # 0.25 kg * 30
    assert out["currency"] == "€"
    assert out["price_per_kg"] == 30.0


def test_nonpositive_price_falls_back_to_default():
    out = ce.estimate(1000, price_per_kg=0)
    assert out["price_per_kg"] == ce.DEFAULT_PRICE_PER_KG
    assert out["cost"] == round(ce.DEFAULT_PRICE_PER_KG, 2)  # 1 kg at default


def test_basis_passthrough():
    out = ce.estimate(50, basis="slicer metadata")
    assert out["basis"] == "slicer metadata"
