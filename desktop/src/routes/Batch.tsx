import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Layers, FilePlus, Play, X, Loader2, CheckCircle2, AlertTriangle, FileBox, Boxes,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader, EmptyState } from "@/components/ui/layout";
import { cn } from "@/lib/utils";
import { batchStart, batchStatus, openModelsDialog } from "@/api";
import type { BatchItem } from "@/api";

function baseName(p: string): string {
  return p.split(/[\\/]/).pop() || p;
}

function StatusDot({ status }: { status: BatchItem["status"] }) {
  if (status === "done") return <CheckCircle2 className="h-4 w-4 text-ready" />;
  if (status === "error") return <AlertTriangle className="h-4 w-4 text-risk" />;
  if (status === "running") return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
  return <span className="h-2 w-2 rounded-full bg-muted-foreground/40" />;
}

export default function Batch() {
  const [staged, setStaged] = useState<string[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [startError, setStartError] = useState<string | null>(null);

  const { data: job, isError, error } = useQuery({
    queryKey: ["batch", jobId],
    queryFn: () => batchStatus(jobId as string),
    enabled: !!jobId,
    retry: 1,
    // Poll while running; stop once finished OR the job/worker reports an error.
    refetchInterval: (q) => {
      const d = q.state.data;
      if (q.state.status === "error" || d?.status === "error" || d?.result?.finished) return false;
      return 400;
    },
  });

  const result = job?.result ?? null;
  const failed = isError || job?.status === "error";
  // Never stay "running" forever: a polling/worker error releases the UI.
  const running = !!jobId && !failed && !result?.finished;
  const pollError = failed
    ? (job?.error ?? String((error as Error)?.message ?? "batch status unavailable"))
    : null;

  async function addFiles() {
    setStartError(null);
    const picked = await openModelsDialog();
    if (picked.length) {
      setStaged((prev) => Array.from(new Set([...prev, ...picked])));
    }
  }

  async function start() {
    if (!staged.length) return;
    setStartError(null);
    try {
      const { job_id } = await batchStart(staged);
      setJobId(job_id);
    } catch (e: any) {
      setStartError(String(e?.message ?? e));
    }
  }

  function clearAll() {
    setStaged([]);
    setJobId(null);
    setStartError(null);
  }

  const pct = result && result.total
    ? Math.round(((result.done + result.failed) / result.total) * 100)
    : 0;

  return (
    <div className="space-y-6">
      <PageHeader
        icon={Layers}
        title="Batch convert"
        subtitle="Make a whole folder of designs U1-ready in one pass. Originals are never overwritten."
        actions={
          <>
            <Button variant="secondary" size="sm" onClick={addFiles} disabled={running}>
              <FilePlus className="h-4 w-4" /> Add files
            </Button>
            {!jobId ? (
              <Button size="sm" onClick={start} disabled={!staged.length}>
                <Play className="h-4 w-4" /> Convert {staged.length || ""}
              </Button>
            ) : (
              <Button variant="secondary" size="sm" onClick={clearAll} disabled={running}>
                <X className="h-4 w-4" /> {running ? "Working…" : "Clear"}
              </Button>
            )}
          </>
        }
      />

      {(startError || pollError) && (
        <Card>
          <CardContent className="flex items-center gap-2 p-4 text-sm text-risk">
            <AlertTriangle className="h-4 w-4" />
            {startError ?? `Batch interrupted: ${pollError}`}
            {pollError && (
              <Button variant="secondary" size="sm" className="ml-auto" onClick={clearAll}>
                <X className="h-4 w-4" /> Clear
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Progress */}
      {result && (
        <Card>
          <CardContent className="space-y-3 p-5">
            <div className="flex items-center justify-between text-sm">
              <span className="font-medium">
                {result.finished ? "Done" : "Converting…"} {result.done + result.failed}/{result.total}
              </span>
              <span className="text-muted-foreground">
                {result.done} ok{result.failed ? ` · ${result.failed} failed` : ""}
              </span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
              <div
                className={cn("h-full transition-all", result.failed ? "bg-repairable" : "bg-ready")}
                style={{ width: `${pct}%` }}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Queue */}
      {(staged.length > 0 || result) ? (
        <Card>
          <CardContent className="p-0">
            <ul className="divide-y divide-border">
              {(result ? result.items : staged.map((path) => ({
                path, status: "pending" as const,
                output_path: null, output_name: null, validated_ok: null, error: null,
              }))).map((it, i) => {
                const Icon = it.path.toLowerCase().endsWith(".stl") ? FileBox : Boxes;
                return (
                  <li key={i} className="flex items-center gap-3 px-4 py-2.5 text-sm">
                    <StatusDot status={it.status} />
                    <Icon className="h-4 w-4 shrink-0 text-muted-foreground" />
                    <span className="min-w-0 flex-1 truncate" title={it.path}>{baseName(it.path)}</span>
                    {it.status === "done" && it.output_name && (
                      <span className={cn("shrink-0 text-xs", it.validated_ok ? "text-ready" : "text-repairable")}>
                        {it.validated_ok ? "U1-ready" : "saved"}
                      </span>
                    )}
                    {it.status === "error" && (
                      <span className="shrink-0 truncate text-xs text-risk" title={it.error ?? ""}>
                        {it.error ?? "failed"}
                      </span>
                    )}
                    {!result && (
                      <button
                        onClick={() => setStaged((prev) => prev.filter((p) => p !== it.path))}
                        className="shrink-0 rounded p-1 text-muted-foreground hover:text-risk"
                        aria-label={`Remove ${baseName(it.path)}`}
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                    )}
                  </li>
                );
              })}
            </ul>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              icon={Layers}
              title="Convert a whole batch at once"
              description="Queue any number of .stl / .3mf files and Studio makes a clean, validated U1 project for each — your originals stay untouched."
              action={<Button size="sm" onClick={addFiles}><FilePlus className="h-4 w-4" /> Add files</Button>}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
