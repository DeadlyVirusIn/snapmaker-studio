// Presentation logic for the ecosystem recommendation panel.
//
// Kept free of JSX so the rules that matter — never call a tool "installed"
// unless the engine said so, never offer to launch something that only handles
// links, always show a preview tool's caution — are unit-testable on their own.
//
// The engine decides *what* to recommend and why (see backend ecosystem.py).
// This file only decides how that reads on screen.

import type { EcosystemAdvice, EcosystemTool } from "@/api";

/** Heading above the panel. Deliberately plain-language, no jargon. */
export const ECOSYSTEM_PANEL_TITLE = "Best tool for this project";

export const ECOSYSTEM_PANEL_NOTE =
  "Studio suggests these from what it read inside your file. It never installs anything and never opens a tool on its own.";

export type ToolAction =
  | { kind: "open"; label: string }
  | { kind: "link"; label: string };

/**
 * What the button on a tool card should do.
 *
 * "open" is only ever offered when the engine confirmed an install AND the tool
 * takes a file handoff. Everything else is a link out — Studio would rather send
 * someone to a download page than pretend it can launch something it never found.
 */
export function toolAction(tool: EcosystemTool): ToolAction {
  if (tool.installed && tool.handoff === "file") {
    return { kind: "open", label: `Open in ${tool.name}` };
  }
  if (tool.installed) {
    return { kind: "link", label: `Open ${tool.name}` };
  }
  return { kind: "link", label: `About ${tool.name}` };
}

/** True when a tool needs its caution shown before anyone acts on the suggestion. */
export function needsCaution(tool: EcosystemTool): boolean {
  return Boolean(tool.caution) && tool.maturity === "preview";
}

/**
 * Suggestions worth showing beside the main Snapmaker Orca handoff.
 *
 * The official slicer already has its own prominent button, so repeating it here
 * would be noise. Everything else only earns a card if the engine attached at
 * least one reason drawn from the file.
 */
export function extraSuggestions(advice: EcosystemAdvice | null): EcosystemTool[] {
  if (!advice) return [];
  const all = [advice.primary, ...advice.alternatives].filter(Boolean) as EcosystemTool[];
  const seen = new Set<string>();
  return all.filter((t) => {
    if (t.id === "snapmaker-orca") return false;
    if (!t.why.length) return false;
    if (seen.has(t.id)) return false;
    seen.add(t.id);
    return true;
  });
}

/**
 * The one-line explanation for why Snapmaker Orca is (or is not) the next step.
 * Returns null when the engine gave no reason, so the UI can stay quiet rather
 * than inventing a justification.
 */
export function orcaReason(advice: EcosystemAdvice | null): string | null {
  if (!advice) return null;
  const orca = [advice.primary, ...advice.alternatives]
    .filter(Boolean)
    .find((t) => (t as EcosystemTool).id === "snapmaker-orca") as EcosystemTool | undefined;
  return orca?.why[0] ?? null;
}

/** Friendly copy for a failed handoff. Never leaks a path or a stack trace. */
export function toolErrorMessage(raw: unknown, toolName: string): string {
  const msg = String((raw as { message?: string })?.message ?? raw ?? "");
  if (msg.includes("tool-not-found")) {
    return `${toolName} isn’t installed yet — use the link to get it.`;
  }
  if (msg.includes("tool-not-supported")) {
    return `Studio can’t open ${toolName} for you — open the file from ${toolName} instead.`;
  }
  if (msg.includes("prepared-file-missing")) {
    return "Couldn’t find the prepared file — try preparing it again.";
  }
  return `Couldn’t open ${toolName} — open the prepared file from ${toolName} instead.`;
}
