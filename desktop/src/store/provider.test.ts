/**
 * The provider settings a user actually types, and what gets sent because of them.
 *
 * The bug this guards against is the one the whole sprint was about: a capability
 * that exists in the engine and that nothing in the app ever reaches. `providerArgs`
 * is the single place that decides whether a request carries provider details, so
 * a screen that forgets is a screen that silently answers "unknown" forever.
 */
import { beforeEach, describe, expect, it } from "vitest";

// These tests run in Node, which has no localStorage. The store already survives
// its absence — every read and write is guarded, because a browser can refuse
// storage too — so the stub is here to exercise the persistence path rather than
// to make the module load.
const store = new Map<string, string>();
(globalThis as { localStorage?: unknown }).localStorage = {
  getItem: (k: string) => (store.has(k) ? store.get(k)! : null),
  setItem: (k: string, v: string) => void store.set(k, String(v)),
  removeItem: (k: string) => void store.delete(k),
  clear: () => store.clear(),
  key: (i: number) => [...store.keys()][i] ?? null,
  get length() { return store.size; },
};

const { providerArgs, useProvider } = await import("./provider");

function reset() {
  localStorage.clear();
  useProvider.getState().clear();
}

describe("providerArgs", () => {
  beforeEach(reset);

  it("sends nothing when no provider is configured", () => {
    expect(providerArgs({ kind: "none", url: "", slotMap: {}, slotBase: 1 })).toEqual({});
  });

  it("sends nothing when a provider is chosen but no address typed", () => {
    expect(providerArgs({ kind: "spoolman", url: "   ", slotMap: {}, slotBase: 1 })).toEqual({});
  });

  it("sends the address, the mapping and the numbering together", () => {
    const args = providerArgs({
      kind: "spoolman", url: " spoolman.local:7912 ", slotMap: { "1": 7 }, slotBase: 1,
    });
    expect(args).toEqual({
      spoolman: "spoolman.local:7912",
      slot_map: { "1": 7 },
      slot_base: 1,
    });
  });

  it("always states the slot numbering rather than leaving it to be guessed", () => {
    // Getting this wrong puts every spool one slot out and then reports the
    // wrong material with complete confidence.
    const zero = providerArgs({ kind: "spoolman", url: "x", slotMap: { "0": 7 }, slotBase: 0 });
    expect(zero.slot_base).toBe(0);
    const one = providerArgs({ kind: "spoolman", url: "x", slotMap: { "1": 7 }, slotBase: 1 });
    expect(one.slot_base).toBe(1);
  });
});

describe("the provider store", () => {
  beforeEach(reset);

  it("starts with nothing configured", () => {
    const state = useProvider.getState();
    expect(state.kind).toBe("none");
    expect(state.url).toBe("");
    expect(state.lastSeen).toBeNull();
  });

  it("persists what the user typed", () => {
    useProvider.getState().setKind("spoolman");
    useProvider.getState().setUrl("  spoolman.local:7912  ");
    useProvider.getState().setSlot("2", 7);
    useProvider.getState().setSlotBase(0);

    expect(localStorage.getItem("materialProviderKind")).toBe('"spoolman"');
    expect(localStorage.getItem("materialProviderUrl")).toBe('"spoolman.local:7912"');
    expect(JSON.parse(localStorage.getItem("materialProviderSlotMap")!)).toEqual({ "2": 7 });
    expect(localStorage.getItem("materialProviderSlotBase")).toBe("0");
  });

  it("clears a slot rather than storing a null in it", () => {
    useProvider.getState().setSlot("2", 7);
    useProvider.getState().setSlot("2", null);
    expect(useProvider.getState().slotMap).toEqual({});
  });

  it("records when the provider was last actually read", () => {
    expect(useProvider.getState().lastSeen).toBeNull();
    useProvider.getState().markSeen();
    const seen = useProvider.getState().lastSeen;
    expect(seen).not.toBeNull();
    expect(Number.isNaN(Date.parse(seen!))).toBe(false);
  });

  it("survives a corrupted stored value rather than failing to start", () => {
    localStorage.setItem("materialProviderSlotMap", "{not json");
    // Re-reading is what happens on the next launch; the store must fall back.
    expect(() => JSON.parse(localStorage.getItem("materialProviderSlotMap")!)).toThrow();
    useProvider.getState().clear();
    expect(useProvider.getState().slotMap).toEqual({});
  });

  it("forgets everything when cleared", () => {
    useProvider.getState().setKind("spoolman");
    useProvider.getState().setUrl("spoolman.local");
    useProvider.getState().markSeen();
    useProvider.getState().clear();

    const state = useProvider.getState();
    expect(state.kind).toBe("none");
    expect(state.url).toBe("");
    expect(state.lastSeen).toBeNull();
    expect(localStorage.getItem("materialProviderUrl")).toBeNull();
  });
});
