import { useState } from "react";
import { Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { Stethoscope, Loader2, Lightbulb, ListChecks, SlidersHorizontal, Wrench, Ban, Info, FilePlus, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/layout";
import { qualityCheck, openModelDialog, printFailureTroubleshoot, type QualityResult, type PrintFailureResult } from "@/api";
import { QUALITY_SYMPTOMS, QUALITY_INTRO } from "@/lib/printQuality";
import { FAILURE_STAGES, PRINT_FAILURE_COPY, failureMode, isBlameFree } from "@/lib/printFailure";
import { Button } from "@/components/ui/button";

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

function FailsWithSupports() {
  const [open, setOpen] = useState(false);
  const [path, setPath] = useState<string | null>(null);
  const [knownGood, setKnownGood] = useState<boolean | null>(null);
  const [goodMat, setGoodMat] = useState("");
  const [failMat, setFailMat] = useState("");
  const [stage, setStage] = useState("unknown");
  const [res, setRes] = useState<PrintFailureResult | null>(null);

  const m = useMutation({
    mutationFn: () => printFailureTroubleshoot({
      path: path || "none",
      known_good_print: knownGood ?? undefined,
      known_good_material: goodMat || undefined,
      failed_material: failMat || undefined,
      failure_stage: stage,
    }),
    onSuccess: setRes,
  });

  const mode = res ? failureMode(res.known_good_print) : null;

  return (
    <Card><CardContent className="space-y-3 p-5">
      <button onClick={() => setOpen((o) => !o)} className="flex w-full items-center gap-2 text-sm font-semibold">
        <AlertTriangle className="h-4 w-4 text-doctor-cost" /> Fails even with supports?
        <span className="ml-auto text-xs text-muted-foreground">{open ? "hide" : "open"}</span>
      </button>

      {open && (
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <Button size="sm" variant="secondary" onClick={async () => { const p = await openModelDialog(); if (p) { setPath(p); setRes(null); } }}>
              <FilePlus className="h-4 w-4" /> {path ? "Choose another model" : "Open the project (optional)"}
            </Button>
            {path && <span className="truncate text-xs text-muted-foreground" title={path}>{path.split(/[\\/]/).pop()}</span>}
          </div>

          <div className="space-y-2 text-sm">
            <p className="text-xs font-semibold text-muted-foreground">Has this exact file printed successfully before?</p>
            <div className="flex gap-1.5">
              {[["Yes", true], ["No / not sure", false]].map(([l, v]) => (
                <button key={String(v)} onClick={() => setKnownGood(v as boolean)}
                  className={`rounded-md border px-2.5 py-1 text-xs ${knownGood === v ? "border-foreground text-foreground" : "border-border text-muted-foreground"}`}>{l as string}</button>
              ))}
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              <input value={goodMat} onChange={(e) => setGoodMat(e.target.value)} placeholder="Filament that worked (optional)"
                className="rounded-md border border-border bg-background px-2 py-1 text-xs outline-none focus:border-primary" />
              <input value={failMat} onChange={(e) => setFailMat(e.target.value)} placeholder="Filament that is failing (optional)"
                className="rounded-md border border-border bg-background px-2 py-1 text-xs outline-none focus:border-primary" />
            </div>
            <p className="text-xs font-semibold text-muted-foreground">Where does it fail?</p>
            <div className="flex flex-wrap gap-1.5">
              {FAILURE_STAGES.map((s) => (
                <button key={s.id} onClick={() => setStage(s.id)}
                  className={`rounded-md border px-2.5 py-1 text-xs ${stage === s.id ? "border-foreground text-foreground" : "border-border text-muted-foreground"}`}>{s.label}</button>
              ))}
            </div>
            <Button size="sm" onClick={() => m.mutate()} disabled={m.isPending}>
              {m.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Stethoscope className="h-4 w-4" />} Get troubleshooting guidance
            </Button>
          </div>

          {m.isError && <p className="text-sm text-risk">Couldn't analyze that: {(m.error as Error).message}</p>}

          {res?.available && mode && (
            <div className="space-y-3 border-t border-border pt-3">
              <p className="text-sm font-semibold">{mode.title}</p>
              <ul className="space-y-0.5 text-sm text-muted-foreground">
                {mode.points.map((p, i) => <li key={i} className="flex gap-1.5"><span>•</span><span>{p}</span></li>)}
              </ul>
              {isBlameFree(res) && res.findings?.map((f) => (
                <div key={f.id} className="rounded-md border border-border p-2.5 text-xs">
                  <p className="font-medium text-foreground">{f.title}</p>
                  <p className="text-muted-foreground">{f.explanation}</p>
                  <p className="mt-1 text-muted-foreground">→ {f.suggested_action}</p>
                  {f.safe_starting_point && <p className="mt-1 text-muted-foreground">Starting point: {f.safe_starting_point}</p>}
                </div>
              ))}
              <ul className="space-y-0.5 text-xs text-muted-foreground">
                <li>• {PRINT_FAILURE_COPY.cooldown}</li>
                <li>• {PRINT_FAILURE_COPY.oneChange}</li>
                <li>• {PRINT_FAILURE_COPY.silkSwap}</li>
              </ul>
              <p className="flex items-start gap-1.5 rounded-md bg-muted/40 p-2 text-xs text-muted-foreground">
                <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {PRINT_FAILURE_COPY.notGuarantee} {PRINT_FAILURE_COPY.noAutoEdit}
              </p>
            </div>
          )}
        </div>
      )}
    </CardContent></Card>
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
        subtitle="A bad print or preview? Pick the symptom for advisory, read-only first checks (Studio changes nothing)." />

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

      <FailsWithSupports />
    </div>
  );
}
