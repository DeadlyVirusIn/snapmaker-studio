import { Sparkles, ShieldCheck, Wand2, Printer, ChevronRight } from "lucide-react";

// The platform story in one strip: every design flows through these four
// stages. Used on the Dashboard to frame Studio as an end-to-end workflow,
// not a one-shot converter. Each stage maps to a real feature in the app.
const PHASES = [
  { icon: Sparkles, label: "Understand", hint: "See colors, size & complexity" },
  { icon: ShieldCheck, label: "Validate", hint: "Confirm it prints on your U1" },
  { icon: Wand2, label: "Prepare", hint: "Make a clean U1 project" },
  { icon: Printer, label: "Print", hint: "Monitor your U1 live" },
];

export function Workflow() {
  return (
    <div className="grid grid-cols-2 gap-2 lg:grid-cols-4 lg:gap-0">
      {PHASES.map((p, i) => (
        <div key={p.label} className="relative flex items-start gap-3 rounded-lg p-3 lg:rounded-none lg:px-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary ring-1 ring-primary/15">
            <p.icon className="h-[18px] w-[18px]" />
          </div>
          <div className="min-w-0">
            <p className="flex items-center gap-1.5 text-sm font-semibold">
              <span className="text-[11px] font-medium text-muted-foreground">{i + 1}</span> {p.label}
            </p>
            <p className="text-xs leading-snug text-muted-foreground">{p.hint}</p>
          </div>
          {i < PHASES.length - 1 && (
            <ChevronRight className="absolute -right-2 top-4 hidden h-4 w-4 text-muted-foreground/40 lg:block" />
          )}
        </div>
      ))}
    </div>
  );
}
