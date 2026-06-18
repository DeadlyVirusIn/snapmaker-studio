import { create } from "zustand";

// "Simple" is the novice-first experience (default); "Advanced" preserves the
// original power-user screens unchanged. Persisted like the theme preference.
export type Mode = "simple" | "advanced";

const initial: Mode = (localStorage.getItem("mode") as Mode) || "simple";

interface ModeState {
  mode: Mode;
  setMode: (m: Mode) => void;
}

export const useMode = create<ModeState>((set) => ({
  mode: initial,
  setMode: (m) => {
    localStorage.setItem("mode", m);
    set({ mode: m });
  },
}));
