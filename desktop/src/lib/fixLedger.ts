// Presentation logic for the fix ledger.
//
// Free of JSX so the wording that a user relies on when undoing something stays
// testable — in particular that "return to original" is always described as
// opening an untouched file, never as reversing edits.

import type { FixChange, FixEntry, FixOriginal } from "@/api";

export const LEDGER_TITLE = "Changes Studio made";

export const LEDGER_NOTE =
  "Studio never writes to your original. Everything here was saved as a new file.";

export const RETURN_LABEL = "Return to the original";

/** A change rendered as one readable line, without dumping raw values. */
export function changeLine(change: FixChange): string {
  const label = change.key ?? "setting";
  const from = formatValue(change.old);
  const to = formatValue(change.new);
  if (from && to) return `${label}: ${from} → ${to}`;
  if (to) return `${label}: ${to}`;
  return label;
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "";
  if (Array.isArray(value)) {
    const shown = value.slice(0, 3).map(String).join(", ");
    return value.length > 3 ? `${shown} …` : shown;
  }
  if (typeof value === "object") return "(details)";
  const text = String(value);
  return text.length > 60 ? `${text.slice(0, 57)}…` : text;
}

/** Short "3 changes · validated" line under an entry's title. */
export function entrySubtitle(entry: FixEntry): string {
  const bits: string[] = [];
  const n = entry.changes.length;
  if (n) bits.push(`${n} change${n === 1 ? "" : "s"}`);
  if (entry.validated === true) bits.push("structure validated");
  if (entry.validated === false) bits.push("did not validate");
  if (entry.output_name) bits.push(entry.output_name);
  return bits.join(" · ");
}

/**
 * What the "return to original" control should say and whether it can act.
 *
 * When the original has been moved, the button must not silently disappear —
 * the user still needs to know their file was never touched and can be reopened
 * from wherever it now lives.
 */
export function returnState(original: FixOriginal | null): {
  enabled: boolean;
  label: string;
  explanation: string;
} {
  if (!original) {
    return { enabled: false, label: RETURN_LABEL, explanation: "" };
  }
  if (original.available) {
    return {
      enabled: true,
      label: RETURN_LABEL,
      explanation: original.note ?? LEDGER_NOTE,
    };
  }
  return {
    enabled: false,
    label: RETURN_LABEL,
    explanation: original.reason ?? "Studio has no record of an original for this file.",
  };
}

/** Entries that produced a file still worth showing, newest first. */
export function visibleEntries(entries: FixEntry[] | undefined): FixEntry[] {
  return (entries ?? []).filter((e) => e.output_name);
}
