import { Palette, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import PlateRemap from "@/routes/PlateRemap";
import { useSession } from "@/store/session";

// "Colors & Materials" (beta.21): Plate Color Remap is the page. The old
// Multi-Material explainer tab was a dead end (it only told you to go somewhere
// else) — the multi-material check itself runs automatically on an open model in
// the workspace, so we link there instead of duplicating a landing page.
export default function ColorsMaterials() {
  const file = useSession((s) => s.file);
  return (
    <div className="space-y-3">
      <PlateRemap />
      <p className="flex items-center gap-2 px-1 text-xs text-muted-foreground">
        <Palette className="h-3.5 w-3.5" />
        Checking colours vs toolheads? That runs automatically when you open a model
        {file ? (
          <Link to="/workspace" className="inline-flex items-center gap-1 text-primary hover:underline">
            — continue with {file.name} <ArrowRight className="h-3 w-3" />
          </Link>
        ) : (
          <span>— open a model to see it.</span>
        )}
      </p>
    </div>
  );
}
