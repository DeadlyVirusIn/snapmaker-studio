import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Maximize2, FilePlus, Loader2, AlertTriangle, CheckCircle2, Info } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import { openModelDialog, scalePreview, scaleOptions, type ScaleResult, type ScaleOptionsResult } from "@/api";
import { SCALE_LADDER_COPY, recommendBlurb, isRecommended, isCaution, riskLabel, fmtDims, partLabel } from "@/lib/scaleOptions";

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
  const [opts, setOpts] = useState<ScaleOptionsResult | null>(null);
  const [copied, setCopied] = useState<number | null>(null);

  const m = useMutation({
    mutationFn: () => scalePreview(path!, pct),
    onSuccess: (d) => setRes(d),
  });

  const om = useMutation({
    mutationFn: () => scaleOptions(path!),
    onSuccess: (d) => setOpts(d),
  });

  async function pick() {
    const p = await openModelDialog();
    if (!p) return;
    setPath(p); setRes(null); setOpts(null);
  }

  async function copyScale(p: number) {
    try { await navigator.clipboard.writeText(String(p)); setCopied(p); setTimeout(() => setCopied(null), 1500); } catch { /* clipboard unavailable */ }
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

      {/* Size Options Ladder */}
      {path && (
        <Card><CardContent className="space-y-3 p-5">
          <div className="flex flex-wrap items-center gap-2">
            <p className="text-sm font-semibold">Size options for Snapmaker U1</p>
            <Button className="ml-auto" size="sm" variant="secondary"
              onClick={() => om.mutate()} disabled={om.isPending}>
              {om.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Maximize2 className="h-4 w-4" />} Show size options
            </Button>
          </div>

          {om.isError && <p className="text-sm text-risk">Couldn't read that file: {(om.error as Error).message}</p>}
          {opts && !opts.available && <p className="text-sm text-risk">{opts.reason}</p>}

          {opts?.available && opts.options && (
            <>
              <p className="text-sm">{recommendBlurb(opts)}</p>
              {opts.group_scaling_recommended && (
                <div className="flex items-start gap-2 rounded-md border border-border p-2.5 text-xs text-muted-foreground">
                  <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                  <span>{SCALE_LADDER_COPY.groupSame} {SCALE_LADDER_COPY.groupSeparate}</span>
                </div>
              )}
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="text-muted-foreground">
                    <tr>
                      <th className="py-1 pr-3">Scale</th>
                      {opts.current_parts?.map((p) => (
                        <th key={p.plate_index} className="py-1 pr-3">{partLabel(p as any)}</th>
                      ))}
                      <th className="py-1 pr-3">Fit</th>
                      <th className="py-1 pr-3">Recommendation</th>
                      <th className="py-1">Risk</th>
                    </tr>
                  </thead>
                  <tbody>
                    {opts.options.map((o) => {
                      const rec = isRecommended(o, opts);
                      const caution = isCaution(o);
                      return (
                        <tr key={o.label}
                          className={rec ? "bg-stage-validate/10 font-medium" : ""}
                          style={rec ? { boxShadow: "inset 2px 0 0 0 hsl(var(--stage-validate))" } : undefined}>
                          <td className="py-1.5 pr-3 align-top">
                            <button className="inline-flex items-center gap-1 underline-offset-2 hover:underline"
                              onClick={() => copyScale(o.scale_percent)} title="Copy scale %">
                              {o.scale_percent}% {copied === o.scale_percent && <span className="text-stage-validate">copied</span>}
                            </button>
                            {rec && <span className="ml-1 rounded bg-stage-validate/15 px-1 text-[10px] text-stage-validate">recommended</span>}
                          </td>
                          {o.dimensions_by_part.map((d, i) => (
                            <td key={i} className="py-1.5 pr-3 align-top">{fmtDims(d.dimensions)}</td>
                          ))}
                          <td className="py-1.5 pr-3 align-top">
                            {o.dimensions_by_part.every((d) => d.fits_build_volume) ? "Fits" : "Too big"}
                          </td>
                          <td className="py-1.5 pr-3 align-top">
                            {caution && <AlertTriangle className="mr-1 inline h-3 w-3 text-risk" />}{o.recommendation}
                          </td>
                          <td className="py-1.5 align-top">{riskLabel(o.risk_level)}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
              <ul className="space-y-1 text-xs text-muted-foreground">
                {opts.options.map((o) => (
                  <li key={o.label}><b>{o.label}:</b> {o.explanation}</li>
                ))}
                <li>{SCALE_LADDER_COPY.theoretical}</li>
                <li>{SCALE_LADDER_COPY.notGuarantee}</li>
              </ul>
            </>
          )}
        </CardContent></Card>
      )}
    </div>
  );
}
