import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, FileWarning, HelpCircle, Loader2, PlugZap } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { postSlice, slicedCost } from "@/api";
import type { PostSlice, PreflightCheck, SlicedCost } from "@/api";
import { usePrinter } from "@/store/printer";
import {
  POST_SLICE_EXPLAINER,
  POST_SLICE_SUBTITLE,
  POST_SLICE_TITLE,
  costHeadline,
  costSourceLabel,
  jobFacts,
  postSliceHeadline,
  problemCount,
  resultLabel,
  resultTone,
  unknownCount,
  wasteNote,
} from "@/lib/postSlice";

/**
 * The Post-Slice Doctor.
 *
 * Everything else in Studio inspects the project. This inspects the G-code the
 * slicer produced and joins it to the printer as it is right now, which is where
 * the interesting failures live: the job prints from slot 3 and slot 3 is empty;
 * the job was sliced for PETG and PLA is loaded; the job was sliced for another
 * machine entirely. None of those are visible in the project, and none are
 * visible on the printer alone.
 *
 * Studio still does not slice. Snapmaker Orca does.
 */
export function PostSliceCard({ path, projectPath }: { path: string; projectPath?: string }) {
  const host = usePrinter((s) => s.host);
  const [report, setReport] = useState<PostSlice | null>(null);
  const [cost, setCost] = useState<SlicedCost | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let alive = true;
    setReport(null);
    setCost(null);
    setFailed(false);
    postSlice(path, host, 7125, projectPath).then(
      (r) => { if (alive) setReport(r); },
      () => { if (alive) setFailed(true); },
    );
    slicedCost(path).then(
      (c) => { if (alive) setCost(c); },
      () => { /* costing is a bonus; the checks are the point */ },
    );
    return () => { alive = false; };
  }, [path, host, projectPath]);

  if (failed) {
    return (
      <Card>
        <CardContent className="space-y-2 p-5">
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <FileWarning className="h-4 w-4 text-risk" aria-hidden="true" />
            {POST_SLICE_TITLE}
          </h3>
          <p className="text-sm text-muted-foreground">
            Studio could not read that file. Pick the <code>.gcode</code> your slicer
            produced — not the project file it was sliced from.
          </p>
        </CardContent>
      </Card>
    );
  }

  const unreadable = report != null && !report.available;
  const problems = problemCount(report);
  const unknowns = unknownCount(report);
  const facts = jobFacts(report?.job);
  const waste = wasteNote(report?.job);

  return (
    <Card>
      <CardContent className="space-y-3 p-5">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            {!report ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : unreadable ? (
              <FileWarning className="h-4 w-4 text-risk" aria-hidden="true" />
            ) : !report.printer_reachable ? (
              <PlugZap className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
            ) : problems > 0 ? (
              <AlertTriangle className="h-4 w-4 text-risk" aria-hidden="true" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-ready" aria-hidden="true" />
            )}
            {POST_SLICE_TITLE}
          </h3>
          <p className="mt-0.5 text-xs text-muted-foreground">{POST_SLICE_SUBTITLE}</p>
        </div>

        <p className="text-sm text-muted-foreground">{postSliceHeadline(report)}</p>

        {facts.length > 0 && (
          <dl className="grid grid-cols-2 gap-x-4 gap-y-1 rounded-md border border-border bg-muted/20 p-2.5 text-xs sm:grid-cols-3">
            {facts.map((fact) => (
              <div key={fact.label}>
                <dt className="text-[11px] uppercase tracking-wide text-muted-foreground">{fact.label}</dt>
                <dd className="font-medium">{fact.value}</dd>
              </div>
            ))}
          </dl>
        )}

        {report?.available && (
          <>
            <ul className="flex flex-col gap-2">
              {report.checks.map((check) => (
                <CheckRow key={check.id} check={check} />
              ))}
            </ul>

            {unknowns > 0 && (
              <p className="rounded-md border border-border bg-muted/20 p-2.5 text-[11px] text-muted-foreground">
                “Studio can’t tell” means Studio has no way to read that — not that
                anything is wrong. Those are the ones to check yourself.
              </p>
            )}

            {cost?.available && (
              <div className="rounded-md border border-border p-2.5">
                <p className="text-sm font-medium">What it costs</p>
                <p className="mt-0.5 text-xs text-muted-foreground">{costHeadline(cost)}</p>
                <ul className="mt-2 flex flex-col gap-1">
                  {(cost.lines ?? []).map((line) => (
                    <li key={line.label} className="flex items-baseline justify-between gap-3 text-xs">
                      <span>
                        {line.label}
                        <span className="ml-1.5 text-[10px] uppercase tracking-wide text-muted-foreground">
                          {costSourceLabel(line.source)}
                        </span>
                      </span>
                      <span className="font-medium tabular-nums">
                        {line.amount == null
                          ? "—"
                          : `${cost.currency ?? "$"}${line.amount.toFixed(2)}`}
                      </span>
                    </li>
                  ))}
                </ul>
                {cost.waste && (
                  <p className="mt-2 text-[11px] text-muted-foreground">{cost.waste.detail}</p>
                )}
              </div>
            )}

            {waste && !cost?.waste && (
              <p className="text-[11px] text-muted-foreground">{waste}</p>
            )}

            <p className="text-[11px] text-muted-foreground">{report.disclaimer}</p>
          </>
        )}

        {!report && <p className="text-[11px] text-muted-foreground">{POST_SLICE_EXPLAINER}</p>}
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
      {check.evidence && (
        <details className="mt-1">
          <summary className="cursor-pointer text-[11px] text-muted-foreground hover:text-foreground">
            Evidence
          </summary>
          <p className="mt-1 text-[11px] text-muted-foreground">
            {check.evidence}
            {check.source ? ` — ${check.source}` : ""}
          </p>
        </details>
      )}
    </li>
  );
}
