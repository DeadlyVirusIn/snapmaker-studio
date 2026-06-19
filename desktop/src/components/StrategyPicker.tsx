import { useQuery } from "@tanstack/react-query";
import { Sparkles, ShieldCheck, AlertTriangle, Info } from "lucide-react";
import { cn } from "@/lib/utils";
import { strategies as apiStrategies, strategyRecommend } from "@/api";

// Print Strategy selector. Simple Mode shows names + plain-language explanations only
// (no raw slicer terms). Advanced Mode also reveals the actual applied settings.
// Studio recommends; Snapmaker Orca still slices.
export function StrategyPicker({
  filePath, mode, value, onChange,
}: {
  filePath: string;
  mode: "simple" | "advanced";
  value: string;
  onChange: (id: string) => void;
}) {
  const list = useQuery({ queryKey: ["strategies"], queryFn: apiStrategies });
  const rec = useQuery({
    queryKey: ["strategy-rec", filePath],
    queryFn: () => strategyRecommend(filePath),
  });

  const strategies = list.data?.strategies ?? [];
  const categories = list.data?.categories ?? {};
  const recommended = rec.data?.recommended;
  const warnings = rec.data?.warnings ?? [];

  if (!strategies.length) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <Sparkles className="h-4 w-4 text-primary" /> Print strategy
      </div>

      {rec.data?.reason && (
        <p className="flex items-start gap-1.5 rounded-md bg-primary/5 px-3 py-2 text-xs text-muted-foreground">
          <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
          <span>{rec.data.reason} <span className="opacity-70">({rec.data.estimated_note})</span></span>
        </p>
      )}

      <div className="space-y-2">
        {strategies.map((s) => {
          const selected = value === s.id;
          const isRec = recommended === s.id;
          return (
            <button
              key={s.id}
              onClick={() => onChange(s.id)}
              className={cn(
                "w-full rounded-lg border p-3 text-left transition-colors",
                selected ? "border-primary bg-primary/5" : "border-border hover:bg-muted/50"
              )}
            >
              <div className="flex items-center gap-2">
                <span className={cn("flex h-4 w-4 shrink-0 items-center justify-center rounded-full border",
                  selected ? "border-primary" : "border-muted-foreground/40")}>
                  {selected && <span className="h-2 w-2 rounded-full bg-primary" />}
                </span>
                <span className="text-sm font-medium">{s.name}</span>
                {isRec && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-ready/10 px-2 py-0.5 text-[11px] font-semibold text-ready">
                    <ShieldCheck className="h-3 w-3" /> Recommended
                  </span>
                )}
              </div>
              <p className="mt-1 pl-6 text-xs text-muted-foreground">{s.explanation}</p>

              {/* Advanced Mode only: the actual applied settings. */}
              {mode === "advanced" && selected && Object.keys(s.settings).length > 0 && (
                <div className="mt-2 grid grid-cols-1 gap-1 pl-6 sm:grid-cols-2">
                  {Object.entries(s.settings).map(([k, v]) => (
                    <div key={k} className="flex items-center justify-between gap-2 rounded bg-muted/60 px-2 py-1 text-[11px]">
                      <span className="text-muted-foreground" title={k}>{categories[k] ?? k}</span>
                      <code className="font-mono">{v}</code>
                    </div>
                  ))}
                </div>
              )}
              {mode === "advanced" && selected && Object.keys(s.settings).length === 0 && (
                <p className="mt-2 pl-6 text-[11px] text-muted-foreground">No automatic overrides — edit raw values in Snapmaker Orca.</p>
              )}
            </button>
          );
        })}
      </div>

      {warnings.map((w, i) => (
        <p key={i} className="flex items-start gap-1.5 text-xs text-repairable">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {w}
        </p>
      ))}

      <p className="text-[11px] text-muted-foreground">
        Studio recommends a strategy — <b>Snapmaker Orca still does the slicing</b>. In Advanced Mode you can see and tweak the exact settings.
      </p>
    </div>
  );
}
