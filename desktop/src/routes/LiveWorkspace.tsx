import { Navigate } from "react-router-dom";
import {
  FileBox, Boxes, Wand2, FolderOpen, RotateCw, CheckCircle2,
  AlertTriangle, Loader2, Save,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/ui/badge";
import type { Verdict } from "@/components/ui/badge";
import { useSession } from "@/store/session";
import { useOpenFile } from "@/hooks/useOpenFile";

function Spinner() {
  return <Loader2 className="h-4 w-4 animate-spin" />;
}

export default function LiveWorkspace() {
  const file = useSession((s) => s.file);
  const doctor = useSession((s) => s.doctor);
  const convert = useSession((s) => s.convert);
  const runDoctor = useSession((s) => s.runDoctor);
  const runConvert = useSession((s) => s.runConvert);
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
                <Spinner /> Converting and saving a U1-ready 3MF…
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
                  <AlertTriangle className="h-5 w-5" /> Conversion failed
                </div>
                <p className="text-sm text-muted-foreground">{convert.error}</p>
                <Button variant="secondary" size="sm" onClick={runConvert}>
                  <RotateCw className="h-4 w-4" /> Retry
                </Button>
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
