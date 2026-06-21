import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  GitCompareArrows, FilePlus, ShieldCheck, AlertTriangle, CheckCircle2,
  Loader2, ArrowRight, Layers, Lock, ImageOff,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import { open3mfDialog, plateInspect, plateDryRun, plateExport } from "@/api";
import {
  COPY, canDryRun, canExport, plateByUiNumber, fromOptions, toOptions, exportView,
  colorName, plateSummary, changeSummary, staysSame,
  type Selection, type PlateInspect, type PlateDryRun, type PlateExport,
} from "@/lib/plateRemapWizard";

const BLUE = "--doctor-project"; // Project Doctor blue, per brief

function Swatch({ color }: { color?: string | null }) {
  if (!color) return null;
  return <span className="inline-block h-3 w-3 rounded-sm border border-border align-middle" style={{ background: color }} />;
}

export default function PlateRemap() {
  const [sel, setSel] = useState<Selection>({ path: null, uiPlate: null, fromFilament: null, toFilament: null });
  const [inspectData, setInspectData] = useState<PlateInspect | null>(null);
  const [dryRun, setDryRun] = useState<PlateDryRun | null>(null);
  const [result, setResult] = useState<PlateExport | null>(null);

  const inspectM = useMutation({
    mutationFn: (p: string) => plateInspect(p),
    onSuccess: (d) => { setInspectData(d); },
  });
  const dryRunM = useMutation({
    mutationFn: () => plateDryRun(sel.path!, sel.uiPlate!, sel.fromFilament!, sel.toFilament!),
    onSuccess: (d) => setDryRun(d),
  });
  const exportM = useMutation({
    mutationFn: () => plateExport(sel.path!, sel.uiPlate!, sel.fromFilament!, sel.toFilament!),
    onSuccess: (d) => setResult(d),
  });

  // Any selection change invalidates a prior dry-run/result → re-gates export.
  function update(patch: Partial<Selection>) {
    setSel((s) => ({ ...s, ...patch }));
    setDryRun(null);
    setResult(null);
  }

  async function pickFile() {
    const p = await open3mfDialog();
    if (!p) return;
    setSel({ path: p, uiPlate: null, fromFilament: null, toFilament: null });
    setInspectData(null); setDryRun(null); setResult(null);
    inspectM.mutate(p);
  }

  const plate = plateByUiNumber(inspectData, sel.uiPlate);
  const froms = fromOptions(plate);
  const tos = toOptions(inspectData);
  const view = exportView(result);
  const exporting = exportM.isPending;

  // Beginner-facing summaries (pure; derived from inspect/dry-run — no writer change).
  const summary = plateSummary(plate);
  const change = changeSummary(inspectData, sel);
  const stays = staysSame(inspectData, plate, sel, dryRun);

  // staged status checklist (the real async steps)
  const steps = [
    { label: "Inspect file", done: !!inspectData?.available, active: inspectM.isPending, failed: false },
    { label: "Preview & validate", done: !!dryRun?.available, active: dryRunM.isPending, failed: false },
    { label: "Export & verify", done: !!result?.passed, active: exporting,
      failed: result != null && !result.passed },
  ];

  return (
    <div className="space-y-6">
      <PageHeader icon={GitCompareArrows} title={COPY.title} subtitle={COPY.subtitle} />

      {/* safety message — always visible */}
      <div className="flex items-start gap-2 rounded-md border border-border p-3 text-sm"
           style={{ backgroundColor: `hsl(var(${BLUE}) / 0.06)` }}>
        <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0" style={{ color: `hsl(var(${BLUE}))` }} />
        <span className="text-muted-foreground">{COPY.safety}</span>
      </div>

      {/* 1. file */}
      <Card><CardContent className="flex items-center gap-3 p-5">
        <Button variant="secondary" size="sm" onClick={pickFile} disabled={inspectM.isPending}>
          <FilePlus className="h-4 w-4" /> {sel.path ? "Choose another 3MF" : "Open a 3MF project"}
        </Button>
        {sel.path && <span className="truncate text-xs text-muted-foreground" title={sel.path}>{sel.path.split(/[\\/]/).pop()}</span>}
        {inspectM.isPending && <span className="flex items-center gap-1 text-xs text-muted-foreground"><Loader2 className="h-3.5 w-3.5 animate-spin" /> inspecting…</span>}
      </CardContent></Card>

      {inspectM.isError && (
        <p className="text-sm text-risk">Couldn't read that file: {(inspectM.error as Error).message}</p>
      )}
      {inspectData && !inspectData.available && (
        <p className="text-sm text-risk">{inspectData.reason ?? "Not a readable Orca/Snapmaker 3MF project."}</p>
      )}

      {/* 2. plate + filament selection (plate-based, by plater_id) */}
      {inspectData?.available && (
        <Card><CardContent className="space-y-4 p-5">
          <p className="text-sm font-semibold">Target one plate (by its plate number)</p>
          <div className="flex flex-wrap gap-2">
            {(inspectData.plates ?? []).filter((p) => p.ui_number != null).map((p) => (
              <button key={p.ui_number}
                onClick={() => update({ uiPlate: p.ui_number, fromFilament: null, toFilament: null })}
                className={`flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm ${sel.uiPlate === p.ui_number ? "text-foreground" : "border-border text-muted-foreground"}`}
                style={sel.uiPlate === p.ui_number ? { borderColor: `hsl(var(${BLUE}))`, backgroundColor: `hsl(var(${BLUE}) / 0.08)` } : undefined}>
                <Layers className="h-3.5 w-3.5" /> Plate {p.ui_number}
                <span className="text-[11px] opacity-70">({p.objects.length} obj{p.painted_accents_present ? ", painted" : ""})</span>
              </button>
            ))}
          </div>

          {plate && (
            <>
              {/* beginner summary of the selected plate */}
              {summary && (
                <div className="rounded-md border border-border bg-muted/30 p-3 text-sm">
                  <p className="font-medium">{summary.sentence}</p>
                  {/* visual fallback: colour/part summary. TODO(beta.4+): render an
                      actual plate/model preview from the 3MF geometry when a
                      renderer is available; until then show this colour summary. */}
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <span className="text-xs text-muted-foreground">Colors on this plate:</span>
                    {(plate.filaments_used ?? []).map((f) => (
                      <span key={f.id} className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Swatch color={f.color} /> {colorName(f.color) ?? `slot ${f.id}`}
                      </span>
                    ))}
                    {(plate.filaments_used ?? []).length === 0 && <span className="text-xs text-muted-foreground">—</span>}
                  </div>
                  <p className="mt-2 flex items-start gap-1.5 text-[11px] text-muted-foreground">
                    <ImageOff className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {COPY.previewUnavailable}
                  </p>
                </div>
              )}

              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <p className="mb-1 text-xs font-medium text-muted-foreground">{COPY.questionFrom}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {froms.map((f) => (
                      <button key={f.id} onClick={() => update({ fromFilament: f.id })}
                        className={`flex items-center gap-1.5 rounded border px-2 py-1 text-xs ${sel.fromFilament === f.id ? "border-foreground text-foreground" : "border-border text-muted-foreground"}`}>
                        <Swatch color={f.color} /> {colorName(f.color) ?? `Filament ${f.id}`} <span className="opacity-60">(slot {f.id})</span>
                      </button>
                    ))}
                    {froms.length === 0 && <span className="text-xs text-muted-foreground">no base colors detected on this plate</span>}
                  </div>
                </div>
                <div>
                  <p className="mb-1 text-xs font-medium text-muted-foreground">{COPY.questionTo}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {tos.map((f) => (
                      <button key={f.id} onClick={() => update({ toFilament: f.id })}
                        disabled={sel.fromFilament === f.id}
                        className={`flex items-center gap-1.5 rounded border px-2 py-1 text-xs disabled:opacity-40 ${sel.toFilament === f.id ? "border-foreground text-foreground" : "border-border text-muted-foreground"}`}>
                        <Swatch color={f.color} /> {colorName(f.color) ?? `Filament ${f.id}`} <span className="opacity-60">(slot {f.id})</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}

          <Button size="sm" onClick={() => dryRunM.mutate()} disabled={!canDryRun(sel) || dryRunM.isPending}>
            {dryRunM.isPending ? <><Loader2 className="h-4 w-4 animate-spin" /> Previewing…</> : <>Preview changes</>}
          </Button>
        </CardContent></Card>
      )}

      {/* 3. dry-run preview (required before export) */}
      {dryRun && (
        <Card><CardContent className="space-y-3 p-5">
          <p className="flex items-center gap-2 text-sm font-semibold"><GitCompareArrows className="h-4 w-4" style={{ color: `hsl(var(${BLUE}))` }} /> {COPY.confirmTitle} — nothing has been written yet</p>
          {!dryRun.available && <p className="text-sm text-risk">{dryRun.reason}</p>}
          {dryRun.available && (
            <>
              {/* What will change — plain English */}
              <div className="rounded-md border border-border p-3">
                <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-muted-foreground">What will change</p>
                {change && (
                  <p className="flex flex-wrap items-center gap-1.5 text-sm">
                    <Swatch color={change.fromColor} /> {change.fromName ?? `slot ${change.fromId}`}
                    <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
                    <Swatch color={change.toColor} /> {change.toName ?? `slot ${change.toId}`}
                    <span className="text-muted-foreground">· {dryRun.change_count ?? 0} object{(dryRun.change_count ?? 0) === 1 ? "" : "s"} on Plate {sel.uiPlate} only</span>
                  </p>
                )}
                {change && <p className="mt-1 text-xs text-muted-foreground">{change.sentence}</p>}
                <p className="mt-1 text-[11px] text-muted-foreground">
                  Changed: {(dryRun.changes ?? []).map((c) => c.name || `object ${c.object_id}`).join(", ") || "none"}
                </p>
              </div>

              {/* What will stay the same — protected details + untouched plates */}
              <div className="rounded-md border p-3" style={{ borderColor: "hsl(var(--stage-validate) / 0.4)" }}>
                <p className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide" style={{ color: "hsl(var(--stage-validate))" }}>
                  <Lock className="h-3.5 w-3.5" /> What will stay the same
                </p>
                <ul className="space-y-1 text-xs text-muted-foreground">
                  {stays.paintedProtected && (
                    <li className="flex items-start gap-1.5"><ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                      {stays.protectedColorLabels.length > 0
                        ? `Protected colors on this plate: ${stays.protectedColorLabels.join(", ")}.`
                        : COPY.paintedUnlabeled}
                    </li>
                  )}
                  {stays.goldDetected && (
                    <li className="flex items-start gap-1.5"><ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0" /> Gold/yellow accents stay unchanged.</li>
                  )}
                  {stays.otherFilaments.length > 0 && (
                    <li className="flex items-start gap-1.5"><ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0" /> Other colors on this plate ({stays.otherFilaments.map((f) => f.name ?? `slot ${f.id}`).join(", ")}) stay unchanged.</li>
                  )}
                  <li className="flex items-start gap-1.5"><ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0" /> Other plates untouched: {stays.otherPlates.join(", ") || "—"}.</li>
                  <li className="flex items-start gap-1.5"><ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0" /> Painted facets and mesh data are not edited. Your original file is never changed.</li>
                </ul>
              </div>

              {(dryRun.warnings ?? []).length > 0 && (
                <div className="rounded-md bg-repairable/5 p-2 text-xs text-repairable">
                  {(dryRun.warnings ?? []).map((w, i) => (
                    <p key={i} className="flex items-start gap-1.5"><AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {w}</p>
                  ))}
                </div>
              )}
              <Button size="sm" onClick={() => exportM.mutate()} disabled={!canExport(sel, dryRun) || exporting}
                      style={canExport(sel, dryRun) ? { backgroundColor: `hsl(var(${BLUE}))` } : undefined}>
                {exporting ? <><Loader2 className="h-4 w-4 animate-spin" /> Creating safe copy… (large files ~30s)</> : <>{COPY.exportCta} <ArrowRight className="h-4 w-4" /></>}
              </Button>
            </>
          )}
        </CardContent></Card>
      )}

      {/* progress checklist while working */}
      {(inspectM.isPending || dryRunM.isPending || exporting || result) && (
        <Card><CardContent className="space-y-1.5 p-4 text-xs">
          {steps.map((s) => (
            <p key={s.label} className="flex items-center gap-2">
              {s.failed ? <AlertTriangle className="h-3.5 w-3.5 text-risk" />
                : s.active ? <Loader2 className="h-3.5 w-3.5 animate-spin text-primary" />
                : s.done ? <CheckCircle2 className="h-3.5 w-3.5 text-ready" />
                : <span className="h-2 w-2 rounded-full bg-muted-foreground/30" />}
              <span className={s.done ? "text-foreground" : "text-muted-foreground"}>{s.label}</span>
            </p>
          ))}
        </CardContent></Card>
      )}

      {/* 4/5. result */}
      {exportM.isError && (
        <p className="text-sm text-risk">Export call failed: {(exportM.error as Error).message}. Your original file was not modified.</p>
      )}
      {view?.kind === "success" && (
        <Card><CardContent className="space-y-2 p-5">
          <p className="flex items-center gap-2 text-sm font-semibold text-ready"><CheckCircle2 className="h-4 w-4" /> {COPY.proofTitle}</p>
          <p className="text-xs text-muted-foreground">{view.message}</p>
          <ul className="space-y-1 pt-1 text-xs text-muted-foreground">
            <li className="flex items-start gap-1.5"><CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-ready" /> Changed objects: {view.changedObjects.map((c) => c.name || `object ${c.object_id}`).join(", ") || "none"}</li>
            <li className="flex items-start gap-1.5"><CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-ready" /> Untouched plates: {view.untouchedPlates.join(", ") || "—"}</li>
            <li className="flex items-start gap-1.5"><CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-ready" /> Painted details unchanged.</li>
            <li className="flex items-start gap-1.5"><CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-ready" /> Mesh data unchanged.</li>
            <li className="flex items-start gap-1.5"><CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-ready" /> Original file unchanged.</li>
          </ul>
          <p className="pt-1 text-xs"><span className="font-medium">Safe copy saved to:</span> <span className="break-all text-muted-foreground">{view.outputPath}</span></p>
          {view.checks.length > 0 && (
            <details className="pt-1 text-[11px] text-muted-foreground">
              <summary className="cursor-pointer">Verification checks ({view.checks.length})</summary>
              <ul className="mt-1 space-y-0.5">
                {view.checks.map((c, i) => (
                  <li key={i} className="flex items-center gap-1.5"><CheckCircle2 className="h-3 w-3 text-ready" /> {c.check}</li>
                ))}
              </ul>
            </details>
          )}
        </CardContent></Card>
      )}
      {view?.kind === "failure" && (
        <Card><CardContent className="space-y-2 p-5">
          <p className="flex items-center gap-2 text-sm font-semibold text-risk"><AlertTriangle className="h-4 w-4" /> {view.message}</p>
          <p className="text-xs text-muted-foreground">Reason: {view.reason}</p>
          {view.quarantined && <p className="text-xs text-muted-foreground">Rejected output quarantined at: <span className="break-all">{view.quarantined}</span></p>}
          <p className="text-xs text-muted-foreground">{view.nextAction}</p>
        </CardContent></Card>
      )}
    </div>
  );
}
