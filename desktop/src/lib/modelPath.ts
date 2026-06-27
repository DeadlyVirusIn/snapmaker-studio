// Pure logic for "reuse the model already open in the session" on tool pages.
// Extracted so the rule (a freshly picked file wins; otherwise fall back to the
// session model when it's eligible) is unit-testable without React.
import type { FileRef } from "@/store/session";

export interface EffectiveModel {
  /** Path the tool should act on, or null when nothing is available. */
  path: string | null;
  /** True when `path` came from the session (vs. a file the user just picked). */
  fromSession: boolean;
}

/**
 * A file the user picks on the page always wins. Otherwise the page reuses the
 * model already open in the session, but only when `eligible` accepts it (e.g. a
 * 3MF-only tool ignores a loaded STL).
 */
export function effectiveModelPath(
  sessionFile: FileRef | null,
  picked: string | null,
  eligible: (f: FileRef) => boolean = () => true,
): EffectiveModel {
  if (picked !== null) return { path: picked, fromSession: false };
  if (sessionFile && eligible(sessionFile)) return { path: sessionFile.path, fromSession: true };
  return { path: null, fromSession: false };
}

/** Eligibility helper: only reuse the session model when it has this extension. */
export const isExt = (ext: string) => (f: FileRef) => f.ext === ext;
