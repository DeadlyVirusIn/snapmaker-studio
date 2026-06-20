// Talks to the local Python sidecar. Port + token come from the Tauri shell,
// which spawned `python -m snapstudio_api` and read its handshake line.
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";

type ApiInfo = { port: number; token: string };
let cached: ApiInfo | null = null;

async function apiInfo(): Promise<ApiInfo> {
  if (!cached) cached = await invoke<ApiInfo>("get_api_info");
  return cached;
}

export async function health(): Promise<any> {
  const { port } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/health`);
  return r.json();
}

export async function doctor(path: string): Promise<any> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/doctor`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ path }),
  });
  if (!r.ok) throw new Error(`doctor failed (${r.status})`);
  return r.json();
}

export async function convert(path: string, outDir?: string): Promise<any> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/convert`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ path, out_dir: outDir ?? null }),
  });
  if (!r.ok) {
    let msg = `convert failed (${r.status})`;
    try { const e = await r.json(); if (e?.error) msg = e.error; } catch { /* ignore */ }
    throw new Error(msg);
  }
  return r.json();
}

export async function diff(a: string, b: string): Promise<any> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/diff`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ a, b }),
  });
  if (!r.ok) {
    let msg = `diff failed (${r.status})`;
    try { const e = await r.json(); if (e?.error) msg = e.error; } catch { /* ignore */ }
    throw new Error(msg);
  }
  return r.json();
}

export interface LibraryProject {
  id: number;
  name: string;
  source_path: string;
  source_family: string | null;
  output_path: string | null;
  verdict: string | null;
  score: number | null;
  filament_count: number | null;
  last_action: string | null;
  updated_at: string | null;
}

export async function library(query = "", tag?: string): Promise<LibraryProject[]> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/library`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ query, tag: tag ?? null }),
  });
  if (!r.ok) throw new Error(`library failed (${r.status})`);
  const data = await r.json();
  return data.projects ?? [];
}

export interface HistoryEvent {
  id: number;
  project_id: number;
  action: string;
  detail: string;
  at: string;
}

export async function history(projectId: number): Promise<HistoryEvent[]> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/history`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ project_id: projectId }),
  });
  if (!r.ok) throw new Error(`history failed (${r.status})`);
  const data = await r.json();
  return data.events ?? [];
}

export async function libraryDelete(id: number): Promise<void> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/library/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ id }),
  });
  if (!r.ok) throw new Error(`delete failed (${r.status})`);
}

export interface BatchItem {
  path: string;
  status: "pending" | "running" | "done" | "error";
  output_path: string | null;
  output_name: string | null;
  validated_ok: boolean | null;
  error: string | null;
}

export interface BatchSnapshot {
  items: BatchItem[];
  total: number;
  done: number;
  failed: number;
  finished: boolean;
}

export interface BatchJobStatus {
  id: string;
  status: "running" | "done" | "error";
  error: string | null;
  result: BatchSnapshot | null;
}

export async function batchStart(paths: string[], outDir?: string): Promise<{ job_id: string; total: number }> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/batch`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ paths, out_dir: outDir ?? null }),
  });
  if (!r.ok) {
    let msg = `batch failed (${r.status})`;
    try { const e = await r.json(); if (e?.error) msg = e.error; } catch { /* ignore */ }
    throw new Error(msg);
  }
  return r.json();
}

export async function batchStatus(jobId: string): Promise<BatchJobStatus> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/batch/status`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ job_id: jobId }),
  });
  if (!r.ok) throw new Error(`batch status failed (${r.status})`);
  return r.json();
}

export interface Insights {
  schema_version: string;
  name: string;
  source_type: string | null;
  source_family: string | null;
  verdict: string | null;
  readiness_score: number | null;
  is_compatible: boolean;
  objects: number | null;
  plates: number | null;
  colors: number | null;
  painted: boolean;
  materials: { color: string; type: string | null }[];
  dimensions_mm: { x: number; y: number; z: number } | null;
  triangles: number | null;
  complexity: string | null;
  issues: string[];
}

export async function insights(path: string): Promise<Insights> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/insights`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ path }),
  });
  if (!r.ok) throw new Error(`insights failed (${r.status})`);
  return r.json();
}

export interface ReadinessReport {
  schema_version: string;
  name: string;
  verdict: string | null;
  readiness_score: number | null;
  ready: boolean;
  checks: { name: string; status: "pass" | "warn" | "fail"; detail: string }[];
  preserved: string[];
  changes: string[];
  at_risk: string[];
  warnings: string[];
}

export async function report(path: string): Promise<ReadinessReport> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ path }),
  });
  if (!r.ok) throw new Error(`report failed (${r.status})`);
  return r.json();
}

export interface FirstLayerReport {
  available: boolean;
  bed_aware?: boolean;
  overall_level?: "ok" | "warn" | "risk";
  overall_text?: string;
  findings?: { level: "ok" | "warn" | "risk"; text: string }[];
  signals_used?: string[];
  reason?: string;
}
export async function firstLayer(path: string, host?: string | null): Promise<FirstLayerReport> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/first_layer`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ path, host: host ?? null }),
  });
  if (!r.ok) throw new Error(`first_layer failed (${r.status})`);
  return r.json();
}

export interface ToolheadFitReport {
  available: boolean;
  printer_aware?: boolean;
  color_count?: number;
  toolhead_count?: number;
  overall_level?: "ok" | "warn" | "risk";
  overall_text?: string;
  findings?: { level: "ok" | "warn" | "risk"; text: string }[];
  reason?: string;
}
export async function toolheadFit(path: string, host?: string | null): Promise<ToolheadFitReport> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/toolhead_fit`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ path, host: host ?? null }),
  });
  if (!r.ok) throw new Error(`toolhead_fit failed (${r.status})`);
  return r.json();
}

export interface CostEstimate {
  available: boolean;
  grams?: number;
  price_per_kg?: number;
  currency?: string;
  cost?: number;
  basis?: string;
  reason?: string;
}
export async function costEstimate(path: string, pricePerKg = 20, currency = "$"): Promise<CostEstimate> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/cost_estimate`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ path, price_per_kg: pricePerKg, currency }),
  });
  if (!r.ok) throw new Error(`cost_estimate failed (${r.status})`);
  return r.json();
}

// Cost-to-Price Intelligence: true cost + suggested selling price with margin.
export interface CostToPrice {
  available: boolean;
  time_known?: boolean;
  grams?: number;
  print_hours?: number | null;
  currency?: string;
  breakdown?: {
    material: number; electricity: number; depreciation: number;
    labor: number; failure_buffer: number; marketplace_fee: number;
  };
  true_cost?: number;
  markup_pct?: number;
  suggested_price?: number;
  margin?: number;
  margin_pct?: number;
  basis?: string;
  verdict?: string;
  reason?: string;
}
export async function costToPrice(
  path: string,
  opts: { pricePerKg?: number; currency?: string; markupPct?: number;
          host?: string | null; filename?: string | null } = {},
): Promise<CostToPrice> {
  const { port, token } = await apiInfo();
  const body: Record<string, unknown> = { path, currency: opts.currency ?? "$" };
  if (opts.pricePerKg != null) body.price_per_kg = opts.pricePerKg;
  if (opts.markupPct != null) body.markup_pct = opts.markupPct;
  if (opts.host) body.host = opts.host;
  if (opts.filename) body.filename = opts.filename;
  const r = await fetch(`http://127.0.0.1:${port}/cost_to_price`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`cost_to_price failed (${r.status})`);
  return r.json();
}

// Business Mode: a whole batch rolled into one cost / price / profit P&L.
export interface BatchPricing {
  available: boolean;
  parts?: number;
  currency?: string;
  total_grams?: number;
  total_cost?: number;
  total_price?: number;
  total_profit?: number;
  margin_pct?: number;
  avg_price?: number;
  time_known?: boolean;
  verdict?: string;
  reason?: string;
}
export async function batchPricing(
  paths: string[],
  opts: { pricePerKg?: number; currency?: string; markupPct?: number } = {},
): Promise<BatchPricing> {
  const { port, token } = await apiInfo();
  const body: Record<string, unknown> = { paths, currency: opts.currency ?? "$" };
  if (opts.pricePerKg != null) body.price_per_kg = opts.pricePerKg;
  if (opts.markupPct != null) body.markup_pct = opts.markupPct;
  const r = await fetch(`http://127.0.0.1:${port}/batch_pricing`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`batch_pricing failed (${r.status})`);
  return r.json();
}

export interface FailureInsights {
  available: boolean;
  overall_level?: "ok" | "warn" | "risk";
  overall_text?: string;
  total?: number;
  failed?: number;
  failure_rate?: number;
  recent_failure_streak?: number;
  top_cause?: string | null;
  repeat_offenders?: { filename: string; failures: number }[];
  findings?: { level: "ok" | "warn" | "risk"; text: string }[];
  reason?: string;
}
export function printerFailureInsights(host: string, port = 7125): Promise<FailureInsights> {
  return printerPost("/printer/failure_insights", { host, port });
}

// Printer Health Score: one 0–100 from the U1's own read-only firmware + history signals.
export interface PrinterHealth {
  available: boolean;
  score?: number;
  grade?: "A" | "B" | "C" | "D" | "F";
  drivers?: string[];
  basis?: string;
  verdict?: string;
  reason?: string;
}
export function printerHealth(host: string, port = 7125): Promise<PrinterHealth> {
  return printerPost("/printer/health", { host, port });
}

export interface MeshReport {
  schema_version: string;
  available: boolean;
  reason?: string;
  triangle_count?: number;
  integrity?: {
    watertight: boolean; manifold: boolean; open_edges: number; holes: number;
    non_manifold_edges: number; degenerate_faces: number; duplicate_faces: number;
    winding_consistent: boolean;
  };
  overhang?: { overhang_pct: number; severe_pct: number; supports_likely: boolean };
  stability?: { tip_risk: boolean; com_over_base: boolean; margin_mm: number | null; height_mm: number; aspect: number };
  volume_mm3?: number;
  volume_cm3?: number;
  surface_area_mm2?: number;
  material_estimate_g?: number | null;
  findings?: { level: "ok" | "warn" | "risk"; text: string }[];
}

export async function mesh(path: string): Promise<MeshReport> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/mesh`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ path }),
  });
  if (!r.ok) throw new Error(`mesh failed (${r.status})`);
  return r.json();
}

export interface PrintStrategy {
  id: string;
  name: string;
  explanation: string;
  intent: string;
  use_cases: string[];
  tradeoffs: string;
  settings: Record<string, string>;
}
export interface StrategyList {
  schema_version: string;
  default: string;
  strategies: PrintStrategy[];
  categories: Record<string, string>;
  notes: string;
}
export interface StrategyRecommendation {
  recommended: string;
  reason: string;
  warnings: string[];
  signals_used: string[];
  estimated_note: string;
  signals: { colors: number | null; source_family: string | null; dimensions_mm: { x: number; y: number; z: number } | null; complexity: string | null };
}

export async function strategies(): Promise<StrategyList> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/strategies`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token }, body: "{}",
  });
  if (!r.ok) throw new Error(`strategies failed (${r.status})`);
  return r.json();
}

export async function strategyRecommend(path: string): Promise<StrategyRecommendation> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/strategy/recommend`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ path }),
  });
  if (!r.ok) throw new Error(`recommend failed (${r.status})`);
  return r.json();
}

export interface PrinterProbe {
  reachable: boolean; host: string; port: number;
  klippy_state?: string; moonraker_version?: string; error?: string;
}
export interface PrinterStatus {
  host: string; port: number; print_state: string | null; filename: string | null;
  message: string | null;
  progress: number | null;
  print_duration_s: number | null; total_duration_s: number | null; filament_used_mm: number | null;
  current_layer: number | null; total_layer: number | null;
  speed_factor: number | null; extrude_factor: number | null;
  bed: { temperature: number | null; target: number | null };
  toolheads: { index: number; temperature: number | null; target: number | null; active?: boolean }[];
}
export interface PrinterJob {
  filename: string | null; status: string | null;
  start_time: number | null; end_time: number | null;
  print_duration_s: number | null; total_duration_s: number | null; filament_used_mm: number | null;
}
export interface PrinterHistory {
  host: string; port: number; jobs: PrinterJob[]; failures: PrinterJob[];
  totals: { total_jobs: number | null; total_print_time_s: number | null; total_time_s: number | null;
    total_filament_used_mm: number | null; longest_print_s: number | null };
}
export interface PrinterDiagnostics {
  host: string; port: number; klippy_state?: string; state_message?: string | null;
  hostname?: string; warnings: string[]; failed_components: string[]; healthy: boolean;
}

async function printerPost<T>(path: string, body: object): Promise<T> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}${path}`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${path} failed (${r.status})`);
  return r.json();
}

export function printerHistory(host: string, port = 7125): Promise<PrinterHistory> {
  return printerPost("/printer/history", { host, port, limit: 20 });
}
export function printerDiagnostics(host: string, port = 7125): Promise<PrinterDiagnostics> {
  return printerPost("/printer/diagnostics", { host, port });
}
export interface PrinterFileMetadata {
  available: boolean; filename: string;
  estimated_time_s?: number | null; filament_total_mm?: number | null; filament_weight_g?: number | null;
  filament_type?: string | null; layer_count?: number | null; layer_height?: number | null;
  first_layer_height?: number | null; object_height?: number | null;
  first_layer_bed_temp?: number | null; first_layer_extr_temp?: number | null;
  slicer?: string | null; slicer_version?: string | null; thumbnail_count?: number;
}
export function printerFileMetadata(host: string, filename: string, port = 7125): Promise<PrinterFileMetadata> {
  return printerPost("/printer/file_metadata", { host, filename, port });
}
export interface PrinterCapabilities {
  host: string; port: number; toolhead_count: number | null;
  bed_mm: { x: number; y: number; z: number } | null;
}
export function printerCapabilities(host: string, port = 7125): Promise<PrinterCapabilities> {
  return printerPost("/printer/capabilities", { host, port });
}

export async function printerDiscover(hosts?: string[]): Promise<PrinterProbe[]> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/printer/discover`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ hosts: hosts ?? null }),
  });
  if (!r.ok) throw new Error(`discover failed (${r.status})`);
  return (await r.json()).printers ?? [];
}

export async function printerStatus(host: string, port = 7125): Promise<PrinterStatus> {
  const { port: p, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${p}/printer/status`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ host, port }),
  });
  if (!r.ok) throw new Error(`status failed (${r.status})`);
  return r.json();
}

// Native open dialog limited to the formats the engine accepts.
export async function openModelDialog(): Promise<string | null> {
  const picked = await open({
    multiple: false,
    filters: [{ name: "3D models / projects", extensions: ["stl", "3mf"] }],
  });
  return typeof picked === "string" ? picked : null;
}

// Multi-select variant for batch conversion.
export async function openModelsDialog(): Promise<string[]> {
  const picked = await open({
    multiple: true,
    filters: [{ name: "3D models / projects", extensions: ["stl", "3mf"] }],
  });
  if (Array.isArray(picked)) return picked;
  return typeof picked === "string" ? [picked] : [];
}
