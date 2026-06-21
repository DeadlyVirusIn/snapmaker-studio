import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AppShell } from "@/components/shell/AppShell";
import Dashboard from "@/routes/Dashboard";
import Projects from "@/routes/Projects";
import Batch from "@/routes/Batch";
import WorkspaceSwitch from "@/routes/WorkspaceSwitch";
import Printers from "@/routes/Printers";
import Settings from "@/routes/Settings";
import WhyStudio from "@/routes/WhyStudio";
import PlateRemap from "@/routes/PlateRemap";
import DoctorLanding from "@/routes/DoctorLanding";
import Compatibility from "@/routes/Compatibility";
import Help from "@/routes/Help";
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
            <Route path="/workspace" element={<WorkspaceSwitch />} />
            <Route path="/printers" element={<Printers />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/why" element={<WhyStudio />} />
            <Route path="/help" element={<Help />} />
            <Route path="/plate-remap" element={<PlateRemap />} />
            <Route path="/compatibility" element={<Compatibility />} />
            <Route path="/doctor/:id" element={<DoctorLanding />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
