"""Studio Intelligence Report — the Doctors become evidence, the Report is the product.

Every Doctor answers one question. A user shouldn't have to read seven cards to
know where they stand. This synthesises them into a single screen's worth of
answer: a Studio Intelligence Score, the money headline, the biggest risk, and
the one next action — with each Doctor's finding as supporting evidence.

Pure synthesis over already-computed Doctor dicts (no network, no fabrication):
it scores only what's present, surfaces real findings, and stays honest about
what it can't yet see.
"""
from __future__ import annotations

SCHEMA_VERSION = "report/1"

_ORDER = {"ok": 0, "warn": 1, "risk": 2}
_LEVEL_SCORE = {"ok": 100, "warn": 70, "risk": 40}


def _push_findings(risks, recs, doctor, doc):
    """Collect a doctor's non-ok findings as risks and its fixes as recommendations."""
    if not doc or not doc.get("available", True):
        return
    for f in (doc.get("findings") or []):
        if f.get("level") in ("warn", "risk"):
            risks.append({"doctor": doctor, "level": f["level"], "text": f["text"]})
    for fx in (doc.get("fixes") or []):
        recs.append(fx)


def build(predict=None, bed_fit=None, mm=None, first_layer=None, health=None,
          cost=None, pricing=None, profit=None) -> dict:
    """Combine the Doctors into one report. All inputs are their build() outputs."""
    avail = {
        "predict": bool(predict and predict.get("available")),
        "bed_fit": bool(bed_fit and bed_fit.get("available")),
        "mm": bool(mm and mm.get("available")),
        "first_layer": bool(first_layer and first_layer.get("overall_level")),
        "health": bool(health and health.get("available")),
        "cost": bool(cost and cost.get("available")),
        "pricing": bool(pricing and pricing.get("available")),
        "profit": bool(profit and profit.get("available")),
    }
    if not any(avail.values()):
        return {"schema_version": SCHEMA_VERSION, "available": False,
                "reason": "no Doctor results available to report on"}

    cur = (cost or {}).get("currency") or (pricing or {}).get("currency") or "$"

    # --- headline scores ---
    success = predict.get("likelihood") if avail["predict"] else None
    health_score = health.get("score") if avail["health"] else None

    # Studio Intelligence Score: blend print-success and printer-health when both
    # are known; otherwise lean on whichever exists, then on the doctors' levels.
    comp = []
    if success is not None:
        comp.append((success, 0.6))
    if health_score is not None:
        comp.append((health_score, 0.4))
    if comp:
        wsum = sum(w for _, w in comp)
        studio_score = round(sum(v * w for v, w in comp) / wsum)
    else:
        worst = "ok"
        for d in (bed_fit, mm, first_layer):
            lvl = (d or {}).get("overall_level")
            if lvl and _ORDER[lvl] > _ORDER[worst]:
                worst = lvl
        studio_score = _LEVEL_SCORE[worst] if any([avail["bed_fit"], avail["mm"], avail["first_layer"]]) else None

    # --- money headline ---
    money = cost or {}
    cost_v = money.get("true_cost") if avail["cost"] else None
    price_v = money.get("suggested_price") if avail["cost"] else None
    margin_pct = (profit.get("margin_pct") if avail["profit"] else money.get("margin_pct")) if (avail["profit"] or avail["cost"]) else None
    profit_v = profit.get("profit_per_print") if avail["profit"] else (money.get("margin") if avail["cost"] else None)

    # --- printer compatibility ---
    if avail["health"]:
        compatibility = "Compatible" if (health_score or 0) >= 60 else "Check"
    else:
        compatibility = "Unknown"   # no printer connected; design-only signals

    # --- risks + recommendations from every doctor ---
    risks: list = []
    recs: list = []
    _push_findings(risks, recs, "Project Doctor", bed_fit)
    _push_findings(risks, recs, "Multi-Material Doctor", mm)
    _push_findings(risks, recs, "First Layer Doctor", first_layer)
    if avail["health"]:
        for d in (health.get("drivers") or []):
            if "no problem" not in d.lower():
                risks.append({"doctor": "Printer Doctor", "level": "warn", "text": d})
    if avail["predict"]:
        for f in (predict.get("factors") or []):
            if "no risk" not in f.lower():
                risks.append({"doctor": "Project Doctor", "level": "warn", "text": f})
    if avail["profit"] and (profit.get("profit_per_print") or 0) <= 0:
        risks.append({"doctor": "Profit Doctor", "level": "warn",
                      "text": "Priced below cost — not profitable as-is."})
        recs.append("Raise the price or cut cost before selling.")

    # dedup, severity-sort
    seen = set()
    risks = [r for r in risks if not (r["text"] in seen or seen.add(r["text"]))]
    risks.sort(key=lambda r: _ORDER.get(r["level"], 0), reverse=True)
    seen_r = set()
    recommendations = [r for r in recs if not (r in seen_r or seen_r.add(r))]

    biggest_risk = risks[0] if risks else None

    # --- the one next action ---
    if biggest_risk:
        next_action = recommendations[0] if recommendations else f"Address: {biggest_risk['text']}"
    elif avail["cost"] and price_v:
        next_action = f"Looks good — prepare it and sell around {cur}{price_v}."
    else:
        next_action = "Looks good — prepare it for your U1 and print."

    # --- supporting evidence (each Doctor's one-line status) ---
    supporting = []

    def add(name, ok, status, detail):
        if ok:
            supporting.append({"doctor": name, "status": status, "detail": detail})

    _lvl_status = {"ok": "Validated", "warn": "Check", "risk": "Action needed"}
    add("Project Doctor", avail["bed_fit"], _lvl_status.get((bed_fit or {}).get("overall_level"), "—"),
        (bed_fit or {}).get("overall_text", ""))
    add("Multi-Material Doctor", avail["mm"], _lvl_status.get((mm or {}).get("overall_level"), "—"),
        (mm or {}).get("overall_text", ""))
    add("First Layer Doctor", avail["first_layer"], _lvl_status.get((first_layer or {}).get("overall_level"), "—"),
        (first_layer or {}).get("overall_text", ""))
    add("Printer Doctor", avail["health"], f"{(health or {}).get('grade','')} · {health_score}/100" if avail["health"] else "—",
        (health or {}).get("verdict", ""))
    add("Cost Doctor", avail["cost"], f"{cur}{cost_v}" if cost_v is not None else "—",
        "True cost to make.")
    add("Pricing Doctor", avail["pricing"], (pricing or {}).get("verdict", ""), "Hobby / Marketplace / Premium tiers.")
    add("Profit Doctor", avail["profit"], f"{cur}{profit_v}/print" if profit_v is not None else "—",
        (profit or {}).get("verdict", ""))

    # --- one-line verdict ---
    bits = []
    if studio_score is not None:
        bits.append(f"Studio score {studio_score}/100")
    if price_v is not None:
        bits.append(f"sell ~{cur}{price_v}")
    if biggest_risk:
        bits.append(f"top risk: {biggest_risk['text']}")
    verdict = "; ".join(bits) + "." if bits else "Report ready."

    return {
        "schema_version": SCHEMA_VERSION,
        "available": True,
        "studio_score": studio_score,
        "print_success_score": success,
        "cost": cost_v,
        "suggested_price": price_v,
        "margin_pct": margin_pct,
        "profit_per_print": profit_v,
        "currency": cur,
        "printer_compatibility": compatibility,
        "risks": risks,
        "biggest_risk": biggest_risk,
        "recommendations": recommendations,
        "next_action": next_action,
        "supporting": supporting,
        "verdict": verdict,
    }
