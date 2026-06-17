import { create } from "zustand";

type Theme = "light" | "dark";

function apply(theme: Theme) {
  document.documentElement.classList.toggle("dark", theme === "dark");
}

const initial: Theme =
  (localStorage.getItem("theme") as Theme) ||
  (window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "dark" : "light");

interface ThemeState {
  theme: Theme;
  toggle: () => void;
  set: (t: Theme) => void;
}

export const useTheme = create<ThemeState>((set, get) => ({
  theme: initial,
  toggle: () => get().set(get().theme === "dark" ? "light" : "dark"),
  set: (t) => {
    localStorage.setItem("theme", t);
    apply(t);
    set({ theme: t });
  },
}));

// apply on module load
apply(initial);
