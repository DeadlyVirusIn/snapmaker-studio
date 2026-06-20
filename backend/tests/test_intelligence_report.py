"""Studio Intelligence Report — the one screen that makes the Doctors a product.

Synthesises every Doctor's output into a single verdict a user grasps in 15s:
will it print, what it costs, what to sell it for, the profit, the biggest risk,
and the next action. The Doctors become evidence behind one Studio Intelligence
Score. Pure synthesis over already-computed dicts — no network here.
"""
from snapstudio_core import intelligence_report as ir


def test_unavailable_with_nothing():
    out = ir.build()
    assert out["available"] is False


def test_headline_from_success_and_health():
    out = ir.build(
        predict={"available": True, "likelihood": 80, "band": "likely", "factors": []},
        health={"available": True, "score": 90, "grade": "A", "drivers": []},
    )
    assert out["available"] is True
    # composite of success (80) and printer health (90)
    assert 80 <= out["studio_score"] <= 90
    assert out["print_success_score"] == 80
    assert out["printer_compatibility"] in ("Compatible", "Check", "Unknown")


def test_money_headline_from_cost_and_profit():
    out = ir.build(
        cost={"available": True, "true_cost": 4.0, "suggested_price": 10.0,
              "margin": 6.0, "margin_pct": 60.0, "currency": "$"},
        profit={"available": True, "profit_per_print": 6.0, "margin_pct": 60.0},
    )
    assert out["cost"] == 4.0
    assert out["suggested_price"] == 10.0
    assert out["margin_pct"] == 60.0


def test_risks_collected_and_biggest_is_highest_severity():
    out = ir.build(
        bed_fit={"available": True, "overall_level": "risk",
                 "findings": [{"level": "risk", "text": "Too big for the bed"}],
                 "fixes": ["Scale to 84%"]},
        mm={"available": True, "overall_level": "warn",
            "findings": [{"level": "warn", "text": "Colour layout needs a swap"}],
            "fixes": ["Remap in Orca"]},
    )
    assert len(out["risks"]) >= 2
    assert out["biggest_risk"]["level"] == "risk"      # risk outranks warn
    assert "bed" in out["biggest_risk"]["text"].lower()
    # recommendations gather the doctors' fixes
    assert any("scale" in r.lower() for r in out["recommendations"])


def test_next_action_when_clean_is_positive():
    out = ir.build(
        predict={"available": True, "likelihood": 100, "band": "likely", "factors": []},
        bed_fit={"available": True, "overall_level": "ok", "findings": [], "fixes": []},
    )
    assert out["biggest_risk"] is None
    assert isinstance(out["next_action"], str) and out["next_action"]


def test_doctors_summarised_as_evidence():
    out = ir.build(
        bed_fit={"available": True, "overall_level": "ok", "findings": [], "fixes": []},
        health={"available": True, "score": 90, "grade": "A", "drivers": []},
    )
    names = [d["doctor"] for d in out["supporting"]]
    assert "Project Doctor" in names
    assert "Printer Doctor" in names
    assert all("status" in d for d in out["supporting"])


def test_headline_questions_present():
    out = ir.build(predict={"available": True, "likelihood": 70, "band": "uncertain", "factors": []})
    for k in ("studio_score", "print_success_score", "cost", "suggested_price",
              "margin_pct", "printer_compatibility", "risks", "biggest_risk",
              "recommendations", "next_action", "supporting", "verdict"):
        assert k in out
