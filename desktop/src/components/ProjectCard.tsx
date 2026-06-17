import { memo } from "react";
import { useNavigate } from "react-router-dom";
import { FileBox, Boxes } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import type { MockProject } from "@/data/mock";

function ProjectCardImpl({ project }: { project: MockProject }) {
  const nav = useNavigate();
  const Icon = project.type === "3mf" ? Boxes : FileBox;
  return (
    <Card
      role="button"
      tabIndex={0}
      onClick={() => nav(`/projects/${project.id}`)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          nav(`/projects/${project.id}`);
        }
      }}
      className="group cursor-pointer transition-all hover:border-primary/40 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
    >
      <CardContent className="space-y-3 p-4">
        <div className="flex items-start justify-between gap-2">
          <div className="flex min-w-0 items-center gap-2.5">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-muted text-muted-foreground group-hover:text-foreground">
              <Icon className="h-[18px] w-[18px]" />
            </div>
            <span className="truncate font-medium">{project.name}</span>
          </div>
          <StatusBadge verdict={project.verdict} />
        </div>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{project.type.toUpperCase()} · {project.colours} colour{project.colours === 1 ? "" : "s"}</span>
          <span>{project.updated}</span>
        </div>
      </CardContent>
    </Card>
  );
}

export const ProjectCard = memo(ProjectCardImpl);
