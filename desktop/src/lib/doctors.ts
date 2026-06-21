// The Doctors — Snapmaker Studio's primary user-facing capabilities.
// Brand hierarchy (Unified Intelligence Hub Asset Pack):
//   Snapmaker Studio (platform) → Studio Intelligence (core engine) → the Doctors.
// "Studio Intelligence" is the engine that powers them; the Doctors are what the
// user sees and remembers. This registry is the single source of truth so every
// surface (Dashboard grid, Design Insights cards) renders them consistently.
import {
  FileCheck2, HeartPulse, Layers, Palette, Coins, Tag, TrendingUp,
  type LucideIcon,
} from "lucide-react";

export interface Doctor {
  id: string;
  name: string;
  icon: LucideIcon;
  // Workflow stage this Doctor mainly serves: Discover → Diagnose → Fix → Validate → Print.
  stage: "Discover" | "Diagnose" | "Fix" | "Validate" | "Print";
  // Spectrum token (the spectrum is reserved for the mark + status, per the Pack).
  token: string;
  // One-line promise — the question this Doctor answers for a novice.
  answers: string;
  tier: "P0" | "P1";
  // Where this Doctor lives in the app. Doctors that run on an open model route
  // to a landing page that explains them and opens a model; Printer Doctor has a
  // real page (Printers). Single source of truth for sidebar + dashboard cards.
  route: string;
}

export const DOCTORS: Doctor[] = [
  { id: "project", name: "Project Doctor", icon: FileCheck2, stage: "Diagnose",
    token: "--doctor-project", tier: "P0", route: "/doctor/project",
    answers: "Will it fit and print on your U1? Catches out-of-bounds before Orca." },
  { id: "printer", name: "Printer Doctor", icon: HeartPulse, stage: "Validate",
    token: "--doctor-printer", tier: "P0", route: "/printers",
    answers: "Is your U1 healthy? One 0–100 score from its own signals." },
  { id: "first-layer", name: "First Layer Doctor", icon: Layers, stage: "Diagnose",
    token: "--stage-input", tier: "P0", route: "/first-layer",
    answers: "Will the first layer stick? Adhesion & bed-mesh risk, explained." },
  { id: "multi-material", name: "Multi-Material Doctor", icon: Palette, stage: "Diagnose",
    token: "--stage-transform", tier: "P0", route: "/doctor/multi-material",
    answers: "Will your colours print right? Toolheads, mapping & purge checks." },
  { id: "cost", name: "Cost Doctor", icon: Coins, stage: "Print",
    token: "--doctor-cost", tier: "P1", route: "/doctor/cost",
    answers: "What does this print truly cost? Material, power, wear & labour." },
  { id: "pricing", name: "Pricing Doctor", icon: Tag, stage: "Print",
    token: "--stage-output", tier: "P1", route: "/doctor/pricing",
    answers: "What should you sell it for? A fair price with your margin." },
  { id: "profit", name: "Profit Doctor", icon: TrendingUp, stage: "Print",
    token: "--stage-output", tier: "P1", route: "/doctor/profit",
    answers: "What's your profit per print and across a whole batch?" },
];

/** Look up a Doctor by id (used by the generic Doctor landing route). */
export function doctorById(id: string | undefined): Doctor | null {
  return DOCTORS.find((d) => d.id === id) ?? null;
}
