import * as React from "react";
import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

/** Consistent page header used across every screen: branded icon tile, title,
 *  subtitle, optional right-aligned actions and an optional status pill. */
export function PageHeader({
  icon: Icon, title, subtitle, actions, badge, className,
}: {
  icon: LucideIcon; title: string; subtitle?: string;
  actions?: React.ReactNode; badge?: React.ReactNode; className?: string;
}) {
  return (
    <div className={cn("flex flex-wrap items-start gap-3", className)}>
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/15">
        <Icon className="h-[22px] w-[22px]" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <h2 className="text-2xl font-semibold tracking-tight">{title}</h2>
          {badge}
        </div>
        {subtitle && <p className="mt-0.5 text-sm text-muted-foreground">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}

/** Small section label with optional trailing element (e.g. a "view all" link). */
export function SectionTitle({ children, trailing, className }: {
  children: React.ReactNode; trailing?: React.ReactNode; className?: string;
}) {
  return (
    <div className={cn("mb-3 flex items-center justify-between", className)}>
      <h3 className="text-sm font-semibold tracking-tight">{children}</h3>
      {trailing}
    </div>
  );
}

/** Value-explaining empty state: icon, what it is, why it matters, an action. */
export function EmptyState({
  icon: Icon, title, description, action, className,
}: {
  icon: LucideIcon; title: string; description: string;
  action?: React.ReactNode; className?: string;
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-3 py-14 text-center", className)}>
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted text-muted-foreground">
        <Icon className="h-6 w-6" />
      </div>
      <div className="max-w-sm space-y-1">
        <p className="font-medium">{title}</p>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      {action}
    </div>
  );
}
