import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import {
  ShieldCheck, FilePlus, AlertTriangle, CheckCircle2, Loader2, Info, ArrowRight,
} from "lucide-react";
import { Link } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import { open3mfDialog, compatibilityCheck, convert, type CompatibilityResult } from "@/api";
import { OrcaHandoff } from "@/components/OrcaHandoff";
import { Copy, Stethoscope } from "lucide-react";
import { COMPAT_COPY, sortFindings, severityLabel, severityToken, countFindings } from "@/lib/compatibility";

export default function Compatibility() {
  const [path, setPath] = useState<string | null>(null);
  const [result, setResult] = useState<CompatibilityResult | null>(null);
  const [prep, setPrep] = useState<Awaited<ReturnType<typeof convert>> | null>(null);

  const checkM = useMutation({
    mutationFn: (p: string) => compatibilityCheck(p),
    onSuccess: (d) => setResult(d),
  });

  const prepM = useMutation({
    mutationFn: () => convert(path!),
    onSuccess: (d) => setPrep(d),
  });

  async function pick() {
    const p = await open3mfDialog();
    if (!p) return;
    setPath(p); setResult(null); setPrep(null);
    checkM.mutate(p);
  }

  async function copyPath(p: string) {
    try { await navigator.clipboard.writeText(p); } catch { /* clipboard unavailable */ }
  }

  const counts = result ? countFindings(result.findings) : null;
  const sorted = result ? sortFindings(result.findings) : [];

  return (
    <div className="space-y-6">
      <PageHeader icon={ShieldCheck} title={COMPAT_COPY.title} subtitle={COMPAT_COPY.subtitle} />

      <div className="flex items-start gap-2 rounded-md border border-border p-3 text-sm">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
        <span className="text-muted-foreground">{COMPAT_COPY.readOnlyNote}</span>
      </div>

      <Card><CardContent className="flex items-center gap-3 p-5">
        <Button variant="secondary" size="sm" onClick={pick} disabled={checkM.isPending}>
          <FilePlus className="h-4 w-4" /> {path ? "Choose another 3MF" : "Open a 3MF project"}
        </Button>
        {path && <span className="truncate text-xs text-muted-foreground" title={path}>{path.split(/[\\/]/).pop()}</span>}
        {checkM.isPending && <span className="flex items-center gap-1 text-xs text-muted-foreground"><Loader2 className="h-3.5 w-3.5 animate-spin" /> checking…</span>}
      </CardContent></Card>

      {!path && <p className="text-sm text-muted-foreground">{COMPAT_COPY.intro}</p>}
      {checkM.isError && <p className="text-sm text-risk">Couldn't read that file: {(checkM.error as Error).message}</p>}

      {result && (
        <Card><CardContent className="space-y-3 p-5">
          <p className="text-sm text-muted-foreground">{result.summary}</p>

          {counts && counts.total === 0 ? (
            <p className="flex items-center gap-2 text-sm font-semibold text-ready">
              <CheckCircle2 className="h-4 w-4" /> {COMPAT_COPY.cleanTitle}
            </p>
          ) : (
            <ul className="space-y-2">
              {sorted.map((f) => (
                <li key={f.id} className="rounded-md border p-3"
                    style={{ borderColor: `hsl(var(${severityToken(f.severity)}) / 0.5)` }}>
                  <p className="flex items-center gap-1.5 text-sm font-semibold">
                    {f.severity === "error"
                      ? <AlertTriangle className="h-4 w-4 text-risk" />
                      : <Info className="h-4 w-4" style={{ color: `hsl(var(${severityToken(f.severity)}))` }} />}
                    {f.title}
                    <span className="rounded-full px-1.5 py-px text-[10px] font-medium uppercase tracking-wide"
                          style={{ color: `hsl(var(${severityToken(f.severity)}))`, backgroundColor: `hsl(var(${severityToken(f.severity)}) / 0.12)` }}>
                      {severityLabel(f.severity)}
                    </span>
                  </p>
                  <p className="mt-1 text-xs text-muted-foreground">{f.explanation}</p>
                  <p className="mt-1 text-xs"><span className="font-medium">Do this:</span> <span className="text-muted-foreground">{f.suggested_action}</span></p>
                  <p className="mt-1 text-[11px] text-muted-foreground"><span className="font-medium">Setting:</span> <span className="break-all">{f.setting_path}</span></p>
                  <p className="text-[11px] text-muted-foreground"><span className="font-medium">Evidence:</span> {f.evidence}</p>
                </li>
              ))}
            </ul>
          )}

          {counts && counts.total > 0 && (
            <div className="space-y-2 rounded-md border border-primary/30 bg-primary/5 p-3">
              <p className="text-sm">
                This model may be fine, but the project settings are for another printer. Studio can
                prepare a U1 profile copy so Orca opens it with U1-compatible settings.
              </p>
              <Button size="sm" onClick={() => prepM.mutate()} disabled={prepM.isPending || !path}>
                {prepM.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <FilePlus className="h-4 w-4" />}
                Prepare U1 copy
              </Button>
              <p className="text-[11px] text-muted-foreground">Creates a new file. Your original is never modified.</p>
            </div>
          )}
          {prepM.isError && <p className="text-sm text-risk">Couldn't prepare a copy: {(prepM.error as Error).message}</p>}

          {prep && (
            <div className="space-y-3 rounded-md border border-border p-3">
              <p className="flex items-center gap-2 text-sm font-semibold text-stage-validate">
                <CheckCircle2 className="h-4 w-4" /> U1 profile copy created
              </p>
              <p className="truncate text-xs text-muted-foreground" title={prep.output_path}>
                Saved as <b>{prep.output_name}</b> · {prep.validated_ok ? "profile & settings updated" : "see notes"} (new file — original untouched).
              </p>
              <p className="flex items-start gap-1.5 rounded-md border border-doctor-cost/40 bg-doctor-cost/5 p-2 text-[11px] text-muted-foreground">
                <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-doctor-cost" />
                Layout isn't verified — Studio fixed settings/profile, not object placement. Open in
                Snapmaker Orca and use <b>Arrange all plates</b> before slicing; objects may sit outside a plate.
              </p>
              {prep.errors && prep.errors.length > 0 && (
                <ul className="space-y-1 text-xs text-muted-foreground">
                  {prep.errors.map((e: string, i: number) => <li key={i}>• {e}</li>)}
                </ul>
              )}
              <div className="flex flex-wrap items-center gap-2">
                {prep.output_path && <OrcaHandoff outputPath={prep.output_path} />}
                <Button size="sm" variant="secondary" onClick={() => copyPath(prep.output_path)}>
                  <Copy className="h-4 w-4" /> Copy path
                </Button>
                <Button size="sm" variant="secondary" asChild>
                  <Link to="/doctor/project"><Stethoscope className="h-4 w-4" /> Run Project Doctor</Link>
                </Button>
              </div>
              <p className="text-[11px] text-muted-foreground">Advisory — not a print-success guarantee. Studio does not slice; Orca does.</p>
            </div>
          )}

          <p className="flex items-start gap-1.5 rounded-md bg-muted/40 p-2 text-xs text-muted-foreground">
            <ShieldCheck className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {result.recommendation}
          </p>
          <p className="text-[11px] text-muted-foreground">
            Tip: see the{" "}
            <Link to="/help" className="text-primary hover:underline">troubleshooting checklist</Link>
            {" "}for more detail. <ArrowRight className="inline h-3 w-3" />
          </p>
          <p className="text-[11px] text-muted-foreground">
            Already printed and the result looks bad (not a file warning)? Try the{" "}
            <Link to="/print-quality" className="text-primary hover:underline">Print Quality Doctor</Link>.
          </p>
        </CardContent></Card>
      )}
    </div>
  );
}
