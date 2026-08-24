import { create } from "zustand";

const FOLDER_KEY = "snapstudio.watchFolder";
const AUTO_KEY = "snapstudio.watchAutoOpen";

/**
 * The one folder Studio is allowed to look in for sliced jobs.
 *
 * Remembered between sessions because choosing it every time would make the
 * round-trip feel like the manual step it replaces. Kept in local storage rather
 * than the engine's database: it is a preference about this machine, and nothing
 * else depends on it.
 */
interface WatchState {
  folder: string | null;
  autoOpen: boolean;
  setFolder: (folder: string | null) => void;
  setAutoOpen: (on: boolean) => void;
}

function read(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;                 // private mode, or no storage at all
  }
}

function write(key: string, value: string | null) {
  try {
    if (value === null) window.localStorage.removeItem(key);
    else window.localStorage.setItem(key, value);
  } catch {
    /* remembering is a convenience, never a requirement */
  }
}

export const useWatch = create<WatchState>((set) => ({
  folder: read(FOLDER_KEY),
  autoOpen: read(AUTO_KEY) !== "off",
  setFolder: (folder) => {
    write(FOLDER_KEY, folder);
    set({ folder });
  },
  setAutoOpen: (on) => {
    write(AUTO_KEY, on ? "on" : "off");
    set({ autoOpen: on });
  },
}));
