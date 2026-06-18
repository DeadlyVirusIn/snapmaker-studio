import { useEffect } from "react";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import { getCurrentWebview } from "@tauri-apps/api/webview";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { StatusBar } from "./StatusBar";
import { Toaster } from "@/components/ui/Toaster";
import { useSession } from "@/store/session";

function titleFor(path: string): string {
  if (path === "/") return "Dashboard";
  if (path.startsWith("/workspace")) return "Workspace";
  if (path.startsWith("/projects")) return "Projects";
  if (path.startsWith("/settings")) return "Settings";
  return "Snapmaker Studio";
}

export function AppShell() {
  const { pathname } = useLocation();
  const nav = useNavigate();
  const setFile = useSession((s) => s.setFile);

  // Native drag-and-drop: a dropped .stl/.3mf loads into the live workspace.
  // Guarded so the app still renders outside Tauri (e.g. a plain browser for
  // screenshots) where the webview API is unavailable.
  useEffect(() => {
    let cleanup: (() => void) | undefined;
    try {
      const un = getCurrentWebview().onDragDropEvent((e) => {
        if (e.payload.type !== "drop" || !e.payload.paths.length) return;
        const model = e.payload.paths.find((p) => /\.(stl|3mf)$/i.test(p));
        if (!model) return;
        setFile(model);
        nav("/workspace");
      });
      cleanup = () => { un.then((f) => f()); };
    } catch {
      /* not running inside Tauri — drag-drop disabled */
    }
    return () => cleanup?.();
  }, [nav, setFile]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-foreground">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar title={titleFor(pathname)} />
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto w-full max-w-[1400px] px-8 py-8 2xl:px-12">
            <Outlet />
          </div>
        </main>
        <StatusBar />
      </div>
      <Toaster />
    </div>
  );
}
