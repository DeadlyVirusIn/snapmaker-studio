// Snapmaker Orca handoff helpers. Studio prepares the file; Snapmaker Orca slices
// it. Studio never slices and never controls Orca — these helpers only support a
// one-way "open the prepared file in Orca" handoff.

export const ORCA_RELEASES_URL = "https://github.com/Snapmaker/OrcaSlicer/releases";

// Beginner framing shown next to the handoff CTA. Kept here so copy stays
// consistent and testable.
export const ORCA_HANDOFF_LINE =
  "Studio checks the model first. Snapmaker Orca slices it next.";

/// Map a raw error from the `open_in_orca` Rust command to friendly, novice-safe
/// copy. Never leaks a path or a stack trace.
export function orcaErrorMessage(raw: unknown): string {
  const msg = String((raw as { message?: string })?.message ?? raw ?? "");
  if (msg.includes("orca-not-found")) {
    return "Snapmaker Orca isn’t installed yet — use Install Snapmaker Orca.";
  }
  if (msg.includes("prepared-file-missing")) {
    return "Couldn’t find the prepared file — try preparing it again.";
  }
  if (msg.includes("launch-failed")) {
    return "Couldn’t launch Snapmaker Orca — open the file from Orca instead.";
  }
  return "Couldn’t open Snapmaker Orca — open the prepared file from Orca instead.";
}
