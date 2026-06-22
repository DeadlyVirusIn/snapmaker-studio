import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { Layers, Loader2, Lightbulb, ListChecks, Cpu, SlidersHorizontal, Ban, Info } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/layout";
import { firstLayerCheck, type FirstLayerResult } from "@/api";
import { FIRST_LAYER_SYMPTOMS, FIRST_LAYER_INTRO, isAdvanced } from "@/lib/firstLayer";

function Section({ icon: Icon, title, items, markAdvanced = false }:
  { icon: typeof Lightbulb; title: string; items: string[]; markAdvanced?: boolean }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <p className="mb-1 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        <Icon className="h-3.5 w-3.5" /> {title}
      </p>
      <ul className="space-y-0.5 text-sm text-muted-foreground">
        {items.map((t, i) => {
          const adv = markAdvanced && isAdvanced(t);
          const text = adv ? t.replace(/^\s*\(advanced\)\s*/i, "") : t;
          return (
            <li key={i} className="flex items-start gap-1.5">
              <span>•</span>
              <span>{adv && <span className="mr-1 rounded bg-muted px-1 py-px text-[10px] font-medium uppercase tracking-wide">Advanced</span>}{text}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

export default function FirstLayer() {
  const [sel, setSel] = useState<string | null>(null);
  const [res, setRes] = useState<FirstLayerResult | null>(null);

  const m = useMutation({
    mutationFn: (s: string) => firstLayerCheck(s),
    onSuccess: (d) => setRes(d.result),
  });

  function pick(id: string) { setSel(id); setRes(null); m.mutate(id); }

  return (
    <div className="space-y-6">
      <PageHeader icon={Layers} title="First Layer Doctor"
        subtitle="Advisory, read-only first-layer checks (Studio changes nothing) — fix it before wasting filament." />

      <div className="flex items-start gap-2 rounded-md border border-border p-3 text-sm">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
        <span className="text-muted-foreground">{FIRST_LAYER_INTRO}</span>
      </div>

      <Card><CardContent className="p-5">
        <p className="mb-2 text-sm font-semibold">What does your first layer look like?</p>
        <div className="flex flex-wrap gap-1.5">
          {FIRST_LAYER_SYMPTOMS.map((s) => (
            <button key={s.id} onClick={() => pick(s.id)}
              className={`rounded-md border px-2.5 py-1 text-xs ${sel === s.id ? "border-foreground text-foreground" : "border-border text-muted-foreground hover:text-foreground"}`}>
              {s.title}
            </button>
          ))}
        </div>
      </CardContent></Card>

      {m.isPending && <p className="flex items-center gap-2 text-sm text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" /> loading…</p>}
      {m.isError && <p className="text-sm text-risk">{(m.error as Error).message}</p>}

      {res && (
        <Card><CardContent className="space-y-4 p-5">
          <p className="text-sm font-semibold">{res.title}</p>
          <Section icon={Lightbulb} title="Likely causes" items={res.likely_causes} />
          <Section icon={ListChecks} title="Safe first checks (in order)" items={res.first_checks} />
          <Section icon={Cpu} title="Snapmaker U1 checks" items={res.u1_checks} markAdvanced />
          <Section icon={SlidersHorizontal} title="Slicer settings to inspect" items={res.slicer_checks} />
          <Section icon={Ban} title="What not to change blindly" items={res.avoid} />
          <p className="flex items-start gap-1.5 rounded-md bg-muted/40 p-2 text-xs text-muted-foreground">
            <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {res.disclaimer}
          </p>
          <p className="text-[11px] text-muted-foreground">
            Not a first-layer issue? Try the{" "}
            <Link to="/print-quality" className="text-primary hover:underline">Print Quality Doctor</Link>.
            {" "}Contact-area / stability / fit risk → open a model and run the{" "}
            <Link to="/doctor/project" className="text-primary hover:underline">Project Doctor</Link>.
            {" "}Bed mesh / telemetry checks will live in the{" "}
            <Link to="/printers" className="text-primary hover:underline">Printer Doctor</Link>.
          </p>
        </CardContent></Card>
      )}
    </div>
  );
}
