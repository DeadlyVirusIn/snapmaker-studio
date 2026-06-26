import { GitCompareArrows, Palette, Plus, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import { ToolTabs } from "@/components/ui/ToolTabs";
import PlateRemap from "@/routes/PlateRemap";
import { useOpenFile } from "@/hooks/useOpenFile";
import { useSession } from "@/store/session";

// The Multi-Material Doctor runs on an open model in the workspace; here it's a
// short entry point (open a model / continue) rather than a duplicate landing page.
function MultiMaterialTab() {
  const openFile = useOpenFile();
  const nav = useNavigate();
  const file = useSession((s) => s.file);
  return (
    <div className="space-y-4">
      <PageHeader icon={Palette} title="Multi-Material Doctor"
        subtitle="Will your colours print right? Toolheads, mapping & purge checks." />
      <Card><CardContent className="space-y-4 p-5">
        <p className="text-sm text-muted-foreground">
          The Multi-Material Doctor runs on an open model and checks toolhead / colour
          mapping in the workspace. Open a model, then continue there.
        </p>
        <div className="flex flex-wrap gap-2">
          <Button size="sm" onClick={openFile}><Plus className="h-4 w-4" /> Open a model</Button>
          {file && (
            <Button size="sm" variant="secondary" onClick={() => nav("/workspace")}>
              Continue with {file.name} <ArrowRight className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardContent></Card>
    </div>
  );
}

// Merged "Colors & Materials" page: changing a plate's colour (Plate Color Remap)
// and checking multi-colour print readiness (Multi-Material Doctor) are the same
// colour job, so they share one sidebar item as two tabs. /plate-remap and
// /doctor/multi-material still resolve on their own for any deep links.
export default function ColorsMaterials() {
  return (
    <ToolTabs tabs={[
      { id: "remap", label: "Plate Color Remap", icon: GitCompareArrows, el: <PlateRemap /> },
      { id: "multi-material", label: "Multi-Material", icon: Palette, el: <MultiMaterialTab /> },
    ]} />
  );
}
