import { useMemo, useState } from "react";
import { Search, Plus, FolderKanban } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ProjectCard } from "@/components/ProjectCard";
import type { Verdict } from "@/components/ui/badge";
import { MOCK_PROJECTS } from "@/data/mock";
import { comingSoon } from "@/store/toast";

const FILTERS: { label: string; match: (v: Verdict) => boolean }[] = [
  { label: "All", match: () => true },
  { label: "U1-ready", match: (v) => v === "READY" },
  { label: "Needs work", match: (v) => v !== "READY" },
];

export default function Projects() {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState(0);

  const shown = useMemo(() => {
    const q = query.trim().toLowerCase();
    return MOCK_PROJECTS.filter(
      (p) => FILTERS[filter].match(p.verdict) && (!q || p.name.toLowerCase().includes(q))
    );
  }, [query, filter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-3">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Projects</h2>
          <p className="text-sm text-muted-foreground">{MOCK_PROJECTS.length} projects in your library.</p>
        </div>
        <Button className="ml-auto" onClick={() => comingSoon("New project")}>
          <Plus className="h-4 w-4" /> New project
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

      {shown.length > 0 ? (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
          {shown.map((p) => (
            <ProjectCard key={p.id} project={p} />
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="flex flex-col items-center justify-center gap-2 py-16 text-center">
            <FolderKanban className="h-7 w-7 text-muted-foreground" />
            <p className="font-medium">No matching projects</p>
            <p className="text-sm text-muted-foreground">Try a different search or filter.</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
