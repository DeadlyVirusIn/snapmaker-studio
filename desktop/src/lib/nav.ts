// Single source of truth for sidebar navigation. Kept free of JSX so the
// information architecture (which Doctors are directly reachable, where
// "Why Studio?" lives, route validity) is unit-testable.
//
// Judge-ready IA rules encoded here:
//  - every Doctor is directly reachable from the primary sidebar,
//  - Plate Color Remap sits next to the Multi-Material Doctor (same colour job),
//  - "Why Studio?" lives in the secondary/help area, never between workflow items,
//  - every nav destination resolves to a real route (no blank pages).
import {
  LayoutDashboard, FolderKanban, Wand2, Palette, GitCompareArrows,
  Settings, BookOpen, FileCheck2, HeartPulse, Layers, Coins, Tag, TrendingUp,
  ShieldCheck, Compass, Maximize2, Stethoscope, Rocket, FileSearch, type LucideIcon,
} from "lucide-react";
import { DOCTORS } from "@/lib/doctors";

export interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  end?: boolean;
  /** Doctor id when this item is one of the Doctors (for grouping assertions). */
  doctorId?: string;
}

const doctorRoute = (id: string) => DOCTORS.find((d) => d.id === id)!.route;

// Primary workflow — Dashboard, where to open models, then the Doctors in the
// order a user meets them, with Plate Color Remap beside the Multi-Material
// Doctor, and Batch Prepare last.
export const PRIMARY_NAV: NavItem[] = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/start", label: "Get Started", icon: Rocket },
  { to: "/projects", label: "Projects", icon: FolderKanban },
  { to: "/find-models", label: "Find Models", icon: Compass },
  { to: "/source", label: "Source Check", icon: FileSearch },
  { to: doctorRoute("project"), label: "Project Doctor", icon: FileCheck2, doctorId: "project" },
  { to: "/compatibility", label: "Compatibility Doctor", icon: ShieldCheck },
  { to: "/scale", label: "Scale Doctor", icon: Maximize2 },
  { to: "/print-quality", label: "Print Quality Doctor", icon: Stethoscope },
  { to: doctorRoute("printer"), label: "Printer Doctor", icon: HeartPulse, doctorId: "printer" },
  { to: doctorRoute("first-layer"), label: "First Layer Doctor", icon: Layers, doctorId: "first-layer" },
  { to: doctorRoute("multi-material"), label: "Multi-Material Doctor", icon: Palette, doctorId: "multi-material" },
  { to: "/plate-remap", label: "Plate Color Remap", icon: GitCompareArrows },
  { to: doctorRoute("cost"), label: "Cost Doctor", icon: Coins, doctorId: "cost" },
  { to: doctorRoute("pricing"), label: "Pricing Doctor", icon: Tag, doctorId: "pricing" },
  { to: doctorRoute("profit"), label: "Profit Doctor", icon: TrendingUp, doctorId: "profit" },
  { to: "/batch", label: "Batch Prepare", icon: Wand2 },
];

// Simple mode IA: a short beginner path up top, the rest tucked under "More
// tools". Advanced mode keeps the full PRIMARY_NAV. Derived from PRIMARY_NAV so
// there's still one source of truth (and routes stay validated).
const BEGINNER_ROUTES: string[] = [
  "/", "/start", doctorRoute("project"), "/find-models", "/projects",
];
export const BEGINNER_NAV: NavItem[] =
  BEGINNER_ROUTES.map((r) => PRIMARY_NAV.find((n) => n.to === r)!);
export const MORE_NAV: NavItem[] =
  PRIMARY_NAV.filter((n) => !BEGINNER_ROUTES.includes(n.to));

// Secondary — supporting / about / help. "Why Studio?" is here on purpose so it
// supports the story without interrupting the task flow.
export const SECONDARY_NAV: NavItem[] = [
  { to: "/why", label: "Why Studio?", icon: GitCompareArrows },
  { to: "/help", label: "Docs / Help", icon: BookOpen },
  { to: "/settings", label: "Settings", icon: Settings },
];

// Static routes the app actually mounts (App.tsx). Doctor landings are dynamic
// (/doctor/:id) and validated against DOCTORS below.
export const STATIC_ROUTES = new Set<string>([
  "/", "/projects", "/batch", "/workspace", "/printers", "/settings",
  "/why", "/plate-remap", "/compatibility", "/scale", "/print-quality", "/first-layer", "/find-models", "/start", "/help", "/source",
]);

/** True when a nav `to` resolves to a real route — guards against blank pages. */
export function isKnownRoute(to: string): boolean {
  if (STATIC_ROUTES.has(to)) return true;
  const m = /^\/doctor\/([a-z-]+)$/.exec(to);
  return !!m && DOCTORS.some((d) => d.id === m[1]);
}
