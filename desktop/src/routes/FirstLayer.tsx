import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { Layers, Loader2, Lightbulb, ListChecks, Cpu, SlidersHorizontal, Ban, Info, FilePlus, CheckCircle2, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/layout";
import { firstLayerCheck, firstLayer, openModelDialog, type FirstLayerResult, type FirstLayerReport } from "@/api";
import { FIRST_LAYER_SYMPTOMS, FIRST_LAYER_INTRO, isAdvanced } from "@/lib/firstLayer";

function lvlColor(l?: string) { return l === "risk" ? "text-risk" : l === "warn" ? "text-doctor-cost" : "text-stage-validate"; }

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

  const [filePath, setFilePath] = useState<string | null>(null);
  const [rep, setRep] = useState<FirstLayerReport | null>(null);
  const fm = useMutation({ mutationFn: (p: string) => firstLayer(p), onSuccess: (d) => setRep(d) });

  function pick(id: string) { setSel(id); setRes(null); m.mutate(id); }
  async function pickFile() {
    const p = await openModelDialog();
    if (!p) return;
    setFilePath(p); setRep(null); fm.mutate(p);
  }

  return (
    <div className="space-y-6">
      <PageHeader icon={Layers} title="First Layer Doctor"
        subtitle="Advisory, read-only first-layer checks (Studio changes nothing) — fix it before wasting filament." />

      <div className="flex items-start gap-2 rounded-md border border-border p-3 text-sm">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
        <span className="text-muted-foreground">{FIRST_LAYER_INTRO}</span>
      </div>

      <Card><CardContent className="space-y-3 p-5">
        <div className="flex flex-wrap items-center gap-3">
          <button onClick={pickFile} className="inline-flex items-center gap-1.5 rounded-md border border-border px-2.5 py-1.5 text-sm hover:text-foreground">
            <FilePlus className="h-4 w-4" /> {filePath ? "Choose another model" : "Open a model for file-specific checks"}
          </button>
          {filePath && <span className="truncate text-xs text-muted-foreground" title={filePath}>{filePath.split(/[\\/]/).pop()}</span>}
          {fm.isPending && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
        </div>
        {fm.isError && <p className="text-sm text-risk">Couldn't read that file: {(fm.error as Error).message}</p>}
        {rep && (
          rep.available ? (
            <div className="space-y-2 rounded-md border border-border p-3">
              <p className="text-sm font-semibold">What Studio found in this file</p>
              {rep.overall_text && (
                <p className={`flex items-center gap-1.5 text-sm font-medium ${lvlColor(rep.overall_level)}`}>
                  {rep.overall_level === "ok" ? <CheckCircle2 className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />}
                  {rep.overall_text}
                </p>
              )}
              <ul className="space-y-1 text-sm">
                {rep.findings?.map((f, i) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className={`mt-1 h-1.5 w-1.5 shrink-0 rounded-full ${f.level === "risk" ? "bg-risk" : f.level === "warn" ? "bg-doctor-cost" : "bg-stage-validate"}`} />
                    <span className="text-muted-foreground">{f.text}</span>
                  </li>
                ))}
              </ul>
              {rep.signals_used && rep.signals_used.length > 0 &&
                <p className="text-[11px] text-muted-foreground">Based on: {rep.signals_used.join(", ")}. Advisory — not a print-success guarantee.</p>}
            </div>
          ) : (
            <p className="rounded-md border border-border p-3 text-sm text-muted-foreground">
              {rep.reason || "Studio didn't find a strong file-specific first-layer signal for this model. Start with the general checks below."}
            </p>
          )
        )}
      </CardContent></Card>

      <Card><CardContent className="p-5">
        <p className="mb-2 text-sm font-semibold">{filePath ? "Or pick what your first layer looks like" : "What does your first layer look like?"}</p>
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
