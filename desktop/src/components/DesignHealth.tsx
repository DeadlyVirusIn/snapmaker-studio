import { CheckCircle2, AlertTriangle, ShieldAlert, Droplets, Boxes, MoveVertical, LifeBuoy, Ruler } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import type { MeshReport } from "@/api";

// U1 build volume (mm) — matches the engine's bed-fit check.
const U1_BED = { x: 270, y: 270, z: 270 };

type Level = "ok" | "warn" | "risk";
interface Row { key: string; label: string; icon: LucideIcon; level: Level; status: string; detail: string; }

const PILL: Record<Level, string> = {
  ok: "bg-ready/10 text-ready",
  warn: "bg-repairable/10 text-repairable",
  risk: "bg-risk/10 text-risk",
};
const STATUS_ICON: Record<Level, LucideIcon> = { ok: CheckCircle2, warn: AlertTriangle, risk: ShieldAlert };

function buildRows(mesh: MeshReport, dims?: { x: number; y: number; z: number } | null,
                   bed?: { x: number; y: number; z: number } | null): Row[] {
  const rows: Row[] = [];
  const integ = mesh.integrity;
  const fitBed = bed ?? U1_BED;
  const bedSource = bed ? "your connected U1" : "the U1’s";

  // 1. Watertight
  if (integ) {
    rows.push(integ.watertight
      ? { key: "watertight", label: "Watertight", icon: Droplets, level: "ok", status: "Sealed",
          detail: "The mesh is fully closed. It will slice cleanly without gaps." }
      : { key: "watertight", label: "Watertight", icon: Droplets, level: "risk", status: `${integ.holes} hole${integ.holes === 1 ? "" : "s"}`,
          detail: `Found ${integ.holes} hole(s) / ${integ.open_edges} open edge(s). Open meshes can print with gaps or fail — repair the model before printing.` });

    // 2. Geometry integrity (manifold + normals + degenerate)
    const intIssues: string[] = [];
    if (integ.non_manifold_edges) intIssues.push(`${integ.non_manifold_edges} non-manifold edge(s)`);
    if (!integ.winding_consistent) intIssues.push("inconsistent face normals");
    if (integ.degenerate_faces) intIssues.push(`${integ.degenerate_faces} zero-area face(s)`);
    rows.push(intIssues.length === 0
      ? { key: "integrity", label: "Geometry integrity", icon: Boxes, level: "ok", status: "Clean",
          detail: "Manifold surface with consistent normals — slicers will read it correctly." }
      : { key: "integrity", label: "Geometry integrity", icon: Boxes, level: integ.non_manifold_edges ? "risk" : "warn", status: "Issues",
          detail: `${intIssues.join(", ")}. These can confuse a slicer; a repair pass cleans them up.` });
  }

  // 3. Stability / tip-risk
  if (mesh.stability) {
    const tip = mesh.stability.tip_risk;
    rows.push({ key: "stability", label: "Stability", icon: MoveVertical, level: tip ? "warn" : "ok",
      status: tip ? "Tip risk" : "Stable",
      detail: tip
        ? `Tall and narrow (aspect ${mesh.stability.aspect}). It may tip over or knock off the bed — add a brim or reorient, and consider the Maximum Reliability strategy.`
        : "Footprint is broad enough relative to height — low tip-over risk." });
  }

  // 4. Supports recommended
  if (mesh.overhang) {
    const s = mesh.overhang.supports_likely;
    rows.push({ key: "supports", label: "Supports", icon: LifeBuoy, level: s ? "warn" : "ok",
      status: s ? "Recommended" : "Not needed",
      detail: s
        ? `${mesh.overhang.overhang_pct}% of surfaces are steep overhangs. Enable supports in Snapmaker Orca so they print cleanly.`
        : "Few steep overhangs — this should print without supports." });
  }

  // 5. Bed fit (from dimensions vs the real connected printer bed, else the U1 default)
  if (dims) {
    const fits = dims.x <= fitBed.x && dims.y <= fitBed.y && dims.z <= fitBed.z;
    const bedStr = `${fitBed.x} × ${fitBed.y} × ${fitBed.z} mm`;
    rows.push({ key: "bedfit", label: "Bed fit", icon: Ruler, level: fits ? "ok" : "risk",
      status: fits ? "Fits" : "Too big",
      detail: fits
        ? `${dims.x} × ${dims.y} × ${dims.z} mm fits ${bedSource} ${bedStr} bed.`
        : `${dims.x} × ${dims.y} × ${dims.z} mm is larger than ${bedSource} ${bedStr} bed — scale it down or split it.` });
  }
  return rows;
}

/** Design Health — at-a-glance geometry verdicts with plain-language what/why/do.
 *  `mode` "advanced" appends the raw metric footer. */
export function DesignHealth({ mesh, dims, bed, mode = "simple" }: {
  mesh?: MeshReport; dims?: { x: number; y: number; z: number } | null;
  bed?: { x: number; y: number; z: number } | null; mode?: "simple" | "advanced";
}) {
  if (!mesh) return null;
  if (!mesh.available) {
    return <p className="text-xs text-muted-foreground">Geometry analysis isn’t available for this file (it may be too large).</p>;
  }
  const rows = buildRows(mesh, dims, bed);
  if (!rows.length) return null;

  return (
    <div className="space-y-2.5">
      {rows.map((r) => {
        const SIcon = STATUS_ICON[r.level];
        return (
          <div key={r.key} className="flex items-start gap-2.5">
            <r.icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">{r.label}</span>
                <span className={cn("inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold", PILL[r.level])}>
                  <SIcon className="h-3 w-3" /> {r.status}
                </span>
              </div>
              <p className="text-xs leading-snug text-muted-foreground">{r.detail}</p>
            </div>
          </div>
        );
      })}
      {mode === "advanced" && (
        <p className="border-t border-border pt-2 text-[11px] text-muted-foreground">
          {mesh.triangle_count?.toLocaleString()} triangles · {mesh.volume_cm3} cm³ · {mesh.surface_area_mm2} mm² ·
          overhang {mesh.overhang?.overhang_pct}% (severe {mesh.overhang?.severe_pct}%) ·
          aspect {mesh.stability?.aspect} · open edges {mesh.integrity?.open_edges}
        </p>
      )}
    </div>
  );
}
