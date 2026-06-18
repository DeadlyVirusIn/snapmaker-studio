import { create } from "zustand";
import { doctor as apiDoctor, convert as apiConvert } from "@/api";

export interface FileRef {
  path: string;
  name: string;
  ext: "stl" | "3mf" | string;
}

export type Phase = "idle" | "loading" | "done" | "error";

export interface AsyncState<T> {
  status: Phase;
  data: T | null;
  error: string | null;
}

const blank = <T>(): AsyncState<T> => ({ status: "idle", data: null, error: null });

function toFileRef(path: string): FileRef {
  const name = path.split(/[\\/]/).pop() || path;
  const ext = (name.split(".").pop() || "").toLowerCase();
  return { path, name, ext };
}

interface SessionState {
  file: FileRef | null;
  doctor: AsyncState<any>;
  convert: AsyncState<any>;
  /** Select a file and immediately run Doctor on it. */
  setFile: (path: string) => void;
  runDoctor: () => Promise<void>;
  runConvert: () => Promise<void>;
  reset: () => void;
}

export const useSession = create<SessionState>((set, get) => ({
  file: null,
  doctor: blank(),
  convert: blank(),

  setFile: (path) => {
    set({ file: toFileRef(path), doctor: blank(), convert: blank() });
    void get().runDoctor();
  },

  runDoctor: async () => {
    const file = get().file;
    if (!file) return;
    set({ doctor: { status: "loading", data: null, error: null } });
    try {
      const data = await apiDoctor(file.path);
      set({ doctor: { status: "done", data, error: null } });
    } catch (e: any) {
      set({ doctor: { status: "error", data: null, error: String(e?.message ?? e) } });
    }
  },

  runConvert: async () => {
    const file = get().file;
    if (!file) return;
    set({ convert: { status: "loading", data: null, error: null } });
    try {
      const data = await apiConvert(file.path);
      set({ convert: { status: "done", data, error: null } });
    } catch (e: any) {
      set({ convert: { status: "error", data: null, error: String(e?.message ?? e) } });
    }
  },

  reset: () => set({ file: null, doctor: blank(), convert: blank() }),
}));
