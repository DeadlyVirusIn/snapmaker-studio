import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, HelpCircle, Loader2, Palette } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { colorPlan } from "@/api";
import type { ColorPlan, ColorUse } from "@/api";
import {
  COLOR_PLAN_TITLE,
  groups,
  swapPointText,
  useLabel,
  verdictBanner,
  verdictTone,
} from "@/lib/colorPlan";

/**
 * Colours against toolheads.
 *
 * "Too many colours" is a count, not an answer. The two reasons a project has
 * more colours than toolheads need completely different fixes: colours that
 * share layers each need a toolhead, and colours introduced part-way up are
 * already sequential and may be handled as planned swaps.
 *
 * Painted colour is stored encoded, so Studio can prove a project has painted
 * regions but not which colours they use. Those colours are shown as
 * unclassified — never in the optimistic bucket, because telling someone their
 * project is easier than it is costs them a whole print.
 */
export function ColorPlanCard({ path, toolheads = 4 }: { path: string; toolheads?: number }) {
  const [plan, setPlan] = useState<ColorPlan | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let alive = true;
    setPlan(null);
    setFailed(false);
    colorPlan(path, toolheads).then(
      (r) => { if (alive) setPlan(r); },
      () => { if (alive) setFailed(true); },
    );
    return () => { alive = false; };
  }, [path, toolheads]);

  if (failed) return null;
  if (plan && !plan.available) return null;

  const g = groups(plan);
  const tone = plan ? verdictTone(plan.verdict) : "muted";
  const Icon = tone === "ready" ? CheckCircle2 : tone === "risk" ? AlertTriangle : HelpCircle;
  const iconClass =
    tone === "ready" ? "text-ready" : tone === "risk" ? "text-risk" : "text-muted-foreground";

  return (
    <Card className="text-left">
      <CardContent className="space-y-3 p-5">
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          <Palette className="h-4 w-4 text-primary" aria-hidden="true" />
          {COLOR_PLAN_TITLE}
        </h3>

        {!plan ? (
          <p className="flex items-center gap-2 text-xs text-muted-foreground">
            <Loader2 className="h-3.5 w-3.5 animate-spin" /> Working out how the colours are used…
          </p>
        ) : (
          <>
            <div>
              <p className="text-sm font-medium">{plan.headline}</p>
              <p className="mt-0.5 flex items-center gap-1.5 text-sm">
                <Icon className={`h-4 w-4 ${iconClass}`} aria-hidden="true" />
                <span className="font-semibold">{verdictBanner(plan.verdict)}</span>
              </p>
            </div>

            <p className="text-xs text-muted-foreground">{plan.summary}</p>

            <ColorGroup
              title="Share the same layers — need a toolhead each"
              uses={g.simultaneous}
            />
            <ColorGroup
              title="Appear only higher up — could be a planned swap"
              uses={g.layerBased}
              swap
            />
            <ColorGroup
              title="Studio can’t tell how these are used"
              uses={g.unclassified}
            />

            {plan.guidance.length > 0 && (
              <ul className="list-inside list-disc space-y-0.5 text-xs text-muted-foreground">
                {plan.guidance.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            )}

            {plan.disclaimer && (
              <p className="text-[11px] text-muted-foreground">{plan.disclaimer}</p>
            )}
          </>
        )}
      </CardContent>
    </Card>
  );
}

function ColorGroup({ title, uses, swap = false }: {
  title: string;
  uses: ColorUse[];
  swap?: boolean;
}) {
  if (!uses.length) return null;
  return (
    <div className="rounded-md border border-border p-2.5">
      <p className="text-xs font-medium">
        {title} <span className="text-muted-foreground">({uses.length})</span>
      </p>
      <ul className="mt-1.5 space-y-1">
        {uses.map((use) => (
          <li key={use.slot} className="flex items-start gap-2 text-xs">
            <span
              aria-hidden="true"
              className="mt-0.5 h-3.5 w-3.5 shrink-0 rounded-sm border border-border"
              style={{ backgroundColor: use.color ?? "transparent" }}
            />
            <span>
              <span className="font-medium">{useLabel(use)}</span>
              {swap && <span className="text-muted-foreground"> — {swapPointText(use)}</span>}
              <span className="block text-[11px] text-muted-foreground">{use.evidence}</span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
