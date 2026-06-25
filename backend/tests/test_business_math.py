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


def test_manual_print_hours_drives_electricity_and_machine_cost():
    none = pricing.price(100, None, power_w=120, electricity_per_kwh=0.20,
                         machine_price=600, machine_life_hours=5000)
    assert none["breakdown"]["electricity"] == 0.0 and none["time_known"] is False
    two = pricing.price(100, 2.0, power_w=120, electricity_per_kwh=0.20,
                        machine_price=600, machine_life_hours=5000)
    assert two["time_known"] is True
    assert two["breakdown"]["electricity"] == round(120 * 2 / 1000 * 0.20, 2)   # 0.05
    assert two["breakdown"]["depreciation"] == round(600 / 5000 * 2, 2)          # 0.24


def test_material_density_scales_volume_grams():
    # service-level: estimate grams from a real STL, then re-base by material density.
    from pathlib import Path
    from snapstudio_api import service
    stl = Path(__file__).resolve().parents[2] / "examples" / "sample_cube.stl"
    if not stl.exists():
        import pytest; pytest.skip("sample STL absent")
    pla = service.cost_to_price(str(stl), None, None, 7125, "$", material_density=1.24)
    petg = service.cost_to_price(str(stl), None, None, 7125, "$", material_density=1.27)
    if not pla.get("available"):
        import pytest; pytest.skip("no geometry grams estimate")
    # denser PETG -> more grams from the same volume.
    assert petg["grams"] > pla["grams"]
    assert "density" in petg["basis"]
    # manual grams override beats density.
    over = service.cost_to_price(str(stl), None, None, 7125, "$", material_density=1.27, grams_override=82)
    assert over["grams"] == 82.0 and over["basis"] == "your entered weight"
