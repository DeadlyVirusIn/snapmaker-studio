import { useState, type ReactNode } from "react";
import { type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

// Lightweight tab switcher used to merge two closely-related tools onto one page
// (one sidebar item, two panels) instead of two duplicate nav entries. Each panel
// is an existing route component rendered as-is.
export interface ToolTab {
  id: string;
  label: string;
  icon?: LucideIcon;
  el: ReactNode;
}

export function ToolTabs({ tabs, initial }: { tabs: ToolTab[]; initial?: string }) {
  const [active, setActive] = useState(initial ?? tabs[0]?.id);
  const current = tabs.find((t) => t.id === active) ?? tabs[0];
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-1 border-b border-border" role="tablist">
        {tabs.map((t) => (
          <button key={t.id} role="tab" type="button" aria-selected={t.id === active}
            onClick={() => setActive(t.id)}
            className={cn(
              "-mb-px flex items-center gap-1.5 border-b-2 px-3 py-2 text-sm font-medium transition-colors",
              t.id === active
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground")}>
            {t.icon ? <t.icon className="h-4 w-4" /> : null}{t.label}
          </button>
        ))}
      </div>
      <div role="tabpanel">{current?.el}</div>
    </div>
  );
}
