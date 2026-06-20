import { create } from "zustand";

type Theme = "light" | "dark";

function apply(theme: Theme) {
  document.documentElement.classList.toggle("dark", theme === "dark");
}

// Brand is dark-first (Asset Pack Primary Dark #0F111A). Default to dark unless
// the user has explicitly chosen otherwise.
const initial: Theme = (localStorage.getItem("theme") as Theme) || "dark";

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
