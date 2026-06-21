import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowRight, Plus, Stethoscope, GitCompareArrows } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import { doctorById } from "@/lib/doctors";
import { useOpenFile } from "@/hooks/useOpenFile";
import { useSession } from "@/store/session";
import NotFound from "@/routes/NotFound";

// Safe landing for the model-based Doctors. The Doctors run on an open model in
// the workspace; this page explains what the Doctor does and routes the user to
// the real functionality (open a model / continue with the current one). It does
// NOT fake a working Doctor — it is an honest entry point.
export default function DoctorLanding() {
  const { id } = useParams();
  const nav = useNavigate();
  const openFile = useOpenFile();
  const file = useSession((s) => s.file);
  const doc = doctorById(id);

  if (!doc) return <NotFound />;
  const Icon = doc.icon;

  return (
    <div className="space-y-6">
      <PageHeader icon={Icon} title={doc.name} subtitle={doc.answers} />

      <Card><CardContent className="space-y-4 p-5">
        <p className="flex items-center gap-2 text-sm font-semibold">
          <Stethoscope className="h-4 w-4 text-primary" /> How to run the {doc.name}
        </p>
        <p className="text-sm text-muted-foreground">
          The {doc.name} runs on a model. Open an STL or 3MF and Studio checks it
          automatically in the workspace — nothing leaves your computer.
        </p>

        <div className="flex flex-wrap gap-2">
          <Button size="sm" onClick={openFile}>
            <Plus className="h-4 w-4" /> Open a model
          </Button>
          {file && (
            <Button size="sm" variant="secondary" onClick={() => nav("/workspace")}>
              Continue with {file.name} <ArrowRight className="h-4 w-4" />
            </Button>
          )}
        </div>

        {doc.id === "multi-material" && (
          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <GitCompareArrows className="h-3.5 w-3.5" />
            Need to fix one plate's colour?{" "}
            <Link to="/plate-remap" className="text-primary hover:underline">Open Plate Color Remap</Link>
          </p>
        )}
      </CardContent></Card>
    </div>
  );
}
