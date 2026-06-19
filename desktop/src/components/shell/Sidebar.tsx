import { NavLink, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { LayoutDashboard, FolderKanban, Settings, Plus, Layers, Wand2, Printer } from "lucide-react";
import { cn } from "@/lib/utils";
import { library } from "@/api";
import { useSession } from "@/store/session";
import { useOpenFile } from "@/hooks/useOpenFile";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/projects", label: "Projects", icon: FolderKanban, end: false },
  { to: "/batch", label: "Batch prepare", icon: Wand2, end: false },
  { to: "/printers", label: "Printers", icon: Printer, end: false },
];

function navClass({ isActive }: { isActive: boolean }) {
  return cn(
    "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
    isActive ? "bg-muted text-foreground" : "text-muted-foreground hover:bg-muted/60 hover:text-foreground"
  );
}

export function Sidebar() {
  const nav = useNavigate();
  const setFile = useSession((s) => s.setFile);
  const openFile = useOpenFile();
  const { data } = useQuery({ queryKey: ["library"], queryFn: () => library() });
  const recent = (data ?? []).slice(0, 3);

  return (
    <aside className="flex h-full w-[230px] flex-col border-r border-border bg-card">
      <div className="flex items-center gap-2.5 px-4 h-14 border-b border-border">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-convertible text-primary-foreground shadow-sm">
          <Layers className="h-[18px] w-[18px]" />
        </div>
        <div className="leading-none">
          <span className="block font-semibold tracking-tight">Snapmaker Studio</span>
          <span className="block text-[10px] font-medium uppercase tracking-wide text-muted-foreground">Workflow Platform</span>
        </div>
      </div>

      <nav className="flex flex-col gap-1 p-3">
        {NAV.map((n) => (
          <NavLink key={n.to} to={n.to} end={n.end} className={navClass}>
            <n.icon className="h-4 w-4" /> {n.label}
          </NavLink>
        ))}
      </nav>

      <button onClick={openFile} className="mx-3 mb-2 flex items-center gap-2 rounded-md border border-dashed border-border px-3 py-2 text-sm text-muted-foreground hover:bg-muted/60 hover:text-foreground">
        <Plus className="h-4 w-4" /> Open a model
      </button>

      {recent.length > 0 && (
        <>
          <div className="px-4 pt-2 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">Recent</div>
          <div className="flex flex-col gap-0.5 px-2 py-1 overflow-y-auto">
            {recent.map((p) => (
              <button
                key={p.id}
                onClick={() => { setFile(p.source_path); nav("/workspace"); }}
                title={p.source_path}
                className={navClass({ isActive: false }) + " w-full text-left"}
              >
                <span className="h-1.5 w-1.5 rounded-full bg-current opacity-60" />
                <span className="truncate">{p.name}</span>
              </button>
            ))}
          </div>
        </>
      )}

      <div className="mt-auto p-3 border-t border-border">
        <NavLink to="/settings" className={navClass}>
          <Settings className="h-4 w-4" /> Settings
        </NavLink>
      </div>
    </aside>
  );
}
