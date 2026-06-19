import { Navigate, Link } from "react-router-dom";
import {
  Boxes, FileBox, Loader2, Sparkles, AlertTriangle, RotateCw, Wand2,
  CheckCircle2, Plus, Star, StarHalf, Palette, Layers, ChevronDown,
  Ruler, Gauge, ShieldCheck, Copy, Printer,
} from "lucide-react";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useSession } from "@/store/session";
import { insights as apiInsights, report as apiReport } from "@/api";
import { useOpenFile } from "@/hooks/useOpenFile";
import { useToast } from "@/store/toast";
import {
  readinessStars, familyLabel, verdictStatus, colorsLabel, partsLabel,
} from "@/lib/simple";

function Stars({ score }: { score: number | null | undefined }) {
  const { full, half, empty } = readinessStars(score);
  return (
    <span className="inline-flex items-center gap-0.5 text-repairable" aria-label={`Print readiness ${Math.round((score ?? 0) / 20 * 10) / 10} of 5`}>
      {Array.from({ length: full }).map((_, i) => <Star key={`f${i}`} className="h-5 w-5 fill-current" />)}
      {half && <StarHalf className="h-5 w-5 fill-current" />}
      {Array.from({ length: empty }).map((_, i) => <Star key={`e${i}`} className="h-5 w-5 opacity-30" />)}
    </span>
  );
}

export default function DesignInsights() {
  const file = useSession((s) => s.file);
  const doctor = useSession((s) => s.doctor);
  const convert = useSession((s) => s.convert);
  const runDoctor = useSession((s) => s.runDoctor);
  const runConvert = useSession((s) => s.runConvert);
  const openFile = useOpenFile();
  const showToast = useToast((s) => s.show);
  const [showDetails, setShowDetails] = useState(false);

  if (!file) return <Navigate to="/" replace />;

  const copyPath = (p: string) => {
    navigator.clipboard?.writeText(p).then(
      () => showToast("Path copied — paste it in your printer’s app"),
      () => showToast("Couldn’t copy the path"),
    );
  };

  const d = doctor.data;
  const TypeIcon = file.name.toLowerCase().endsWith(".stl") ? FileBox : Boxes;
  const status = d ? verdictStatus(d.verdict) : null;
  // Rich Project Intelligence (real geometry + materials), fetched read-only.
  const { data: ins } = useQuery({
    queryKey: ["insights", file.path],
    queryFn: () => apiInsights(file.path),
    enabled: doctor.status === "done",
  });
  const dims = ins?.dimensions_mm;
  // Validation Center: readiness + preservation report (read-only).
  const { data: rep } = useQuery({
    queryKey: ["report", file.path],
    queryFn: () => apiReport(file.path),
    enabled: doctor.status === "done",
  });
  const issues = [...(d?.validation_issues ?? []), ...(d?.compatibility_issues ?? [])];

  // ---- Done: it's ready ------------------------------------------------------
  if (convert.status === "done" && convert.data) {
    return (
      <div className="mx-auto max-w-xl">
        <Card>
          <CardContent className="flex flex-col items-center gap-4 p-8 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-ready/15 text-ready">
              <CheckCircle2 className="h-9 w-9" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Ready to print!</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                We made a print-ready copy of <b>{file.name}</b>. Your original is kept safe.
              </p>
            </div>
            <div className="w-full rounded-lg border border-border bg-muted/30 p-3 text-left text-sm">
              <p className="font-medium">{convert.data.output_name}</p>
              <p className="break-all text-xs text-muted-foreground">{convert.data.output_path}</p>
            </div>
            <div className="text-left text-sm text-muted-foreground">
              <p className="mb-1 font-medium text-foreground">What now?</p>
              <p>1. Copy the file path (or find it in the folder shown above)</p>
              <p>2. Open it in Snapmaker Orca to slice and print</p>
            </div>
            <div className="flex flex-wrap justify-center gap-2">
              <Button variant="secondary" onClick={() => copyPath(convert.data!.output_path)}>
                <Copy className="h-4 w-4" /> Copy path
              </Button>
              <Button variant="secondary" asChild>
                <Link to="/printers"><Printer className="h-4 w-4" /> View my U1</Link>
              </Button>
              <Button onClick={openFile}>
                <Plus className="h-4 w-4" /> Do another
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl space-y-4">
      {/* heading */}
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-muted-foreground">
          <TypeIcon className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <h2 className="truncate text-xl font-semibold tracking-tight">{file.name}</h2>
          <p className="text-xs text-muted-foreground">Let's see what's in your design.</p>
        </div>
      </div>

      {/* looking at it */}
      {doctor.status === "loading" && (
        <Card><CardContent className="flex items-center gap-2 p-6 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Looking at your design…
        </CardContent></Card>
      )}

      {doctor.status === "error" && (
        <Card><CardContent className="space-y-3 p-6">
          <p className="flex items-center gap-2 text-sm text-risk"><AlertTriangle className="h-4 w-4" /> We couldn't open this design.</p>
          <p className="text-sm text-muted-foreground">{doctor.error}</p>
          <Button variant="secondary" size="sm" onClick={runDoctor}><RotateCw className="h-4 w-4" /> Try again</Button>
        </CardContent></Card>
      )}

      {doctor.status === "done" && d && status && (
        <>
          {/* what's in this design */}
          <Card>
            <CardContent className="space-y-4 p-5">
              <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Step 1 · Understand</p>
              <div className="flex items-center gap-2 text-sm font-semibold"><Sparkles className="h-4 w-4 text-primary" /> What's in this design</div>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2"><FileBox className="h-4 w-4 text-muted-foreground" /> {familyLabel(d.family)}</li>
                {dims && <li className="flex items-center gap-2"><Ruler className="h-4 w-4 text-muted-foreground" /> {dims.x} × {dims.y} × {dims.z} mm</li>}
                {colorsLabel(d.filament_count) && <li className="flex items-center gap-2"><Palette className="h-4 w-4 text-muted-foreground" /> {colorsLabel(d.filament_count)}</li>}
                {partsLabel(d.object_count) && <li className="flex items-center gap-2"><Layers className="h-4 w-4 text-muted-foreground" /> {partsLabel(d.object_count)}{(ins?.plates ?? 0) > 1 ? ` · ${ins!.plates} plates` : ""}</li>}
                {ins?.complexity && <li className="flex items-center gap-2"><Gauge className="h-4 w-4 text-muted-foreground" /> {ins.complexity} complexity{ins.triangles ? ` · ${ins.triangles.toLocaleString()} triangles` : ""}</li>}
                {d.painted && <li className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-ready" /> painted areas kept</li>}
              </ul>
              {ins?.materials && ins.materials.length > 0 && (
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  {ins.materials.map((m, i) => (
                    <span key={i} className="inline-flex items-center gap-1 rounded-full border border-border px-2 py-0.5 text-xs">
                      <span className="h-3 w-3 rounded-full border border-border" style={{ backgroundColor: m.color }} />
                      {m.type ?? "filament"}
                    </span>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Validation Center — will it print + what's preserved/changes/at-risk */}
          {rep && (
            <Card>
              <CardContent className="space-y-4 p-5">
                <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Step 2 · Validate</p>
                <div className="flex items-center gap-2 text-sm font-semibold"><ShieldCheck className="h-4 w-4 text-primary" /> Validation Center</div>
                <p className="-mt-2 text-xs text-muted-foreground">Will it print on your U1 — and what we keep, change, or can’t carry over.</p>
                <ul className="space-y-1.5 text-sm">
                  {rep.checks.map((c, i) => (
                    <li key={i} className="flex items-start gap-2">
                      {c.status === "pass"
                        ? <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-ready" />
                        : <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-repairable" />}
                      <span><span className="font-medium">{c.name}</span> — <span className="text-muted-foreground">{c.detail}</span></span>
                    </li>
                  ))}
                </ul>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 text-xs">
                  <div>
                    <p className="mb-1 font-medium text-ready">Kept</p>
                    <ul className="space-y-1 text-muted-foreground">{rep.preserved.map((x, i) => <li key={i}>• {x}</li>)}</ul>
                  </div>
                  <div>
                    <p className="mb-1 font-medium">Changes</p>
                    <ul className="space-y-1 text-muted-foreground">{rep.changes.length ? rep.changes.map((x, i) => <li key={i}>• {x}</li>) : <li>• none</li>}</ul>
                  </div>
                  <div>
                    <p className="mb-1 font-medium text-repairable">At risk</p>
                    <ul className="space-y-1 text-muted-foreground">{rep.at_risk.length ? rep.at_risk.map((x, i) => <li key={i}>• {x}</li>) : <li>• nothing</li>}</ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* readiness */}
          <Card>
            <CardContent className="space-y-3 p-5">
              <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Step 3 · Prepare</p>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Print-Readiness</span>
                <Stars score={d.score} />
              </div>
              <p className={cn("flex items-center gap-2 text-sm",
                status.tone === "ready" ? "text-ready" : status.tone === "risk" ? "text-risk" : "text-repairable")}>
                <span>{status.icon}</span> {status.label}
              </p>

              {issues.length > 0 && (
                <div>
                  <button onClick={() => setShowDetails((v) => !v)} className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground">
                    <ChevronDown className={cn("h-3.5 w-3.5 transition-transform", showDetails && "rotate-180")} /> What needs fixing?
                  </button>
                  {showDetails && (
                    <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                      {issues.map((it: string, i: number) => (
                        <li key={i} className="flex items-start gap-2"><span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-repairable" />{it}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}

              <Button className="w-full" onClick={runConvert} disabled={convert.status === "loading"}>
                {convert.status === "loading" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wand2 className="h-4 w-4" />}
                {convert.status === "loading" ? "Getting it ready…" : "Get it ready"}
              </Button>
              <p className="text-center text-xs text-muted-foreground">We never change your original file.</p>

              {convert.status === "error" && (
                <p className="flex items-center justify-center gap-2 text-xs text-risk"><AlertTriangle className="h-3.5 w-3.5" /> {convert.error}</p>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
