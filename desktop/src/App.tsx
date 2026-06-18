import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "@/components/shell/AppShell";
import Dashboard from "@/routes/Dashboard";
import Projects from "@/routes/Projects";
import Batch from "@/routes/Batch";
import LiveWorkspace from "@/routes/LiveWorkspace";
import Settings from "@/routes/Settings";
import NotFound from "@/routes/NotFound";
import { useTheme } from "@/store/theme";

const queryClient = new QueryClient();

export default function App() {
  const { theme } = useTheme();

  // Keep the <html> class in sync with the persisted theme on load.
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/batch" element={<Batch />} />
            <Route path="/workspace" element={<LiveWorkspace />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
