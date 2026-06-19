import { Navigate } from "react-router-dom";
import {
  FileBox, Boxes, Wand2, FolderOpen, RotateCw, CheckCircle2,
  AlertTriangle, Loader2, Save, GitCompare,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/ui/badge";
import type { Verdict } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useSession } from "@/store/session";
import { useOpenFile } from "@/hooks/useOpenFile";
import { StrategyPicker } from "@/components/StrategyPicker";
import { useState } from "react";

function Spinner() {
  return <Loader2 className="h-4 w-4 animate-spin" />;
}

export default function LiveWorkspace() {
  const file = useSession((s) => s.file);
  const [strategy, setStrategy] = useState("balanced");  // default Balanced
  const doctor = useSession((s) => s.doctor);
  const convert = useSession((s) => s.convert);
  const runDoctor = useSession((s) => s.runDoctor);
  const runConvert = useSession((s) => s.runConvert);
  const diff = useSession((s) => s.diff);
  const runDiff = useSession((s) => s.runDiff);
  const openFile = useOpenFile();

  // No file in session (e.g. hard refresh) — send the user back to start.
  if (!file) return <Navigate to="/" replace />;

  const d = doctor.data;
  const TypeIcon = file.ext === "stl" ? FileBox : Boxes;
  const converting = convert.status === "loading";

  return (
    <div className="space-y-5">
      {/* header */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-muted-foreground">
          <TypeIcon className="h-5 w-5" />
        </div>
        <div className="min-w-0">
          <h2 className="truncate text-xl font-semibold tracking-tight">{file.name}</h2>
          <p className="truncate text-xs text-muted-foreground">{file.path}</p>
        </div>
        {doctor.status === "done" && d?.verdict && <StatusBadge verdict={d.verdict as Verdict} />}
        <div className="ml-auto flex gap-2">
          <Button variant="secondary" size="sm" onClick={openFile}>
            <FolderOpen className="h-4 w-4" /> Open another
          </Button>
          <Button onClick={runConvert} disabled={converting || doctor.status === "loading"}>
            {converting ? <Spinner /> : <Wand2 className="h-4 w-4" />} Make U1-ready
          </Button>
        </div>
      </div>

      {doctor.status === "done" && (
        <Card>
          <CardContent className="p-5">
            <StrategyPicker filePath={file.path} mode="advanced" value={strategy} onChange={setStrategy} />
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_300px]">
        {/* Doctor (left) */}
        <div className="space-y-4">
          {doctor.status === "loading" && (
            <Card>
              <CardContent className="space-y-3 p-6">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Spinner /> Analyzing compatibility…
                </div>
                <Skeleton className="h-20" />
                <Skeleton className="h-4 w-2/3" />
              </CardContent>
            </Card>
          )}

          {doctor.status === "error" && (
            <Card>
              <CardContent className="space-y-3 p-6">
                <div className="flex items-center gap-2 font-medium text-risk">
                  <AlertTriangle className="h-5 w-5" /> Couldn’t analyze this file
                </div>
                <p className="text-sm text-muted-foreground">{doctor.error}</p>
                <Button variant="secondary" size="sm" onClick={runDoctor}>
                  <RotateCw className="h-4 w-4" /> Retry
                </Button>
              </CardContent>
            </Card>
          )}

          {doctor.status === "done" && d && (
            <>
              <Card>
                <CardContent className="flex items-center gap-5 p-6">
                  <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full border-4 border-primary/30 text-2xl font-bold text-primary">
                    {d.score ?? "—"}
                  </div>
                  <div className="space-y-1.5">
                    <StatusBadge verdict={d.verdict as Verdict} />
                    <p className="text-sm text-muted-foreground">{d.recommended_action}</p>
                  </div>
                </CardContent>
              </Card>

              {(d.compatibility_issues?.length || d.validation_issues?.length) ? (
                <Card>
                  <CardContent className="p-5">
                    <h3 className="mb-3 text-sm font-semibold">Issues found</h3>
                    <ul className="space-y-2 text-sm">
                      {[...(d.validation_issues ?? []), ...(d.compatibility_issues ?? [])].map(
                        (issue: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-muted-foreground">
                            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-repairable" />
                            <span>{issue}</span>
                          </li>
                        )
                      )}
                    </ul>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="flex items-center gap-2 p-5 text-sm">
                    <CheckCircle2 className="h-4 w-4 text-ready" /> No compatibility issues found.
                  </CardContent>
                </Card>
              )}
            </>
          )}

          {/* Convert outcome */}
          {convert.status === "loading" && (
            <Card>
              <CardContent className="flex items-center gap-2 p-5 text-sm text-muted-foreground">
                <Spinner /> Preparing and saving a U1-ready 3MF…
              </CardContent>
            </Card>
          )}
          {convert.status === "done" && convert.data && (
            <Card>
              <CardContent className="space-y-2 p-5">
                <div className="flex items-center gap-2 font-medium text-ready">
                  <Save className="h-5 w-5" /> Saved U1-ready project
                </div>
                <p className="text-sm">{convert.data.output_name}</p>
                <p className="break-all text-xs text-muted-foreground">{convert.data.output_path}</p>
                {convert.data.validated_ok ? (
                  <p className="flex items-center gap-1.5 text-xs text-ready">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Validated — ready to slice in Snapmaker Orca
                  </p>
                ) : (
                  <p className="flex items-center gap-1.5 text-xs text-repairable">
                    <AlertTriangle className="h-3.5 w-3.5" /> Saved, but validation reported issues
                  </p>
                )}
              </CardContent>
            </Card>
          )}
          {convert.status === "error" && (
            <Card>
              <CardContent className="space-y-3 p-5">
                <div className="flex items-center gap-2 font-medium text-risk">
                  <AlertTriangle className="h-5 w-5" /> Preparation failed
                </div>
                <p className="text-sm text-muted-foreground">{convert.error}</p>
                <Button variant="secondary" size="sm" onClick={runConvert}>
                  <RotateCw className="h-4 w-4" /> Retry
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Compare: original ↔ converted (only once an output exists) */}
          {convert.status === "done" && (
            <Card>
              <CardContent className="p-5">
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                  <GitCompare className="h-4 w-4" /> Compare — original ↔ U1-ready
                </div>
                {file.ext === "stl" && (
                  <p className="text-sm text-muted-foreground">
                    Built a native Snapmaker U1 project from your STL — there’s no source project to compare against.
                  </p>
                )}
                {file.ext !== "stl" && diff.status === "idle" && (
                  <p className="text-sm text-muted-foreground">Comparison runs automatically after conversion.</p>
                )}
                {diff.status === "loading" && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground"><Spinner /> Comparing…</div>
                )}
                {diff.status === "error" && (
                  <div className="space-y-2">
                    <p className="flex items-center gap-2 text-sm text-risk"><AlertTriangle className="h-4 w-4" /> {diff.error}</p>
                    <Button variant="secondary" size="sm" onClick={runDiff}><RotateCw className="h-4 w-4" /> Retry compare</Button>
                  </div>
                )}
                {diff.status === "done" && diff.data && (
                  <div className="space-y-4">
                    <div className={cn("flex items-center gap-2 text-sm", diff.data.geometry_changed ? "text-repairable" : "text-ready")}>
                      {diff.data.geometry_changed ? <AlertTriangle className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
                      {diff.data.geometry_changed ? "Geometry changed" : "Geometry identical — mesh preserved"}
                    </div>
                    <div className="overflow-hidden rounded-md border border-border text-sm">
                      <div className="grid grid-cols-[1fr_auto_auto] gap-3 border-b border-border bg-muted/40 px-3 py-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        <span>Metric</span><span>Original</span><span>U1-ready</span>
                      </div>
                      {([["Objects", "object_count"], ["Plates", "plate_count"], ["Filaments", "filament_count"], ["Painted △", "painted_triangles"]] as [string, string][]).map(([label, key]) => {
                        const v = diff.data[key] || [0, 0];
                        return (
                          <div key={key} className="grid grid-cols-[1fr_auto_auto] gap-3 px-3 py-2">
                            <span className="font-medium">{label}</span>
                            <span className="text-muted-foreground">{v[0]}</span>
                            <span className={cn(v[0] !== v[1] && "font-medium text-foreground")}>{v[1]}</span>
                          </div>
                        );
                      })}
                    </div>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="rounded-md border border-border p-3"><p className="text-xs text-muted-foreground">Parts</p><p>+{diff.data.parts_added?.length || 0} / −{diff.data.parts_removed?.length || 0}</p></div>
                      <div className="rounded-md border border-border p-3"><p className="text-xs text-muted-foreground">Settings normalized</p><p>{diff.data.settings_changed?.length || 0} changed · +{diff.data.settings_added?.length || 0} / −{diff.data.settings_removed?.length || 0}</p></div>
                    </div>
                    {diff.data.settings_changed?.length > 0 && (
                      <div>
                        <p className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">Normalization results</p>
                        <ul className="space-y-1 text-xs">
                          {diff.data.settings_changed.slice(0, 8).map((c: any, i: number) => (
                            <li key={i} className="flex gap-2"><span className="font-mono text-muted-foreground">{c.key}</span><span className="truncate">{String(c.old).slice(0, 18)} → <span className="text-ready">{String(c.new).slice(0, 18)}</span></span></li>
                          ))}
                          {diff.data.settings_changed.length > 8 && <li className="text-muted-foreground">+{diff.data.settings_changed.length - 8} more</li>}
                        </ul>
                      </div>
                    )}
                    <div className={cn("flex items-center gap-1.5 text-xs", convert.data?.validated_ok ? "text-ready" : "text-repairable")}>
                      {convert.data?.validated_ok ? <CheckCircle2 className="h-3.5 w-3.5" /> : <AlertTriangle className="h-3.5 w-3.5" />}
                      Validation: {convert.data?.validated_ok ? "passed — U1-clean" : "issues remain"}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Source inspector (right) */}
        <aside>
          <Card>
            <CardContent className="space-y-2 p-4 text-sm">
              <div className="flex items-center gap-2 font-medium"><FileBox className="h-4 w-4" /> Source</div>
              <dl className="space-y-1 text-muted-foreground">
                <div className="flex justify-between"><dt>Type</dt><dd className="text-foreground">{file.ext.toUpperCase()}</dd></div>
                {doctor.status === "done" && d && (
                  <>
                    <div className="flex justify-between"><dt>U1 compatible</dt><dd className="text-foreground">{d.is_compatible ? "yes" : "no"}</dd></div>
                    {d.filament_count != null && <div className="flex justify-between"><dt>Filaments</dt><dd className="text-foreground">{d.filament_count}</dd></div>}
                    {d.score != null && <div className="flex justify-between"><dt>Score</dt><dd className="text-foreground">{d.score}</dd></div>}
                  </>
                )}
              </dl>
              <p className="pt-1 text-xs text-muted-foreground">Originals are never overwritten.</p>
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
}
