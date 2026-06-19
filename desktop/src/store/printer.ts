import { create } from "zustand";

// The U1 the user monitors. Persisted so the Printer Hub, Dashboard, and
// Settings all agree on one address. Default is the U1's stock mDNS name.
const KEY = "u1Host";
const initial = localStorage.getItem(KEY) || "U1.local";

interface PrinterState {
  host: string;
  setHost: (h: string) => void;
}

export const usePrinter = create<PrinterState>((set) => ({
  host: initial,
  setHost: (h) => {
    const v = h.trim() || "U1.local";
    localStorage.setItem(KEY, v);
    set({ host: v });
  },
}));
