import { describe, it, expect } from "vitest";
import { bizFactors, BIZ_DEFAULTS } from "./business";

describe("bizFactors — user assumptions map to backend factor keys", () => {
  it("forwards the user filament price (not a default)", () => {
    expect(bizFactors(BIZ_DEFAULTS, 35).price_per_kg).toBe(35);
    expect(bizFactors(BIZ_DEFAULTS, 12.5).price_per_kg).toBe(12.5);
  });

  it("maps every editable assumption to its snake_case key", () => {
    const a = { ...BIZ_DEFAULTS, marketplaceFeePct: 7, markupPct: 120, failureRatePct: 10, laborRate: 25 };
    const f = bizFactors(a, 20);
    expect(f.marketplace_fee_pct).toBe(7);
    expect(f.markup_pct).toBe(120);
    expect(f.failure_rate_pct).toBe(10);
    expect(f.labor_rate).toBe(25);
    expect(f.electricity_per_kwh).toBe(BIZ_DEFAULTS.electricityPerKwh);
    expect(f.machine_price).toBe(BIZ_DEFAULTS.machinePrice);
  });

  it("emits only backend-supported keys (no fabricated factors)", () => {
    const keys = Object.keys(bizFactors(BIZ_DEFAULTS, 20)).sort();
    expect(keys).toEqual([
      "electricity_per_kwh", "failure_rate_pct", "labor_hours", "labor_rate",
      "machine_life_hours", "machine_price", "marketplace_fee_pct", "markup_pct",
      "packaging", "power_w", "price_per_kg", "shipping_charged", "shipping_cost",
    ]);
  });

  it("derives price/kg from spool price and spool weight", () => {
    // $24 spool, 1000 g -> 24/kg; same $24 on a 750 g spool -> 32/kg.
    expect(bizFactors({ ...BIZ_DEFAULTS, spoolWeightG: 1000 }, 24).price_per_kg).toBe(24);
    expect(bizFactors({ ...BIZ_DEFAULTS, spoolWeightG: 750 }, 24).price_per_kg).toBe(32);
  });

  it("only sends grams_override when the user entered a weight", () => {
    expect("grams_override" in bizFactors(BIZ_DEFAULTS, 20)).toBe(false);
    expect(bizFactors({ ...BIZ_DEFAULTS, gramsOverride: 82 }, 20).grams_override).toBe(82);
  });
});
