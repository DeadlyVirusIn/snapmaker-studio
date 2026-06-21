import { Link } from "react-router-dom";
import { BookOpen, ArrowRight } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/layout";
import { DOCTORS } from "@/lib/doctors";

// Lightweight help/about hub. Honest pointers only — links to in-app surfaces
// that actually exist; no fabricated documentation.
export default function Help() {
  return (
    <div className="space-y-6">
      <PageHeader icon={BookOpen} title="Docs / Help"
        subtitle="What Snapmaker Studio does and where to find each tool." />

      <Card><CardContent className="space-y-3 p-5 text-sm">
        <p className="font-semibold">The Intelligence Layer for Open 3D Printing</p>
        <p className="text-muted-foreground">
          Orca slices. Fluidd monitors. Studio decides. Studio checks a model and
          your U1 before a layer is sliced — local-first, nothing leaves your
          computer.
        </p>
        <Link to="/why" className="inline-flex items-center gap-1 text-primary hover:underline">
          Why Studio? <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </CardContent></Card>

      <Card><CardContent className="space-y-2 p-5">
        <p className="text-sm font-semibold">The Doctors</p>
        <ul className="space-y-1 text-sm">
          {DOCTORS.map((d) => (
            <li key={d.id}>
              <Link to={d.route} className="text-primary hover:underline">{d.name}</Link>
              <span className="text-muted-foreground"> — {d.answers}</span>
            </li>
          ))}
          <li>
            <Link to="/plate-remap" className="text-primary hover:underline">Plate Color Remap</Link>
            <span className="text-muted-foreground"> — change one plate's colour, safely, with a verified copy.</span>
          </li>
        </ul>
      </CardContent></Card>
    </div>
  );
}
