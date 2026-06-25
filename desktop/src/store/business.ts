import { create } from "zustand";

// Editable "Material & business assumptions" for the Cost/Pricing/Profit Doctors.
// Persisted locally (no cloud, no account). These map 1:1 to backend factor keys the
// pricing engine already accepts; filament price + currency live in the filament store.
// Defaults are beginner-friendly *assumptions*, not measured values.
export interface BizAssumptions {
  electricityPerKwh: number;  // electricity_per_kwh
  powerW: number;             // power_w (printer draw)
  machinePrice: number;       // machine_price (for depreciation)
  machineLifeHours: number;   // machine_life_hours
  laborHours: number;         // labor_hours per print
  laborRate: number;          // labor_rate ($/hr; 0 = off)
  failureRatePct: number;     // failure_rate_pct (waste/failed-print buffer)
  marketplaceFeePct: number;  // marketplace_fee_pct
  markupPct: number;          // markup_pct (margin)
}

const DEFAULTS: BizAssumptions = {
  electricityPerKwh: 0.20, powerW: 120, machinePrice: 600, machineLifeHours: 5000,
  laborHours: 0.25, laborRate: 0, failureRatePct: 5, marketplaceFeePct: 0, markupPct: 80,
};

const KEY = "businessAssumptions";

function load(): BizAssumptions {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) return { ...DEFAULTS, ...JSON.parse(raw) };
  } catch { /* ignore bad json */ }
  return { ...DEFAULTS };
}

interface BizState extends BizAssumptions {
  set: (patch: Partial<BizAssumptions>) => void;
  reset: () => void;
}

export const useBusiness = create<BizState>((set, get) => ({
  ...load(),
  set: (patch) => {
    const next = stripFns({ ...get(), ...patch } as BizAssumptions);
    try { localStorage.setItem(KEY, JSON.stringify(next)); } catch { /* ignore */ }
    set(patch);
  },
  reset: () => {
    try { localStorage.setItem(KEY, JSON.stringify(DEFAULTS)); } catch { /* ignore */ }
    set({ ...DEFAULTS });
  },
}));

function stripFns(s: BizAssumptions): BizAssumptions {
  const { electricityPerKwh, powerW, machinePrice, machineLifeHours, laborHours, laborRate, failureRatePct, marketplaceFeePct, markupPct } = s;
  return { electricityPerKwh, powerW, machinePrice, machineLifeHours, laborHours, laborRate, failureRatePct, marketplaceFeePct, markupPct };
}

// Map to the snake_case factor keys the backend pricing engine reads.
export function bizFactors(a: BizAssumptions, pricePerKg: number) {
  return {
    price_per_kg: pricePerKg,
    power_w: a.powerW,
    electricity_per_kwh: a.electricityPerKwh,
    machine_price: a.machinePrice,
    machine_life_hours: a.machineLifeHours,
    labor_hours: a.laborHours,
    labor_rate: a.laborRate,
    failure_rate_pct: a.failureRatePct,
    markup_pct: a.markupPct,
    marketplace_fee_pct: a.marketplaceFeePct,
  };
}

export const BIZ_DEFAULTS = DEFAULTS;
