import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Maximize2, FilePlus, Loader2, AlertTriangle, CheckCircle2, Info } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import { openModelDialog, scalePreview, type ScaleResult } from "@/api";

function recTone(rec?: string): { token: string; label: string } {
  if (rec === "not recommended") return { token: "--stage-input", label: "Not recommended" };
  if (rec === "caution") return { token: "--doctor-cost", label: "Caution" };
  return { token: "--stage-validate", label: "Likely safe" };
}

function dims(d?: { x: number; y: number; z: number }) {
  return d ? `${d.x.toFixed(1)} × ${d.y.toFixed(1)} × ${d.z.toFixed(1)} mm` : "—";
}

export default function ScaleDoctor() {
  const [path, setPath] = useState<string | null>(null);
  const [pct, setPct] = useState(100);
  const [res, setRes] = useState<ScaleResult | null>(null);

  const m = useMutation({
    mutationFn: () => scalePreview(path!, pct),
    onSuccess: (d) => setRes(d),
  });

  async function pick() {
    const p = await openModelDialog();
    if (!p) return;
    setPath(p); setRes(null);
  }

  const tone = recTone(res?.recommendation);

  return (
    <div className="space-y-6">
      <PageHeader icon={Maximize2} title="Scale Doctor"
        subtitle="Preview a uniform resize: size, U1 fit, and material/cost — read-only, no export." />

      <div className="flex items-start gap-2 rounded-md border border-border p-3 text-sm">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
        <span className="text-muted-foreground">Uniform scaling only. Studio previews the change — it does not resize or export your file.</span>
      </div>

      <Card><CardContent className="flex flex-wrap items-center gap-3 p-5">
        <Button variant="secondary" size="sm" onClick={pick}>
          <FilePlus className="h-4 w-4" /> {path ? "Choose another model" : "Open an STL or 3MF"}
        </Button>
        {path && <span className="truncate text-xs text-muted-foreground" title={path}>{path.split(/[\\/]/).pop()}</span>}
        <div className="ml-auto flex items-center gap-2">
          <label className="text-xs text-muted-foreground">Scale %</label>
          <input type="number" min={1} value={pct}
            onChange={(e) => setPct(Number(e.target.value) || 0)}
            className="w-24 rounded-md border border-border bg-background px-2 py-1 text-sm outline-none focus:border-primary" />
          <Button size="sm" onClick={() => m.mutate()} disabled={!path || pct <= 0 || m.isPending}>
            {m.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Maximize2 className="h-4 w-4" />} Preview
          </Button>
        </div>
      </CardContent></Card>

      {m.isError && <p className="text-sm text-risk">Couldn't read that file: {(m.error as Error).message}</p>}
      {res && !res.available && <p className="text-sm text-risk">{res.reason}</p>}

      {res?.available && (
        <Card><CardContent className="space-y-3 p-5">
          <p className="flex items-center gap-2 text-sm font-semibold"
             style={{ color: `hsl(var(${tone.token}))` }}>
            {res.recommendation === "not recommended" ? <AlertTriangle className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
            {tone.label}
          </p>
          <div className="grid gap-3 text-sm sm:grid-cols-2">
            <div><p className="text-xs text-muted-foreground">Original size</p><p>{dims(res.original_dimensions)}</p></div>
            <div><p className="text-xs text-muted-foreground">Scaled size ({res.scale_percent}%)</p><p>{dims(res.scaled_dimensions)}</p></div>
            <div><p className="text-xs text-muted-foreground">Fits U1 build volume</p>
              <p>{res.fits_build_volume ? "Yes" : "No — exceeds the 270 mm bed"}</p></div>
            <div><p className="text-xs text-muted-foreground">Material change</p>
              <p>{res.estimated_material_delta ? `${res.estimated_material_delta.grams >= 0 ? "+" : ""}${res.estimated_material_delta.grams} g` : "—"}
                {res.estimated_cost_delta?.amount != null ? ` · ${res.estimated_cost_delta.amount >= 0 ? "+" : ""}$${Math.abs(res.estimated_cost_delta.amount).toFixed(2)}` : ""}</p></div>
          </div>
          {res.scale_percent != null && (
            <p className="text-sm">
              {res.scale_percent >= 100 ? "Making it bigger" : "Making it smaller"}: about{" "}
              <b>{Math.pow(res.scale_percent / 100, 3).toFixed(res.scale_percent >= 100 ? 1 : 2)}×</b>{" "}
              the material at {res.scale_percent}% scale (volume estimate, not slicer-accurate).
            </p>
          )}
          {res.risks && res.risks.length > 0 && (
            <ul className="space-y-1 text-xs text-muted-foreground">
              {res.risks.map((r, i) => (
                <li key={i} className="flex items-start gap-1.5"><AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {r}</li>
              ))}
            </ul>
          )}
          <p className="text-xs text-muted-foreground">{res.explanation}</p>
        </CardContent></Card>
      )}
    </div>
  );
}
