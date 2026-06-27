import { useState } from "react";
import { useSession, type FileRef } from "@/store/session";
import { effectiveModelPath } from "@/lib/modelPath";

/**
 * Tool-page hook: reuse the model already open in the session instead of forcing
 * the user to re-pick. `path` is what the tool should act on (a file the user
 * picks via `override` wins); `fromSession` is true while it's the session model.
 * Pass `eligible` (e.g. isExt("3mf")) so a 3MF-only tool ignores a loaded STL.
 */
export function useModelPath(eligible?: (f: FileRef) => boolean) {
  const sessionFile = useSession((s) => s.file);
  const [picked, setPicked] = useState<string | null>(null);
  const { path, fromSession } = effectiveModelPath(sessionFile, picked, eligible);
  return { path, fromSession, override: setPicked };
}
