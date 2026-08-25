import { create } from "zustand";

// The material provider the user has configured, if any.
//
// Studio's engine has read Spoolman for several releases, and until now no part
// of the app ever sent it an address — so the capability existed and nobody
// could reach it. This store is the missing half: it holds what the user typed,
// persists it locally the way the printer address and filament price already
// are, and every screen that asks "do I have enough filament?" passes it along.
//
// Nothing here goes anywhere. The address is a machine on the user's own
// network, the engine refuses anything that is not, and none of it is ever sent
// off the machine.

export type ProviderKind = "none" | "spoolman";

/** Which spool the user says is in which slot. Keyed by the slot number as the
 *  user counts them — see `slotBase`, which records whether that is 0 or 1. */
export type SlotMap = Record<string, number>;

const KEY_KIND = "materialProviderKind";
const KEY_URL = "materialProviderUrl";
const KEY_MAP = "materialProviderSlotMap";
const KEY_BASE = "materialProviderSlotBase";
const KEY_SEEN = "materialProviderLastSeen";

function read<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw === null ? fallback : (JSON.parse(raw) as T);
  } catch {
    // A corrupted value is not worth failing to start over.
    return fallback;
  }
}

function write(key: string, value: unknown): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    /* storage full or blocked — the setting simply does not persist */
  }
}

interface ProviderState {
  kind: ProviderKind;
  url: string;
  slotMap: SlotMap;
  /** 0 when the user counts their slots from zero, 1 when from one. Stated
   *  rather than guessed: getting it wrong puts every spool one slot out and
   *  then reports the wrong material with complete confidence. */
  slotBase: 0 | 1;
  /** ISO timestamp of the last successful read, so the app can say how long it
   *  has been since it actually spoke to the provider. */
  lastSeen: string | null;

  setKind: (kind: ProviderKind) => void;
  setUrl: (url: string) => void;
  setSlot: (slot: string, spoolId: number | null) => void;
  setSlotBase: (base: 0 | 1) => void;
  markSeen: () => void;
  clear: () => void;
}

/** What to send with a request, or nothing at all when no provider is set up. */
export function providerArgs(state: {
  kind: ProviderKind; url: string; slotMap: SlotMap; slotBase: 0 | 1;
}): { spoolman?: string; slot_map?: SlotMap; slot_base?: number } {
  if (state.kind !== "spoolman" || !state.url.trim()) return {};
  return { spoolman: state.url.trim(), slot_map: state.slotMap, slot_base: state.slotBase };
}

export const useProvider = create<ProviderState>((set, get) => ({
  kind: read<ProviderKind>(KEY_KIND, "none"),
  url: read<string>(KEY_URL, ""),
  slotMap: read<SlotMap>(KEY_MAP, {}),
  slotBase: read<0 | 1>(KEY_BASE, 1),
  lastSeen: read<string | null>(KEY_SEEN, null),

  setKind: (kind) => {
    write(KEY_KIND, kind);
    set({ kind });
  },
  setUrl: (url) => {
    const value = url.trim();
    write(KEY_URL, value);
    set({ url: value });
  },
  setSlot: (slot, spoolId) => {
    const next = { ...get().slotMap };
    if (spoolId === null) delete next[slot];
    else next[slot] = spoolId;
    write(KEY_MAP, next);
    set({ slotMap: next });
  },
  setSlotBase: (slotBase) => {
    write(KEY_BASE, slotBase);
    set({ slotBase });
  },
  markSeen: () => {
    const lastSeen = new Date().toISOString();
    write(KEY_SEEN, lastSeen);
    set({ lastSeen });
  },
  clear: () => {
    [KEY_KIND, KEY_URL, KEY_MAP, KEY_BASE, KEY_SEEN].forEach((k) => {
      try { localStorage.removeItem(k); } catch { /* nothing to do */ }
    });
    set({ kind: "none", url: "", slotMap: {}, slotBase: 1, lastSeen: null });
  },
}));
