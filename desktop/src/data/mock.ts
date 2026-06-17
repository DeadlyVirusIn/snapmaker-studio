// Mock data only — Phase A has no backend wiring. Names are generic placeholders.
import type { Verdict } from "@/components/ui/badge";

export interface MockProject {
  id: string;
  name: string;
  type: "stl" | "3mf";
  verdict: Verdict;
  score: number | null;
  colours: number;
  updated: string;
}

export const MOCK_PROJECTS: MockProject[] = [
  { id: "lantern", name: "Hex Lantern", type: "3mf", verdict: "REPAIRABLE", score: 90, colours: 4, updated: "2m ago" },
  { id: "cube", name: "Calibration Cube", type: "stl", verdict: "READY", score: 100, colours: 1, updated: "18m ago" },
  { id: "vase", name: "Spiral Vase", type: "stl", verdict: "CONVERTIBLE", score: null, colours: 1, updated: "1h ago" },
  { id: "bracket", name: "Printer Bracket", type: "3mf", verdict: "READY", score: 100, colours: 2, updated: "yesterday" },
  { id: "legacy", name: "Old Export", type: "3mf", verdict: "HIGH_RISK", score: 20, colours: 0, updated: "3d ago" },
];

export interface MockActivity {
  id: string;
  text: string;
  when: string;
}

export const MOCK_ACTIVITY: MockActivity[] = [
  { id: "a1", text: "Converted Calibration Cube to U1", when: "2m ago" },
  { id: "a2", text: "Doctor checked Hex Lantern — Repairable", when: "5m ago" },
  { id: "a3", text: "Optimized Spiral Vase", when: "1h ago" },
];

export const INSIGHTS = { projects: 5, ready: 2, needsWork: 3 };
