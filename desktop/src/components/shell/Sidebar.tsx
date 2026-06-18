import { NavLink } from "react-router-dom";
import { LayoutDashboard, FolderKanban, Settings, Plus, Layers, Wand2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { MOCK_PROJECTS } from "@/data/mock";
import { comingSoon } from "@/store/toast";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/projects", label: "Projects", icon: FolderKanban, end: false },
  { to: "/batch", label: "Batch convert", icon: Wand2, end: false },
];

function navClass({ isActive }: { isActive: boolean }) {
  return cn(
    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
    isActive ? "bg-muted text-foreground" : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
  );
}

export function Sidebar() {
  const pinned = MOCK_PROJECTS.slice(0, 3);
  return (
    <aside className="flex h-full w-[230px] flex-col border-r border-border bg-card">
      <div className="flex items-center gap-2 px-4 h-14 border-b border-border">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
          <Layers className="h-4 w-4" />
        </div>
        <span className="font-semibold tracking-tight">Snapmaker Studio</span>
      </div>

      <nav className="flex flex-col gap-1 p-3">
        {NAV.map((n) => (
          <NavLink key={n.to} to={n.to} end={n.end} className={navClass}>
            <n.icon className="h-4 w-4" /> {n.label}
          </NavLink>
        ))}
      </nav>

      <button onClick={() => comingSoon("New project")} className="mx-3 mb-2 flex items-center gap-2 rounded-md border border-dashed border-border px-3 py-2 text-sm text-muted-foreground hover:bg-muted/60 hover:text-foreground">
        <Plus className="h-4 w-4" /> New project
      </button>

      <div className="px-4 pt-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Pinned</div>
      <div className="flex flex-col gap-0.5 px-2 py-1 overflow-y-auto">
        {pinned.map((p) => (
          <NavLink key={p.id} to={`/projects/${p.id}`} className={navClass}>
            <span className="h-1.5 w-1.5 rounded-full bg-current opacity-60" />
            <span className="truncate">{p.name}</span>
          </NavLink>
        ))}
      </div>

      <div className="mt-auto p-3 border-t border-border">
        <NavLink to="/settings" className={navClass}>
          <Settings className="h-4 w-4" /> Settings
        </NavLink>
      </div>
    </aside>
  );
}
