import { Search, Stethoscope, Wand2, ShieldCheck, Printer, ChevronRight } from "lucide-react";

// The platform story in one strip: the brand workflow every design flows through —
// Discover → Diagnose → Fix → Validate → Print (Unified Intelligence Hub Asset
// Pack). Each stage maps to a real Doctor/feature and carries its spectrum colour
// so the workflow is legible at a glance — Studio as the Intelligence Layer for
// open 3D printing, not a one-shot converter.
const STAGES = [
  { icon: Search, label: "Discover", token: "--stage-input", hint: "Any file, any ecosystem — STL or 3MF, kept local" },
  { icon: Stethoscope, label: "Diagnose", token: "--stage-diagnose", hint: "The Doctors check fit, colours & first layer — before Orca" },
  { icon: Wand2, label: "Fix", token: "--stage-transform", hint: "Repair & standardize into a clean U1 project" },
  { icon: ShieldCheck, label: "Validate", token: "--stage-validate", hint: "Watertight, supported, stable & in-bounds" },
  { icon: Printer, label: "Print", token: "--stage-output", hint: "Send and monitor live on your U1" },
];

export function Workflow() {
  return (
    <div>
      <div className="grid grid-cols-2 gap-2 md:grid-cols-3 lg:grid-cols-5 lg:gap-0">
        {STAGES.map((s, i) => (
          <div key={s.label} className="relative flex items-start gap-3 rounded-lg p-3 lg:rounded-none lg:px-3">
            <div
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg"
              style={{
                color: `hsl(var(${s.token}))`,
                backgroundColor: `hsl(var(${s.token}) / 0.12)`,
                boxShadow: `inset 0 0 0 1px hsl(var(${s.token}) / 0.25)`,
              }}
            >
              <s.icon className="h-[18px] w-[18px]" />
            </div>
            <div className="min-w-0">
              <p className="flex items-center gap-1.5 text-sm font-semibold">
                <span className="text-[11px] font-medium text-muted-foreground">{i + 1}</span> {s.label}
              </p>
              <p className="text-xs leading-snug text-muted-foreground">{s.hint}</p>
            </div>
            {i < STAGES.length - 1 && (
              <ChevronRight className="absolute -right-2 top-4 hidden h-4 w-4 text-muted-foreground/40 lg:block" />
            )}
          </div>
        ))}
      </div>
      {/* the multi-material spectrum flowing left→right under the stages */}
      <div className="spectrum-rule mt-2 h-0.5 w-full rounded-full opacity-60" />
    </div>
  );
}
