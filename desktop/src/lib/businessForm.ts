// Draft-vs-applied logic for the Cost & Pricing Doctor calculator.
//
// The calculator edits a *draft* of the user's assumptions; the Cost/Pricing/Profit
// cards keep showing the last *applied* calculation until the user clicks
// Recalculate. This module holds the pure, unit-testable parts of that model:
// building a draft, validating it, and deciding whether the draft is stale
// (different from what's applied). No React, no stores — easy to test.
import { BIZ_DEFAULTS, type BizAssumptions } from "@/store/business";

// A draft is every editable business assumption plus the spool price (which the
// app stores in the filament store, separate from BizAssumptions).
export interface BizDraft extends BizAssumptions {
  spoolPrice: number;
}

const BIZ_KEYS = Object.keys(BIZ_DEFAULTS) as (keyof BizAssumptions)[];

/** Copy only the assumption fields (drops any store methods like set/reset). */
export function pickAssumptions(o: BizAssumptions): BizAssumptions {
  const out = {} as BizAssumptions;
  for (const k of BIZ_KEYS) out[k] = o[k] as never;
  return out;
}

/** Combine the applied business assumptions with the current spool price. */
export function draftFrom(biz: BizAssumptions, spoolPrice: number): BizDraft {
  return { ...pickAssumptions(biz), spoolPrice };
}

/** Split a draft back into the spool price and the BizAssumptions to apply. */
export function splitDraft(d: BizDraft): { spoolPrice: number; assumptions: BizAssumptions } {
  const { spoolPrice, ...assumptions } = d;
  return { spoolPrice, assumptions };
}

// Gentle, novice-friendly validation. Blank grams (0) is allowed — it means
// "use Studio's estimate", so 0 is NOT an error. We never want a novice to type a
// magic number to get the fallback.
export function validateBusinessDraft(d: BizDraft): Partial<Record<keyof BizDraft, string>> {
  const e: Partial<Record<keyof BizDraft, string>> = {};
  if (!(d.spoolPrice > 0)) e.spoolPrice = "Enter a spool price above 0.";
  if (!(d.spoolWeightG > 0)) e.spoolWeightG = "Spool weight must be above 0.";
  if (d.gramsOverride < 0) e.gramsOverride = "Grams must be 0 or more (leave blank for the estimate).";
  if (d.markupPct < 0) e.markupPct = "Markup can't be negative.";
  return e;
}

/** True when a draft has at least one validation error. */
export function hasErrors(e: Partial<Record<string, string>>): boolean {
  return Object.keys(e).length > 0;
}

/** True when the draft differs from what's applied, so the shown results are stale. */
export function isBusinessDirty(draft: BizDraft, applied: BizDraft): boolean {
  return (Object.keys(draft) as (keyof BizDraft)[]).some((k) => draft[k] !== applied[k]);
}
