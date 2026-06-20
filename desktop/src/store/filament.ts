import { create } from "zustand";

// Filament price the user pays, used for material cost estimates. Persisted like
// the theme / mode preferences. Defaults to a typical 1 kg PLA spool.
interface FilamentState {
  pricePerKg: number;
  currency: string;
  setPrice: (p: number) => void;
  setCurrency: (c: string) => void;
}

const initPrice = Number(localStorage.getItem("filamentPricePerKg")) || 20;
const initCurrency = localStorage.getItem("filamentCurrency") || "$";

export const useFilament = create<FilamentState>((set) => ({
  pricePerKg: initPrice,
  currency: initCurrency,
  setPrice: (p) => {
    const v = Number.isFinite(p) && p > 0 ? p : 20;
    localStorage.setItem("filamentPricePerKg", String(v));
    set({ pricePerKg: v });
  },
  setCurrency: (c) => {
    const v = (c || "$").slice(0, 3);
    localStorage.setItem("filamentCurrency", v);
    set({ currency: v });
  },
}));
