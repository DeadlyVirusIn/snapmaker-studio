import { create } from "zustand";

/**
 * The sliced job Studio currently has open.
 *
 * Kept separate from the project session on purpose: a G-code file is not a
 * project, and confusing the two is how a tool starts checking the wrong file.
 * A user can have a project open and a sliced job open at the same time, and
 * the Post-Slice Doctor compares them.
 */
interface SlicedState {
  path: string | null;
  name: string | null;
  setSliced: (path: string) => void;
  clear: () => void;
}

export const useSliced = create<SlicedState>((set) => ({
  path: null,
  name: null,
  setSliced: (path: string) =>
    // Split on both separators. Getting this wrong meant `name` stayed the whole
    // Windows path, and the page — and the recorded demo — showed a home
    // directory where a file name belonged.
    set({ path, name: path.split(/[\\/]/).pop() || path }),
  clear: () => set({ path: null, name: null }),
}));
