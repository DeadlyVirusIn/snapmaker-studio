import { describe, it, expect } from "vitest";
import {
  draftFrom, splitDraft, validateBusinessDraft, isBusinessDirty, hasErrors, pickAssumptions,
} from "./businessForm";
import { BIZ_DEFAULTS, bizFactors } from "@/store/business";

const base = draftFrom(BIZ_DEFAULTS, 25); // applied snapshot: $25 spool, defaults

describe("draft vs applied — results don't change until Recalculate", () => {
  it("editing a field marks the draft dirty (cards stay on the applied calc)", () => {
    const edited = { ...base, spoolPrice: 10 };
    expect(isBusinessDirty(edited, base)).toBe(true);
  });

  it("an unchanged draft is not dirty", () => {
    expect(isBusinessDirty({ ...base }, base)).toBe(false);
  });

  it("typing intermediate values stays draft-only until applied", () => {
    // user types 1 then 10 — both are draft edits, both 'not applied yet'
    expect(isBusinessDirty({ ...base, spoolPrice: 1 }, base)).toBe(true);
    expect(isBusinessDirty({ ...base, spoolPrice: 10 }, base)).toBe(true);
    // applying makes draft == applied -> no longer dirty
    const applied = { ...base, spoolPrice: 10 };
    expect(isBusinessDirty(applied, applied)).toBe(false);
  });

  it("Recalculate applies the draft to one factor snapshot feeding all three cards", () => {
    const { spoolPrice, assumptions } = splitDraft({ ...base, spoolPrice: 10, markupPct: 120 });
    expect(spoolPrice).toBe(10);
    // one factors object drives cost + pricing + profit queries together
    const f = bizFactors(assumptions, spoolPrice);
    expect(f.price_per_kg).toBe(10); // 1000 g spool
    expect(f.markup_pct).toBe(120);
  });
});

describe("validation — gentle, no crash, no nonsense", () => {
  it("spool price must be positive", () => {
    expect(validateBusinessDraft({ ...base, spoolPrice: 0 }).spoolPrice).toBeTruthy();
    expect(validateBusinessDraft({ ...base, spoolPrice: 25 }).spoolPrice).toBeUndefined();
  });
  it("spool weight must be positive", () => {
    expect(validateBusinessDraft({ ...base, spoolWeightG: 0 }).spoolWeightG).toBeTruthy();
  });
  it("markup must be zero or positive", () => {
    expect(validateBusinessDraft({ ...base, markupPct: -5 }).markupPct).toBeTruthy();
    expect(validateBusinessDraft({ ...base, markupPct: 0 }).markupPct).toBeUndefined();
  });
  it("a valid draft has no errors", () => {
    expect(hasErrors(validateBusinessDraft(base))).toBe(false);
  });
});

describe("grams: blank uses Studio estimate, entered overrides", () => {
  it("blank grams (0) is valid and means 'use the estimate'", () => {
    expect(validateBusinessDraft({ ...base, gramsOverride: 0 }).gramsOverride).toBeUndefined();
    // 0 -> backend gets no grams_override, so it uses its own estimate
    expect("grams_override" in bizFactors({ ...BIZ_DEFAULTS, gramsOverride: 0 }, 25)).toBe(false);
  });
  it("entered grams override the estimate", () => {
    expect(bizFactors({ ...BIZ_DEFAULTS, gramsOverride: 82 }, 25).grams_override).toBe(82);
  });
  it("negative grams is rejected", () => {
    expect(validateBusinessDraft({ ...base, gramsOverride: -1 }).gramsOverride).toBeTruthy();
  });
});

describe("pickAssumptions — draft never carries store methods", () => {
  it("drops set/reset and keeps only assumption fields", () => {
    const dirty = { ...BIZ_DEFAULTS, set: () => {}, reset: () => {} } as never;
    const clean = pickAssumptions(dirty);
    expect("set" in clean).toBe(false);
    expect("reset" in clean).toBe(false);
    expect(clean.spoolWeightG).toBe(BIZ_DEFAULTS.spoolWeightG);
  });
});
