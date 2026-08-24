import { useEffect, useState } from "react";
import {
  AlertOctagon, AlertTriangle, CheckCircle2, HelpCircle, ListOrdered, Loader2, Package,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { materialPlan, printPlan, sendCheck } from "@/api";
import type { MaterialPlan, PrintPlan, SendCheck, SendItem } from "@/api";
import { usePrinter } from "@/store/printer";
import {
  MATERIALS_SUBTITLE, MATERIALS_TITLE, PLAN_SUBTITLE, PLAN_TITLE, SEND_TITLE,
  changeCount, itemLabel, itemsOfKind, materialsHeadline, orderedSlots, planHeadline,
  planIsTruncated, planLines, sendHeadline, sendTone, shouldDiscourageSend, slotLabel, slotTone,
} from "@/lib/sendPlan";

/**
 * "Ready to send?" — the last thing Studio says before a person presses a button.
 *
 * Three buckets kept apart on purpose. A blocker is a provable mismatch, a
 * warning is a real concern that is not proof, and an unknown is something
 * Studio cannot verify. Collapsing them would be the easiest way to make this
 * card feel decisive and be wrong.
 *
 * Nothing here sends anything.
 */
export function SendReadyCard({ path, projectPath }: { path: string; projectPath?: string }) {
  const host = usePrinter((s) => s.host);
  const [check, setCheck] = useState<SendCheck | null>(null);

  useEffect(() => {
    let alive = true;
    setCheck(null);
    sendCheck(path, host, 7125, true, projectPath).then(
      (r) => { if (alive) setCheck(r); },
      () => { /* the post-slice card already reports an unreadable file */ },
    );
    return () => { alive = false; };
  }, [path, host, projectPath]);

  const tone = sendTone(check?.verdict);
  const Icon = tone === "ready" ? CheckCircle2
    : tone === "risk" ? AlertOctagon
    : tone === "warn" ? AlertTriangle : HelpCircle;
  const iconClass = tone === "ready" ? "text-ready"
    : tone === "risk" ? "text-risk"
    : tone === "warn" ? "text-risk" : "text-muted-foreground";

  return (
    <Card>
      <CardContent className="space-y-3 p-5">
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          {check ? <Icon className={`h-4 w-4 ${iconClass}`} aria-hidden="true" />
                 : <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
          {SEND_TITLE}
        </h3>

        <p className="text-sm text-muted-foreground">{sendHeadline(check)}</p>

        {check?.available && (
          <>
            {(["blocker", "warning", "unknown"] as SendItem["kind"][]).map((kind) => {
              const items = itemsOfKind(check, kind);
              if (!items.length) return null;
              return (
                <ul key={kind} className="flex flex-col gap-2">
                  {items.map((item) => (
                    <li
                      key={`${kind}-${item.title}`}
                      className={`rounded-md border p-2.5 ${
                        kind === "blocker" ? "border-risk/50"
                        : kind === "warning" ? "border-risk/25" : "border-border"}`}
                    >
                      <p className="flex flex-wrap items-center gap-1.5 text-sm font-medium">
                        {item.title}
                        <span className="rounded-full bg-muted px-1.5 py-px text-[10px] uppercase tracking-wide text-muted-foreground">
                          {itemLabel(kind)}
                        </span>
                      </p>
                      {item.detail && (
                        <p className="mt-1 text-xs text-muted-foreground">{item.detail}</p>
                      )}
                      {item.action && (
                        <p className="mt-1 text-xs">
                          <span className="font-medium">Do this:</span>{" "}
                          <span className="text-muted-foreground">{item.action}</span>
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              );
            })}

            {shouldDiscourageSend(check) && (
              <p className="rounded-md border border-risk/50 bg-risk/5 p-2.5 text-xs">
                Studio will not stop you — it is your printer. But sending this now
                spends the upload on a job that will not finish.
              </p>
            )}

            <p className="text-[11px] text-muted-foreground">{check.disclaimer}</p>
          </>
        )}
      </CardContent>
    </Card>
  );
}

/** What to load, slot by slot. An intelligence layer over spool state, not an inventory. */
export function MaterialPlanCard({ path }: { path: string }) {
  const host = usePrinter((s) => s.host);
  const [plan, setPlan] = useState<MaterialPlan | null>(null);

  useEffect(() => {
    let alive = true;
    setPlan(null);
    materialPlan(path, host).then(
      (r) => { if (alive) setPlan(r); },
      () => { /* silent: the send card already carries the important half */ },
    );
    return () => { alive = false; };
  }, [path, host]);

  const changes = changeCount(plan);

  return (
    <Card>
      <CardContent className="space-y-3 p-5">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            {plan ? <Package className={`h-4 w-4 ${changes ? "text-risk" : "text-ready"}`} aria-hidden="true" />
                  : <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />}
            {MATERIALS_TITLE}
          </h3>
          <p className="mt-0.5 text-xs text-muted-foreground">{MATERIALS_SUBTITLE}</p>
        </div>

        <p className="text-sm text-muted-foreground">{materialsHeadline(plan)}</p>

        {plan?.available && (
          <ul className="flex flex-col gap-2">
            {orderedSlots(plan).map((slot) => {
              const tone = slotTone(slot.state);
              const border = tone === "ready" ? "border-ready/40"
                : tone === "risk" ? "border-risk/40" : "border-border";
              return (
                <li key={slot.tool} className={`rounded-md border ${border} p-2.5`}>
                  <p className="flex flex-wrap items-center gap-1.5 text-sm font-medium">
                    <span className="capitalize">{slot.label}</span>
                    <span className="rounded-full bg-muted px-1.5 py-px text-[10px] uppercase tracking-wide text-muted-foreground">
                      {slotLabel(slot.state)}
                    </span>
                    {slot.wants_colour && (
                      <span
                        className="inline-block h-3 w-3 rounded-full border border-border"
                        style={{ backgroundColor: slot.wants_colour }}
                        aria-label={`the job expects ${slot.wants_colour}`}
                      />
                    )}
                    {slot.has_colour && slot.has_colour !== slot.wants_colour && (
                      <span
                        className="inline-block h-3 w-3 rounded-full border border-border"
                        style={{ backgroundColor: slot.has_colour }}
                        aria-label={`${slot.has_colour} is loaded`}
                      />
                    )}
                  </p>
                  {slot.detail && (
                    <p className="mt-1 text-xs text-muted-foreground">{slot.detail}</p>
                  )}
                  {slot.action && (
                    <p className="mt-1 text-xs">
                      <span className="font-medium">Do this:</span>{" "}
                      <span className="text-muted-foreground">{slot.action}</span>
                    </p>
                  )}
                </li>
              );
            })}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * The print, in order.
 *
 * Loaded on request: it costs a full pass over the file, which on a 300 MB job is
 * seconds rather than milliseconds. Everything else on the page answers instantly
 * and should not wait for this.
 */
export function PrintPlanCard({ path }: { path: string }) {
  const [plan, setPlan] = useState<PrintPlan | null>(null);
  const [asked, setAsked] = useState(false);

  useEffect(() => { setPlan(null); setAsked(false); }, [path]);

  const lines = planLines(plan);

  return (
    <Card>
      <CardContent className="space-y-3 p-5">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            {asked && !plan
              ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              : <ListOrdered className="h-4 w-4" aria-hidden="true" />}
            {PLAN_TITLE}
          </h3>
          <p className="mt-0.5 text-xs text-muted-foreground">{PLAN_SUBTITLE}</p>
        </div>

        {!asked && (
          <Button
            variant="secondary"
            onClick={() => {
              setAsked(true);
              printPlan(path).then(setPlan, () => setPlan(null));
            }}
          >
            Read the whole job
          </Button>
        )}

        {asked && <p className="text-sm text-muted-foreground">{planHeadline(plan)}</p>}

        {lines.length > 0 && (
          <ol className="flex flex-col gap-1.5">
            {lines.map((line, index) => (
              <li key={`${line.at}-${index}`} className="rounded-md border border-border p-2.5">
                <p className="text-sm">
                  <span className="font-medium">{line.at}</span>
                  <span className="text-muted-foreground"> — {line.text}</span>
                </p>
                <details className="mt-1">
                  <summary className="cursor-pointer text-[11px] text-muted-foreground hover:text-foreground">
                    Evidence
                  </summary>
                  <p className="mt-1 text-[11px] text-muted-foreground">{line.evidence}</p>
                </details>
              </li>
            ))}
          </ol>
        )}

        {planIsTruncated(plan) && (
          <p className="text-[11px] text-muted-foreground">
            This job has more events than Studio keeps in one report, so the list above
            stops early rather than pretending to be complete.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
