import { create } from "zustand";

// Editable "Material & business assumptions" for the Cost/Pricing/Profit Doctors.
// Persisted locally (no cloud, no account). These map 1:1 to backend factor keys the
// pricing engine already accepts; filament price + currency live in the filament store.
// Defaults are beginner-friendly *assumptions*, not measured values.
export interface BizAssumptions {
  spoolWeightG: number;       // spool weight (g); material = grams * price / spoolWeight
  gramsOverride: number;      // 0 = use Studio's grams; >0 = your entered weight
  printHours: number;         // 0 = use slicer time if known; >0 = your entered hours
  material: string;           // PLA/PETG/ABS/ASA/TPU — density used when grams unknown
  electricityPerKwh: number;  // electricity_per_kwh
  powerW: number;             // power_w (printer draw)
  machinePrice: number;       // machine_price (for depreciation)
  machineLifeHours: number;   // machine_life_hours
  laborHours: number;         // labor_hours per print
  laborRate: number;          // labor_rate ($/hr; 0 = off)
  failureRatePct: number;     // failure_rate_pct (waste/failed-print buffer)
  packaging: number;          // packaging cost per item
  marketplaceFeePct: number;  // marketplace_fee_pct
  shippingCost: number;       // shipping the seller pays
  shippingCharged: number;    // shipping charged to the buyer
  markupPct: number;          // markup_pct (margin)
}

const DEFAULTS: BizAssumptions = {
  spoolWeightG: 1000, gramsOverride: 0, printHours: 0, material: "PLA",
  electricityPerKwh: 0.20, powerW: 120, machinePrice: 600, machineLifeHours: 5000,
  laborHours: 0.25, laborRate: 0, failureRatePct: 5, packaging: 0,
  marketplaceFeePct: 0, shippingCost: 0, shippingCharged: 0, markupPct: 80,
};

// Documented filament densities (g/cm³). Used only when grams are estimated from volume
// and not known from the slicer or entered by the user.
export const MATERIAL_DENSITY: Record<string, number> = {
  PLA: 1.24, PETG: 1.27, ABS: 1.04, ASA: 1.07, TPU: 1.21,
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
  const { spoolWeightG, gramsOverride, printHours, material, electricityPerKwh, powerW, machinePrice, machineLifeHours,
    laborHours, laborRate, failureRatePct, packaging, marketplaceFeePct, shippingCost, shippingCharged, markupPct } = s;
  return { spoolWeightG, gramsOverride, printHours, material, electricityPerKwh, powerW, machinePrice, machineLifeHours,
    laborHours, laborRate, failureRatePct, packaging, marketplaceFeePct, shippingCost, shippingCharged, markupPct };
}

// Map to the snake_case factor keys the backend pricing engine reads.
// `spoolPrice` is what the user pays for one spool; effective price/kg = price / (spoolWeight/1000).
export function bizFactors(a: BizAssumptions, spoolPrice: number) {
  const w = a.spoolWeightG > 0 ? a.spoolWeightG : 1000;
  const out: Record<string, number> = {
    price_per_kg: spoolPrice * 1000 / w,
    power_w: a.powerW,
    electricity_per_kwh: a.electricityPerKwh,
    machine_price: a.machinePrice,
    machine_life_hours: a.machineLifeHours,
    labor_hours: a.laborHours,
    labor_rate: a.laborRate,
    failure_rate_pct: a.failureRatePct,
    packaging: a.packaging,
    markup_pct: a.markupPct,
    marketplace_fee_pct: a.marketplaceFeePct,
    shipping_cost: a.shippingCost,
    shipping_charged: a.shippingCharged,
  };
  if (a.gramsOverride > 0) out.grams_override = a.gramsOverride;
  if (a.printHours > 0) out.print_hours = a.printHours;
  // density only matters when grams are estimated from volume (no override / no slicer).
  if (a.gramsOverride <= 0) out.material_density = MATERIAL_DENSITY[a.material] ?? MATERIAL_DENSITY.PLA;
  return out;
}

export const BIZ_DEFAULTS = DEFAULTS;
