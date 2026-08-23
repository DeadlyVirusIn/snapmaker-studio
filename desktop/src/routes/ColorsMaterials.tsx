import { Palette, FilePlus } from "lucide-react";
import PlateRemap from "@/routes/PlateRemap";
import { ColorPlanCard } from "@/components/ColorPlanCard";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useModelPath } from "@/hooks/useModelPath";
import { isExt } from "@/lib/modelPath";
import { open3mfDialog } from "@/api";

// "Colors & Materials": Plate Color Remap plus the colours-vs-toolheads answer.
//
// That answer used to be a pointer to another page, which is a dead end for the
// exact question this page's name asks. It is now shown here, with each colour
// classified as sharing layers, arriving higher up, or unclassifiable.
//
// The path comes from the same hook every other tool page uses, so a project
// opened anywhere in Studio appears here — and when nothing is open, this page
// can open one itself instead of sending the user somewhere else.
export default function ColorsMaterials() {
  const { path, fromSession, override } = useModelPath(isExt("3mf"));

  async function pick() {
    const chosen = await open3mfDialog();
    if (chosen) override(chosen);
  }

  return (
    <div className="space-y-3">
      <PlateRemap />

      <Card>
        <CardContent className="flex flex-wrap items-center gap-3 p-5">
          <Button variant="secondary" size="sm" onClick={pick}>
            <FilePlus className="h-4 w-4" />
            {path
              ? fromSession
                ? "Using your open 3MF — choose another"
                : "Choose another 3MF"
              : "Open a 3MF project"}
          </Button>
          {path ? (
            <span className="truncate text-xs text-muted-foreground">
              {path.split(/[\\/]/).pop()}
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Palette className="h-3.5 w-3.5" />
              Open a project to see how its colours map onto your four toolheads.
            </span>
          )}
        </CardContent>
      </Card>

      {path && <ColorPlanCard path={path} />}
    </div>
  );
}
