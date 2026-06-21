import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { Stethoscope, Loader2, Lightbulb, ListChecks, SlidersHorizontal, Wrench, Ban, Info } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/layout";
import { qualityCheck, type QualityResult } from "@/api";
import { QUALITY_SYMPTOMS, QUALITY_INTRO } from "@/lib/printQuality";

function Section({ icon: Icon, title, items }: { icon: typeof Lightbulb; title: string; items: string[] }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <p className="mb-1 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        <Icon className="h-3.5 w-3.5" /> {title}
      </p>
      <ul className="space-y-0.5 text-sm text-muted-foreground">
        {items.map((t, i) => <li key={i} className="flex gap-1.5"><span>•</span><span>{t}</span></li>)}
      </ul>
    </div>
  );
}

export default function PrintQuality() {
  const [sel, setSel] = useState<string | null>(null);
  const [res, setRes] = useState<QualityResult | null>(null);

  const m = useMutation({
    mutationFn: (s: string) => qualityCheck(s),
    onSuccess: (d) => setRes(d.result),
  });

  function pick(id: string) {
    setSel(id); setRes(null); m.mutate(id);
  }

  return (
    <div className="space-y-6">
      <PageHeader icon={Stethoscope} title="Print Quality Doctor"
        subtitle="A bad print or preview? Pick the symptom and get safe first checks." />

      <div className="flex items-start gap-2 rounded-md border border-border p-3 text-sm">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
        <span className="text-muted-foreground">{QUALITY_INTRO}</span>
      </div>

      <Card><CardContent className="p-5">
        <p className="mb-2 text-sm font-semibold">What does your print look like?</p>
        <div className="flex flex-wrap gap-1.5">
          {QUALITY_SYMPTOMS.map((s) => (
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
          <Section icon={SlidersHorizontal} title="Where to look in Snapmaker Orca" items={res.orca_paths} />
          <Section icon={Wrench} title="Hardware / material checks" items={res.hardware_checks} />
          <Section icon={Ban} title="What not to change blindly" items={res.avoid} />
          <p className="flex items-start gap-1.5 rounded-md bg-muted/40 p-2 text-xs text-muted-foreground">
            <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {res.disclaimer}
          </p>
          <p className="text-[11px] text-muted-foreground">
            Related: a slicer/profile warning before printing →{" "}
            <Link to="/compatibility" className="text-primary hover:underline">Compatibility Doctor</Link>;
            {" "}resize-related risk →{" "}
            <Link to="/scale" className="text-primary hover:underline">Scale Doctor</Link>;
            {" "}geometry / fit risk → open a model and run the{" "}
            <Link to="/doctor/project" className="text-primary hover:underline">Project Doctor</Link>.
          </p>
        </CardContent></Card>
      )}
    </div>
  );
}
