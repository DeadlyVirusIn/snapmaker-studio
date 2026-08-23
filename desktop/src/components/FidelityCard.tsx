import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, Loader2, ShieldCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { fidelityAudit } from "@/api";
import type { FidelityReport, FidelityRow } from "@/api";
import {
  FIDELITY_HEADINGS,
  FIDELITY_TITLE,
  countsLine,
  fidelityHeadline,
  groupedRows,
  statusLabel,
  statusTone,
} from "@/lib/fidelity";

/**
 * What survived preparing this copy.
 *
 * Every other converter tells a user "converted". This says what that cost:
 * what stayed identical, what Studio changed and why, what it could not carry
 * over — and, most importantly, what it could not check at all.
 *
 * The strong claim ("nothing was lost") is only shown when the engine's audit
 * granted it for this specific pair of files. It is never inferred here.
 */
export function FidelityCard({ original, prepared }: { original: string; prepared: string }) {
  const [report, setReport] = useState<FidelityReport | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let alive = true;
    setReport(null);
    setFailed(false);
    fidelityAudit(original, prepared).then(
      (r) => { if (alive) setReport(r); },
      () => { if (alive) setFailed(true); },
    );
    return () => { alive = false; };
  }, [original, prepared]);

  if (failed) return null;

  const groups = groupedRows(report);
  const unresolved = groups.unverified.length + groups.notCarried.length;

  return (
    <Card className="text-left">
      <CardContent className="space-y-3 p-5">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            {!report ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            ) : unresolved === 0 ? (
              <ShieldCheck className="h-4 w-4 text-ready" aria-hidden="true" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-risk" aria-hidden="true" />
            )}
            {FIDELITY_TITLE}
          </h3>
          {report?.available && (
            <p className="mt-0.5 text-[11px] text-muted-foreground">{countsLine(report)}</p>
          )}
        </div>

        <p className="text-sm text-muted-foreground">{fidelityHeadline(report)}</p>

        {report?.available && (
          <div className="space-y-2">
            <Group title={FIDELITY_HEADINGS.unverified} rows={groups.unverified} open />
            <Group title={FIDELITY_HEADINGS.notCarried} rows={groups.notCarried} open />
            <Group title={FIDELITY_HEADINGS.changed} rows={groups.changed} />
            <Group title={FIDELITY_HEADINGS.kept} rows={groups.kept} />
            {report.disclaimer && (
              <p className="text-[11px] text-muted-foreground">{report.disclaimer}</p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function Group({ title, rows, open = false }: { title: string; rows: FidelityRow[]; open?: boolean }) {
  if (!rows.length) return null;
  return (
    <details open={open} className="rounded-md border border-border">
      <summary className="cursor-pointer px-2.5 py-2 text-xs font-medium">
        {title} <span className="text-muted-foreground">({rows.length})</span>
      </summary>
      <ul className="space-y-1.5 px-2.5 pb-2.5">
        {rows.map((row) => (
          <RowLine key={`${row.element}-${row.part ?? ""}`} row={row} />
        ))}
      </ul>
    </details>
  );
}

function RowLine({ row }: { row: FidelityRow }) {
  const tone = statusTone(row.status);
  const Icon = tone === "ready" ? CheckCircle2 : tone === "risk" ? AlertTriangle : undefined;
  const iconClass = tone === "ready" ? "text-ready" : "text-risk";
  return (
    <li className="text-xs">
      <p className="flex flex-wrap items-center gap-1.5 font-medium">
        {Icon && <Icon className={`h-3.5 w-3.5 shrink-0 ${iconClass}`} aria-hidden="true" />}
        {row.element}
        <span className="rounded-full bg-muted px-1.5 py-px text-[10px] uppercase tracking-wide text-muted-foreground">
          {statusLabel(row.status)}
        </span>
      </p>
      <p className="text-muted-foreground">{row.detail}</p>
      {row.reason && <p className="text-muted-foreground">Why: {row.reason}</p>}
    </li>
  );
}
