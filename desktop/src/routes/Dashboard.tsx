import { Link } from "react-router-dom";
import { UploadCloud, Stethoscope, Wand2, GitCompare, Plus, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ProjectCard } from "@/components/ProjectCard";
import { MOCK_PROJECTS, MOCK_ACTIVITY, INSIGHTS } from "@/data/mock";
import { comingSoon } from "@/store/toast";
import { useOpenFile } from "@/hooks/useOpenFile";

const QUICK = [
  { label: "Check compatibility", icon: Stethoscope, hint: "Run Doctor", live: true },
  { label: "Convert STL", icon: UploadCloud, hint: "STL → U1", live: true },
  { label: "Repair 3MF", icon: Wand2, hint: "Fix presets", live: false },
  { label: "Compare files", icon: GitCompare, hint: "Diff versions", live: false },
];

export default function Dashboard() {
  const recent = MOCK_PROJECTS.slice(0, 3);
  const openFile = useOpenFile();

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

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold">Continue working</h3>
          <Link to="/projects" className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground">
            All projects <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {recent.map((p) => (
            <ProjectCard key={p.id} project={p} />
          ))}
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardContent className="p-5">
            <h3 className="mb-3 text-sm font-semibold">Activity</h3>
            <ul className="space-y-2 text-sm">
              {MOCK_ACTIVITY.map((a) => (
                <li key={a.id} className="flex items-center gap-2 text-muted-foreground">
                  <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                  <span className="text-foreground">{a.text}</span>
                  <span className="ml-auto text-xs">{a.when}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-5">
            <h3 className="mb-3 text-sm font-semibold">Library</h3>
            <div className="space-y-1 text-sm text-muted-foreground">
              <p><span className="text-2xl font-semibold text-foreground">{INSIGHTS.projects}</span> projects</p>
              <p>{INSIGHTS.ready} U1-ready · {INSIGHTS.needsWork} need work</p>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
