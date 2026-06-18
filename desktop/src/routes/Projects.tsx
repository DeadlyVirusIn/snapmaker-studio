import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Search, FolderKanban, FileBox, Boxes, Loader2, AlertTriangle, Trash2, RotateCw,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/badge";
import type { Verdict } from "@/components/ui/badge";
import { library, libraryDelete } from "@/api";
import type { LibraryProject } from "@/api";
import { useSession } from "@/store/session";

const FILTERS: { label: string; match: (v: string | null) => boolean }[] = [
  { label: "All", match: () => true },
  { label: "U1-ready", match: (v) => v === "READY" },
  { label: "Needs work", match: (v) => v !== "READY" },
];

function fmtDate(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "" : d.toLocaleDateString();
}

function LibraryCard({ p, onOpen, onDelete }: {
  p: LibraryProject; onOpen: () => void; onDelete: () => void;
}) {
  const Icon = p.name.toLowerCase().endsWith(".stl") ? FileBox : Boxes;
  return (
    <Card className="group transition-all hover:border-primary/40 hover:shadow-md">
      <CardContent className="space-y-3 p-4">
        <div className="flex items-start justify-between gap-2">
          <button
            onClick={onOpen}
            className="flex min-w-0 items-center gap-2.5 text-left focus-visible:outline-none"
            title={p.source_path}
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground group-hover:text-foreground">
              <Icon className="h-[18px] w-[18px]" />
            </span>
            <span className="truncate font-medium">{p.name}</span>
          </button>
          {p.verdict && <StatusBadge verdict={p.verdict as Verdict} />}
        </div>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>
            {(p.source_family ?? "project")}
            {p.filament_count != null && ` · ${p.filament_count} filament${p.filament_count === 1 ? "" : "s"}`}
          </span>
          <span>{fmtDate(p.updated_at)}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">
            {p.output_path ? "U1 project saved" : `Last: ${p.last_action ?? "—"}`}
          </span>
          <button
            onClick={onDelete}
            className="rounded p-1 text-muted-foreground opacity-0 transition hover:text-risk group-hover:opacity-100"
            title="Remove from library (keeps your files)"
            aria-label={`Remove ${p.name} from library`}
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </CardContent>
    </Card>
  );
}

export default function Projects() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState(0);
  const nav = useNavigate();
  const setFile = useSession((s) => s.setFile);
  const qc = useQueryClient();

  const { data, status, error, refetch, isFetching } = useQuery({
    queryKey: ["library", query],
    queryFn: () => library(query),
  });

  const del = useMutation({
    mutationFn: (id: number) => libraryDelete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["library"] }),
  });

  const shown = useMemo(
    () => (data ?? []).filter((p) => FILTERS[filter].match(p.verdict)),
    [data, filter]
  );

  const openProject = (p: LibraryProject) => {
    setFile(p.source_path);
    nav("/workspace");
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Projects</h2>
          <p className="text-sm text-muted-foreground">
            {status === "success"
              ? `${data?.length ?? 0} project${(data?.length ?? 0) === 1 ? "" : "s"} in your library.`
              : "Your converted and diagnosed files."}
          </p>
        </div>
        <Button className="ml-auto" variant="secondary" size="sm" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? <Loader2 className="h-4 w-4 animate-spin" /> : <RotateCw className="h-4 w-4" />} Refresh
        </Button>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex h-9 min-w-[220px] flex-1 items-center gap-2 rounded-md border border-border bg-card px-3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search projects…"
            className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>
        <div className="flex gap-1">
          {FILTERS.map((f, i) => (
            <Button key={f.label} variant={filter === i ? "primary" : "secondary"} size="sm" onClick={() => setFilter(i)}>
              {f.label}
            </Button>
          ))}
        </div>
      </div>

      {status === "pending" && (
        <div className="flex items-center gap-2 py-16 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading your library…
        </div>
      )}

      {status === "error" && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center gap-2 py-16 text-center">
            <AlertTriangle className="h-7 w-7 text-risk" />
            <p className="font-medium">Couldn’t load your library</p>
            <p className="text-sm text-muted-foreground">{String((error as Error)?.message ?? error)}</p>
            <Button variant="secondary" size="sm" onClick={() => refetch()}>
              <RotateCw className="h-4 w-4" /> Retry
            </Button>
          </CardContent>
        </Card>
      )}

      {status === "success" && shown.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          {shown.map((p) => (
            <LibraryCard key={p.id} p={p} onOpen={() => openProject(p)} onDelete={() => del.mutate(p.id)} />
          ))}
        </div>
      )}

      {status === "success" && shown.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center gap-2 py-16 text-center">
            <FolderKanban className="h-7 w-7 text-muted-foreground" />
            {(data?.length ?? 0) === 0 && !query ? (
              <>
                <p className="font-medium">Your library is empty</p>
                <p className="text-sm text-muted-foreground">
                  Open or convert a file and it’ll show up here automatically.
                </p>
                <Button size="sm" onClick={() => nav("/")}>Get started</Button>
              </>
            ) : (
              <>
                <p className="font-medium">No matching projects</p>
                <p className="text-sm text-muted-foreground">Try a different search or filter.</p>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
