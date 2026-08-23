import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, HelpCircle, Loader2, PlugZap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { preflight } from "@/api";
import type { Preflight, PreflightCheck } from "@/api";
import { usePrinter } from "@/store/printer";
import {
  PREFLIGHT_SUBTITLE,
  PREFLIGHT_TITLE,
  attentionCount,
  preflightHeadline,
  resultLabel,
  resultTone,
  unknownCount,
} from "@/lib/preflight";

/**
 * "Before you slice" — this project, on this printer.
 *
 * Studio knew what a project needed and, separately, what the printer reported.
 * This card is the join: materials against toolheads, the project's nozzle
 * against the printer's, the objects against the printer's real bed, the
 * capabilities the prepared project relies on against the firmware's own list.
 *
 * The important behaviour is what it does when it cannot know. Stock U1 firmware
 * does not publish which nozzle is fitted, so that check says so and tells the
 * user to go and look — it never becomes a pass, and it never becomes
 * "unsupported".
 */
export function PreflightCard({ path }: { path: string }) {
  const host = usePrinter((s) => s.host);
  const [pre, setPre] = useState<Preflight | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let alive = true;
    setPre(null);
    setFailed(false);
    preflight(path, host).then(
      (r) => { if (alive) setPre(r); },
      () => { if (alive) setFailed(true); },
    );
    return () => { alive = false; };
  }, [path, host]);

  // Never block the page around it — the project-only Doctors still work.
  if (failed) return null;

  const problems = attentionCount(pre);
  const unknowns = unknownCount(pre);

  return (
    <Card>
      <CardContent className="space-y-3 p-5">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            {!pre ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : !pre.printer_reachable ? (
              <PlugZap className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            ) : problems > 0 ? (
              <AlertTriangle className="h-4 w-4 text-risk" aria-hidden="true" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-ready" aria-hidden="true" />
            )}
            {PREFLIGHT_TITLE}
          </h3>
          <p className="mt-0.5 text-xs text-muted-foreground">{PREFLIGHT_SUBTITLE}</p>
        </div>

        <p className="text-sm text-muted-foreground">{preflightHeadline(pre)}</p>

        {pre && (
          <>
            <ul className="flex flex-col gap-2">
              {pre.checks.map((check) => (
                <CheckRow key={check.id} check={check} />
              ))}
            </ul>
            {unknowns > 0 && (
              <p className="rounded-md border border-border bg-muted/20 p-2.5 text-[11px] text-muted-foreground">
                “Studio can’t tell” means Studio has no way to read that from your
                printer — not that your printer can’t do it. Those are the ones to
                check yourself.
              </p>
            )}
            <p className="text-[11px] text-muted-foreground">{pre.disclaimer}</p>
          </>
        )}
      </CardContent>
    </Card>
  );
}

function CheckRow({ check }: { check: PreflightCheck }) {
  const tone = resultTone(check.result);
  const border =
    tone === "ready" ? "border-ready/40" : tone === "risk" ? "border-risk/40" : "border-border";
  const Icon = tone === "ready" ? CheckCircle2 : tone === "risk" ? AlertTriangle : HelpCircle;
  const iconClass =
    tone === "ready" ? "text-ready" : tone === "risk" ? "text-risk" : "text-muted-foreground";

  return (
    <li className={`rounded-md border ${border} bg-background p-2.5`}>
      <p className="flex flex-wrap items-center gap-1.5 text-sm font-medium">
        <Icon className={`h-4 w-4 shrink-0 ${iconClass}`} aria-hidden="true" />
        {check.title}
        <span className="rounded-full bg-muted px-1.5 py-px text-[10px] uppercase tracking-wide text-muted-foreground">
          {resultLabel(check.result)}
        </span>
      </p>
      <p className="mt-1 text-xs text-muted-foreground">{check.consequence}</p>
      {check.action && (
        <p className="mt-1 text-xs">
          <span className="font-medium">Do this:</span>{" "}
          <span className="text-muted-foreground">{check.action}</span>
        </p>
      )}
      <details className="mt-1">
        <summary className="cursor-pointer text-[11px] text-muted-foreground hover:text-foreground">
          Evidence
        </summary>
        <p className="mt-1 text-[11px] text-muted-foreground">{check.evidence}</p>
        <p className="text-[11px] text-muted-foreground">
          Confidence: {check.confidence}
          {check.source ? ` · read from ${check.source}` : ""}
        </p>
      </details>
    </li>
  );
}
