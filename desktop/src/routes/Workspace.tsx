import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ArrowLeft, FileBox, Boxes, CheckCircle2, AlertTriangle, XCircle,
  Wand2, Clock, Layers, ArrowRight, Sparkles,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/badge";
import type { Verdict } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { MOCK_PROJECTS } from "@/data/mock";
import { comingSoon } from "@/store/toast";

const TABS = ["Overview", "Doctor", "Convert", "Compare", "History"] as const;
type Tab = (typeof TABS)[number];

type CheckState = "pass" | "warn" | "fail";

function checkIcon(state: CheckState) {
  if (state === "pass") return <CheckCircle2 className="h-4 w-4 text-ready" />;
  if (state === "warn") return <AlertTriangle className="h-4 w-4 text-repairable" />;
  return <XCircle className="h-4 w-4 text-risk" />;
}

// Mock diagnostic checks derived from the project verdict — no backend.
function checksFor(verdict: Verdict): { label: string; state: CheckState; detail: string }[] {
  const base: CheckState = verdict === "READY" ? "pass" : verdict === "HIGH_RISK" ? "fail" : "warn";
  return [
    { label: "Filament block", state: verdict === "HIGH_RISK" ? "fail" : "pass", detail: "Padded to 4 toolhead slots" },
    { label: "Snapmaker U1 preset", state: base, detail: "PLA SnapSpeed @U1" },
    { label: "Object → extruder mapping", state: base, detail: "All objects mapped" },
    { label: "Geometry integrity", state: "pass", detail: "Mesh preserved exactly" },
  ];
}

const ACTION_COPY: Record<Verdict, { tone: string; text: string }> = {
  READY: { tone: "ready", text: "This project is ready to slice on the Snapmaker U1." },
  REPAIRABLE: { tone: "repairable", text: "Minor preset fixes needed — one click makes it U1-ready." },
  CONVERTIBLE: { tone: "convertible", text: "An STL — convert it to a U1 project to slice." },
  HIGH_RISK: { tone: "risk", text: "Significant issues found. Review before converting." },
};

function EmptyState({ icon: Icon, title, hint }: { icon: any; title: string; hint: string }) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center gap-2 py-16 text-center">
        <Icon className="h-7 w-7 text-muted-foreground" />
        <p className="font-medium">{title}</p>
        <p className="text-sm text-muted-foreground">{hint}</p>
      </CardContent>
    </Card>
  );
}

export default function Workspace() {
  const { id } = useParams();
  const project = MOCK_PROJECTS.find((p) => p.id === id) ?? MOCK_PROJECTS[0];
  const [tab, setTab] = useState<Tab>("Overview");

  const TypeIcon = project.type === "3mf" ? Boxes : FileBox;
  const checks = checksFor(project.verdict);
  const action = ACTION_COPY[project.verdict];

  return (
    <div className="space-y-5">
      <Link to="/projects" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Projects
      </Link>

      <div className="flex flex-wrap items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-muted-foreground">
          <TypeIcon className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-xl font-semibold tracking-tight">{project.name}</h2>
          <p className="text-sm text-muted-foreground">
            Snapmaker U1 · {project.type.toUpperCase()} · {project.colours} colour{project.colours === 1 ? "" : "s"}
          </p>
        </div>
        <StatusBadge verdict={project.verdict} />
        <div className="ml-auto">
          <Button onClick={() => comingSoon("Make U1-ready")}>
            <Wand2 className="h-4 w-4" /> Make U1-ready
          </Button>
        </div>
      </div>

      <div className="flex gap-1 border-b border-border">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "px-3 py-2 text-sm font-medium border-b-2 -mb-px transition-colors",
              tab === t ? "border-primary text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-[1fr_260px]">
        <div className="space-y-4">
          {tab === "Overview" && (
            <>
              <Card>
                <CardContent className="flex items-center gap-5 p-6">
                  <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full border-4 border-primary/30 text-2xl font-bold text-primary">
                    {project.score ?? "—"}
                  </div>
                  <div className="space-y-1.5">
                    <StatusBadge verdict={project.verdict} />
                    <p className="text-sm text-muted-foreground">{action.text}</p>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-5">
                  <h3 className="mb-3 text-sm font-semibold">Compatibility summary</h3>
                  <ul className="space-y-2.5">
                    {checks.map((c) => (
                      <li key={c.label} className="flex items-center gap-3 text-sm">
                        {checkIcon(c.state)}
                        <span className="font-medium">{c.label}</span>
                        <span className="ml-auto text-muted-foreground">{c.detail}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </>
          )}

          {tab === "Doctor" && (
            <>
              <Card>
                <CardContent className="flex items-center gap-3 p-5">
                  <Sparkles className="h-5 w-5 text-primary" />
                  <p className="text-sm">{action.text}</p>
                  {project.verdict !== "READY" && (
                    <Button size="sm" className="ml-auto" onClick={() => comingSoon("Auto-fix")}><Wand2 className="h-4 w-4" /> Auto-fix</Button>
                  )}
                </CardContent>
              </Card>
              <Card>
                <CardContent className="divide-y divide-border p-0">
                  {checks.map((c) => (
                    <div key={c.label} className="flex items-center gap-3 px-5 py-3.5 text-sm">
                      {checkIcon(c.state)}
                      <div>
                        <p className="font-medium">{c.label}</p>
                        <p className="text-xs text-muted-foreground">{c.detail}</p>
                      </div>
                      <span className="ml-auto text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        {c.state}
                      </span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </>
          )}

          {tab === "Convert" && (
            <Card>
              <CardContent className="space-y-4 p-5">
                <div className="flex items-center gap-2 text-sm font-semibold"><Layers className="h-4 w-4" /> Convert to Snapmaker U1</div>
                <div className="grid grid-cols-3 gap-3 text-sm">
                  <div className="rounded-md border border-border p-3">
                    <p className="text-xs text-muted-foreground">Source</p>
                    <p className="font-medium">{project.type.toUpperCase()}</p>
                  </div>
                  <div className="flex items-center justify-center"><ArrowRight className="h-5 w-5 text-muted-foreground" /></div>
                  <div className="rounded-md border border-primary/40 bg-primary/5 p-3">
                    <p className="text-xs text-muted-foreground">Target</p>
                    <p className="font-medium text-primary">U1 3MF</p>
                  </div>
                </div>
                <div>
                  <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">Filament slots (min 4)</p>
                  <div className="flex gap-2">
                    {[0, 1, 2, 3].map((i) => (
                      <div key={i} className="flex h-8 flex-1 items-center justify-center rounded-md border border-border bg-muted/40 text-xs">
                        {i < Math.max(project.colours, 1) ? `Colour ${i + 1}` : "—"}
                      </div>
                    ))}
                  </div>
                </div>
                <Button className="w-full" onClick={() => comingSoon("Convert to U1")}>Convert &amp; save U1 project</Button>
                <p className="text-center text-xs text-muted-foreground">Originals are never overwritten.</p>
              </CardContent>
            </Card>
          )}

          {tab === "Compare" && (
            project.verdict === "CONVERTIBLE" ? (
              <EmptyState icon={Layers} title="Nothing to compare yet" hint="Convert this model to a U1 project, then compare versions." />
            ) : (
              <Card>
                <CardContent className="p-5">
                  <h3 className="mb-3 text-sm font-semibold">Original vs U1-ready</h3>
                  <div className="overflow-hidden rounded-md border border-border text-sm">
                    <div className="grid grid-cols-[1fr_1fr_1fr] gap-2 border-b border-border bg-muted/40 px-3 py-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      <span>Field</span>
                      <span>Original</span>
                      <span>U1-ready</span>
                    </div>
                    {[
                      { field: "Filament count", a: `${project.colours}`, b: `${Math.max(project.colours, 4)}` },
                      { field: "Preset", a: "Generic PLA", b: "PLA SnapSpeed @U1" },
                      { field: "Object mapping", a: "None", b: "All objects mapped" },
                      { field: "Geometry", a: "Original", b: "Identical" },
                    ].map((row, i) => (
                      <div key={row.field} className={cn("grid grid-cols-[1fr_1fr_1fr] gap-2 px-3 py-2.5", i % 2 && "bg-muted/30")}>
                        <span className="font-medium">{row.field}</span>
                        <span className="text-muted-foreground line-through">{row.a}</span>
                        <span className="text-ready">{row.b}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )
          )}

          {tab === "History" && (
            <Card>
              <CardContent className="p-5">
                <ol className="relative space-y-5 border-l border-border pl-5">
                  {[
                    { text: "Doctor check completed", when: project.updated },
                    { text: project.type === "stl" ? "Imported STL" : "Imported 3MF project", when: project.updated },
                    { text: "Project created", when: project.updated },
                  ].map((e, i) => (
                    <li key={i} className="relative">
                      <span className="absolute -left-[23px] top-1 flex h-3 w-3 items-center justify-center rounded-full border-2 border-primary bg-background" />
                      <p className="text-sm font-medium">{e.text}</p>
                      <p className="flex items-center gap-1 text-xs text-muted-foreground"><Clock className="h-3 w-3" /> {e.when}</p>
                    </li>
                  ))}
                </ol>
              </CardContent>
            </Card>
          )}
        </div>

        <aside className="space-y-3">
          <Card>
            <CardContent className="space-y-2 p-4 text-sm">
              <div className="flex items-center gap-2 font-medium"><FileBox className="h-4 w-4" /> Source</div>
              <dl className="space-y-1 text-muted-foreground">
                <div className="flex justify-between"><dt>Type</dt><dd className="text-foreground">{project.type.toUpperCase()}</dd></div>
                <div className="flex justify-between"><dt>Colours</dt><dd className="text-foreground">{project.colours}</dd></div>
                <div className="flex justify-between"><dt>Score</dt><dd className="text-foreground">{project.score ?? "—"}</dd></div>
                <div className="flex justify-between"><dt>Updated</dt><dd className="text-foreground">{project.updated}</dd></div>
              </dl>
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  );
}
