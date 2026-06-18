import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  UploadCloud, Stethoscope, Wand2, GitCompare, Plus, ArrowRight,
  FileBox, Boxes, Loader2, CheckCircle2, AlertTriangle, RotateCw,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/badge";
import type { Verdict } from "@/components/ui/badge";
import { library } from "@/api";
import type { LibraryProject } from "@/api";
import { useSession } from "@/store/session";
import { comingSoon } from "@/store/toast";
import { useOpenFile } from "@/hooks/useOpenFile";

const QUICK = [
  { label: "Check compatibility", icon: Stethoscope, hint: "Run Doctor", live: true },
  { label: "Convert STL", icon: UploadCloud, hint: "STL → U1", live: true },
  { label: "Repair 3MF", icon: Wand2, hint: "Fix presets", live: true },
  { label: "Compare files", icon: GitCompare, hint: "Diff versions", live: true },
];

function timeAgo(iso: string | null): string {
  if (!iso) return "";
  const t = new Date(iso).getTime();
  if (Number.isNaN(t)) return "";
  const s = Math.max(0, Math.floor((Date.now() - t) / 1000));
  if (s < 60) return "just now";
  const m = Math.floor(s / 60); if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60); if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24); if (d < 7) return `${d}d ago`;
  return new Date(iso).toLocaleDateString();
}

function activityText(p: LibraryProject): string {
  if (p.last_action === "convert") return `Converted ${p.name} to U1`;
  return `Diagnosed ${p.name}${p.verdict ? ` — ${p.verdict[0]}${p.verdict.slice(1).toLowerCase()}` : ""}`;
}

export default function Dashboard() {
  const openFile = useOpenFile();
  const nav = useNavigate();
  const setFile = useSession((s) => s.setFile);

  const { data, status, error, refetch } = useQuery({ queryKey: ["library"], queryFn: () => library() });
  const projects = data ?? [];
  const recent = projects.slice(0, 3);
  const ready = projects.filter((p) => p.verdict === "READY").length;
  const needsWork = projects.length - ready;

  const openProject = (p: LibraryProject) => { setFile(p.source_path); nav("/workspace"); };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Welcome back.</h2>
        <p className="text-muted-foreground">Make any model Snapmaker U1-ready — fully on your machine.</p>
      </div>

      <Card onClick={openFile} className="cursor-pointer border-dashed bg-gradient-to-b from-muted/40 to-transparent transition-colors hover:border-primary/40">
        <CardContent className="flex flex-col items-center justify-center gap-4 py-16 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary ring-1 ring-primary/20">
            <UploadCloud className="h-7 w-7" />
          </div>
          <div>
            <p className="text-base font-medium">Drop a model to begin</p>
            <p className="text-sm text-muted-foreground">Supports <b>.stl</b> and <b>.3mf</b> · nothing leaves your computer</p>
          </div>
          <Button onClick={(e) => { e.stopPropagation(); openFile(); }}>
            <Plus className="h-4 w-4" /> Open a model
          </Button>
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {QUICK.map((q) => (
          <Card key={q.label} onClick={() => (q.live ? openFile() : comingSoon(q.label))} className="cursor-pointer transition-all hover:border-primary/40 hover:shadow-md">
            <CardContent className="flex flex-col gap-2 p-4">
              <div className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 text-primary">
                <q.icon className="h-5 w-5" />
              </div>
              <span className="text-sm font-medium leading-tight">{q.label}</span>
              <span className="text-xs text-muted-foreground">{q.hint}</span>
            </CardContent>
          </Card>
        ))}
      </div>

      {status === "error" && (
        <Card>
          <CardContent className="flex items-center gap-2 p-4 text-sm">
            <AlertTriangle className="h-4 w-4 text-risk" />
            <span className="text-muted-foreground">Couldn’t load your library: {String((error as Error)?.message ?? error)}</span>
            <Button variant="secondary" size="sm" className="ml-auto" onClick={() => refetch()}>
              <RotateCw className="h-4 w-4" /> Retry
            </Button>
          </CardContent>
        </Card>
      )}

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold">Continue working</h3>
          <Link to="/projects" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground">
            All projects <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
        {status === "pending" ? (
          <div className="flex items-center gap-2 py-6 text-sm text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" /> Loading…</div>
        ) : status === "error" ? (
          <div className="py-6 text-sm text-muted-foreground">Library unavailable — see the error above.</div>
        ) : recent.length > 0 ? (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            {recent.map((p) => {
              const Icon = p.name.toLowerCase().endsWith(".stl") ? FileBox : Boxes;
              return (
                <Card key={p.id} role="button" tabIndex={0}
                  onClick={() => openProject(p)}
                  onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openProject(p); } }}
                  className="group cursor-pointer transition-all hover:border-primary/40 hover:shadow-md">
                  <CardContent className="space-y-3 p-4">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex min-w-0 items-center gap-2.5">
                        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground group-hover:text-foreground">
                          <Icon className="h-[18px] w-[18px]" />
                        </span>
                        <span className="truncate font-medium">{p.name}</span>
                      </div>
                      {p.verdict && <StatusBadge verdict={p.verdict as Verdict} />}
                    </div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{(p.source_family ?? "project")}{p.filament_count != null ? ` · ${p.filament_count} filament${p.filament_count === 1 ? "" : "s"}` : ""}</span>
                      <span>{timeAgo(p.updated_at)}</span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        ) : (
          <Card>
            <CardContent className="flex flex-col items-center justify-center gap-1 py-10 text-center">
              <p className="text-sm font-medium">No projects yet</p>
              <p className="text-sm text-muted-foreground">Open a model above — it’ll appear here once diagnosed or converted.</p>
            </CardContent>
          </Card>
        )}
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardContent className="p-5">
            <h3 className="mb-3 text-sm font-semibold">Activity</h3>
            {status === "pending" ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" /> Loading…</div>
            ) : status === "error" ? (
              <p className="text-sm text-muted-foreground">Activity unavailable.</p>
            ) : projects.length > 0 ? (
              <ul className="space-y-2 text-sm">
                {projects.slice(0, 6).map((p) => (
                  <li key={p.id} className="flex items-center gap-2 text-muted-foreground">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                    <span className="truncate text-foreground">{activityText(p)}</span>
                    <span className="ml-auto shrink-0 text-xs">{timeAgo(p.updated_at)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">No activity yet. Your conversions and checks will show up here.</p>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <h3 className="mb-3 text-sm font-semibold">Library</h3>
            <div className="space-y-1 text-sm text-muted-foreground">
              {status === "error" ? (
                <p>Library unavailable.</p>
              ) : (
                <>
                  <p><span className="text-2xl font-semibold text-foreground">{projects.length}</span> project{projects.length === 1 ? "" : "s"}</p>
                  {projects.length > 0 ? (
                    <p className="flex items-center gap-1.5">
                      <CheckCircle2 className="h-3.5 w-3.5 text-ready" />{ready} U1-ready · {needsWork} need work
                    </p>
                  ) : (
                    <p>Nothing indexed yet.</p>
                  )}
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
