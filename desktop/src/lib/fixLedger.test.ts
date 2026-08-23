import { describe, expect, it } from "vitest";
import type { FixEntry, FixOriginal } from "@/api";
import {
  LEDGER_NOTE,
  changeLine,
  entrySubtitle,
  returnState,
  visibleEntries,
} from "./fixLedger";

const entry = (over: Partial<FixEntry> = {}): FixEntry => ({
  schema_version: "fixledger/1",
  operation: "prepare_u1_copy",
  title: "Prepared a U1 copy",
  timestamp: "2026-08-23T10:00:00Z",
  source_name: "model.3mf",
  output_name: "model_SnapmakerU1.3mf",
  changes: [],
  findings: [],
  validated: true,
  notes: [],
  ...over,
});

describe("changeLine", () => {
  it("shows an old and new value", () => {
    expect(changeLine({ key: "brim_type", old: "auto_brim", new: "no_brim" }))
      .toBe("brim_type: auto_brim → no_brim");
  });

  it("shows only the new value when there was no old one", () => {
    expect(changeLine({ key: "exclude_object", new: "1" })).toBe("exclude_object: 1");
  });

  it("summarises a long array instead of dumping it", () => {
    const line = changeLine({ key: "filament_colour", new: ["#a", "#b", "#c", "#d", "#e"] });
    expect(line).toContain("…");
    expect(line).not.toContain("#e");
  });

  it("does not spill a huge value into the line", () => {
    const line = changeLine({ key: "machine_start_gcode", new: "G".repeat(500) });
    expect(line.length).toBeLessThan(90);
  });

  it("falls back to the key alone", () => {
    expect(changeLine({ key: "something" })).toBe("something");
    expect(changeLine({})).toBe("setting");
  });
});

describe("entrySubtitle", () => {
  it("counts changes and names the output", () => {
    const line = entrySubtitle(entry({ changes: [{ key: "a" }, { key: "b" }] }));
    expect(line).toContain("2 changes");
    expect(line).toContain("model_SnapmakerU1.3mf");
    expect(line).toContain("structure validated");
  });

  it("uses the singular for one change", () => {
    expect(entrySubtitle(entry({ changes: [{ key: "a" }] }))).toContain("1 change ");
  });

  it("says plainly when something did not validate", () => {
    expect(entrySubtitle(entry({ validated: false }))).toContain("did not validate");
  });

  it("says nothing about validation when it is unknown", () => {
    const line = entrySubtitle(entry({ validated: null }));
    expect(line).not.toContain("validate");
  });
});

describe("returnState", () => {
  const original = (over: Partial<FixOriginal> = {}): FixOriginal => ({
    available: true,
    source_path: "C:/x/model.3mf",
    source_name: "model.3mf",
    note: "Your original was never modified.",
    ...over,
  });

  it("is disabled and silent before the lookup returns", () => {
    const state = returnState(null);
    expect(state.enabled).toBe(false);
    expect(state.explanation).toBe("");
  });

  it("enables the return when the original is still there", () => {
    const state = returnState(original());
    expect(state.enabled).toBe(true);
    expect(state.explanation).toContain("never modified");
  });

  it("keeps explaining when the original has been moved", () => {
    const state = returnState(original({
      available: false,
      reason: "The original is no longer where Studio last saw it. It was never modified.",
    }));
    expect(state.enabled).toBe(false);
    expect(state.explanation).toContain("never modified");
  });

  it("never describes the return as undoing edits to the prepared file", () => {
    for (const o of [original(), original({ available: false, reason: "gone" })]) {
      const text = `${returnState(o).label} ${returnState(o).explanation}`.toLowerCase();
      expect(text).not.toContain("revert the copy");
      expect(text).not.toContain("undo the changes");
    }
  });
});

describe("visibleEntries", () => {
  it("is empty when there is no history", () => {
    expect(visibleEntries(undefined)).toEqual([]);
  });

  it("drops entries that produced no file", () => {
    const list = visibleEntries([entry(), entry({ output_name: null })]);
    expect(list).toHaveLength(1);
  });
});

describe("wording", () => {
  it("the standing note tells the user their original is untouched", () => {
    expect(LEDGER_NOTE).toContain("never writes to your original");
  });
});
