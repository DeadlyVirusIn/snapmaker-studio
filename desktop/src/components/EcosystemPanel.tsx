import { useEffect, useState } from "react";
import { AlertTriangle, ExternalLink, Loader2, Rocket, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/store/toast";
import { detectTools, ecosystemAdvice, openWithTool } from "@/api";
import type { EcosystemAdvice, EcosystemTool } from "@/api";
import {
  ECOSYSTEM_PANEL_NOTE,
  ECOSYSTEM_PANEL_TITLE,
  extraSuggestions,
  needsCaution,
  orcaReason,
  toolAction,
  toolErrorMessage,
} from "@/lib/ecosystem";

/**
 * "Best tool for this project."
 *
 * The U1 has a large open-source ecosystem, and the hard part for a beginner is
 * not that the tools are missing — it is having to know all of them before any
 * of them can help. This panel reads what is actually inside the file and names
 * the tool that fits, with the reason drawn from the file itself.
 *
 * It never installs anything, never launches anything on its own, and only says
 * a tool is installed when the shell found its executable on disk.
 */
export function EcosystemPanel({ path }: { path: string }) {
  const showToast = useToast((s) => s.show);
  const [advice, setAdvice] = useState<EcosystemAdvice | null>(null);
  const [state, setState] = useState<"loading" | "ready" | "failed">("loading");
  const [busy, setBusy] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    setState("loading");
    (async () => {
      try {
        const installed = await detectTools();
        const result = await ecosystemAdvice(path, installed);
        if (alive) {
          setAdvice(result);
          setState("ready");
        }
      } catch {
        if (alive) setState("failed");
      }
    })();
    return () => {
      alive = false;
    };
  }, [path]);

  if (state === "loading") {
    return (
      <div className="flex items-center gap-2 rounded-md border border-border bg-muted/20 p-3 text-xs text-muted-foreground">
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
        Checking which tools suit this project…
      </div>
    );
  }

  // A failure here must never block the main workflow — the Orca handoff above
  // still works, so the panel simply says nothing rather than showing an error.
  if (state === "failed" || !advice) return null;

  const suggestions = extraSuggestions(advice);
  const why = orcaReason(advice);
  if (!why && suggestions.length === 0) return null;

  return (
    <section
      aria-labelledby="ecosystem-panel-title"
      className="rounded-md border border-border bg-muted/20 p-3 text-left"
    >
      <h3
        id="ecosystem-panel-title"
        className="flex items-center gap-1.5 text-sm font-medium text-foreground"
      >
        <Sparkles className="h-4 w-4 text-primary" aria-hidden="true" />
        {ECOSYSTEM_PANEL_TITLE}
      </h3>

      {why && (
        <p className="mt-1.5 text-xs text-muted-foreground">
          <span className="font-medium text-foreground">Snapmaker Orca — </span>
          {why}
        </p>
      )}

      {suggestions.length > 0 && (
        <ul className="mt-2 flex flex-col gap-2">
          {suggestions.map((tool) => (
            <ToolCard
              key={tool.id}
              tool={tool}
              path={path}
              busy={busy === tool.id}
              onOpen={async () => {
                setBusy(tool.id);
                try {
                  await openWithTool(tool.id, path);
                  showToast(`Opening your file in ${tool.name}…`);
                } catch (e) {
                  showToast(toolErrorMessage(e, tool.name));
                } finally {
                  setBusy(null);
                }
              }}
            />
          ))}
        </ul>
      )}

      <p className="mt-2 text-[11px] text-muted-foreground">{ECOSYSTEM_PANEL_NOTE}</p>
    </section>
  );
}

function ToolCard({
  tool,
  busy,
  onOpen,
}: {
  tool: EcosystemTool;
  path: string;
  busy: boolean;
  onOpen: () => void;
}) {
  const action = toolAction(tool);
  return (
    <li className="rounded-md border border-border bg-background p-2.5">
      <div className="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
        <span className="text-sm font-medium text-foreground">{tool.name}</span>
        <span className="text-[11px] uppercase tracking-wide text-muted-foreground">
          {tool.official ? "official" : "community"} · {tool.license}
        </span>
      </div>
      <p className="mt-0.5 text-xs text-muted-foreground">{tool.role}</p>
      <ul className="mt-1.5 flex flex-col gap-0.5">
        {tool.why.map((reason) => (
          <li key={reason} className="text-xs text-foreground">
            {reason}
          </li>
        ))}
      </ul>

      {needsCaution(tool) && (
        <p className="mt-1.5 flex items-start gap-1.5 text-[11px] text-amber-600 dark:text-amber-400">
          <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0" aria-hidden="true" />
          <span>{tool.caution}</span>
        </p>
      )}

      <div className="mt-2 flex flex-wrap items-center gap-2">
        {action.kind === "open" ? (
          <Button size="sm" onClick={onOpen} disabled={busy}>
            {busy ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Rocket className="h-3.5 w-3.5" />
            )}
            {busy ? "Opening…" : action.label}
          </Button>
        ) : (
          <Button size="sm" variant="secondary" asChild>
            <a href={tool.url} target="_blank" rel="noreferrer">
              <ExternalLink className="h-3.5 w-3.5" /> {action.label}
            </a>
          </Button>
        )}
        {!tool.installed && (
          <span className="text-[11px] text-muted-foreground">{tool.install_hint}</span>
        )}
      </div>
    </li>
  );
}
