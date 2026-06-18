import { useMode } from "@/store/mode";
import LiveWorkspace from "@/routes/LiveWorkspace";
import DesignInsights from "@/routes/DesignInsights";

// Single /workspace route: novice-first Design Insights in Simple Mode,
// the unchanged power-user workspace in Advanced Mode. No duplicated routes.
export default function WorkspaceSwitch() {
  const mode = useMode((s) => s.mode);
  return mode === "simple" ? <DesignInsights /> : <LiveWorkspace />;
}
