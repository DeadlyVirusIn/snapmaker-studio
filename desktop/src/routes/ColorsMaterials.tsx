import { Palette, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import PlateRemap from "@/routes/PlateRemap";
import { ColorPlanCard } from "@/components/ColorPlanCard";
import { useSession } from "@/store/session";

// "Colors & Materials": Plate Color Remap plus the colours-vs-toolheads answer.
// That answer used to be a pointer to another page, which is a dead end for the
// exact question this page's name asks. With a project open it is now shown here,
// classified into colours that share layers, colours introduced higher up, and
// colours Studio cannot classify.
export default function ColorsMaterials() {
  const file = useSession((s) => s.file);
  return (
    <div className="space-y-3">
      <PlateRemap />
      {file?.path ? (
        <ColorPlanCard path={file.path} />
      ) : (
        <p className="flex items-center gap-2 px-1 text-xs text-muted-foreground">
          <Palette className="h-3.5 w-3.5" />
          Open a model to see how its colours map onto your four toolheads
          <Link to="/workspace" className="inline-flex items-center gap-1 text-primary hover:underline">
            — open one <ArrowRight className="h-3 w-3" />
          </Link>
        </p>
      )}
    </div>
  );
}
