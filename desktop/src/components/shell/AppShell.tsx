import { Outlet, useLocation } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { StatusBar } from "./StatusBar";
import { Toaster } from "@/components/ui/Toaster";

function titleFor(path: string): string {
  if (path === "/") return "Dashboard";
  if (path.startsWith("/projects")) return "Projects";
  if (path.startsWith("/settings")) return "Settings";
  return "Snapmaker Studio";
}

export function AppShell() {
  const { pathname } = useLocation();
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
