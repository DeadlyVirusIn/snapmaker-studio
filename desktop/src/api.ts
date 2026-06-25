// Talks to the local Python sidecar. Port + token come from the Tauri shell,
// which spawned `python -m snapstudio_api` and read its handshake line.
import { invoke } from "@tauri-apps/api/core";
import { open } from "@tauri-apps/plugin-dialog";

type ApiInfo = { port: number; token: string };
let cached: ApiInfo | null = null;

async function apiInfo(): Promise<ApiInfo> {
  if (cached) return cached;
  // Dev/screenshot-harness only: let headless Edge point at a running backend via
  // ?api=PORT:TOKEN. Stripped from production builds (import.meta.env.DEV === false).
  if ((import.meta as any).env?.DEV) {
    const q = new URLSearchParams(location.search).get("api");
    if (q) { const [p, t] = q.split(":"); cached = { port: Number(p), token: t || "" }; return cached; }
  }
  cached = await invoke<ApiInfo>("get_api_info");
  return cached;
}
// Dev/screenshot-harness only: a sample file path from ?file= instead of the native picker.
function devFilePath(): string | null {
  if ((import.meta as any).env?.DEV) return new URLSearchParams(location.search).get("file");
  return null;
}

// Open the locked in-app Model Browser at an approved-site URL. Rust validates
// the URL against the domain allowlist; this is a thin pass-through.
export async function openModelBrowser(url: string): Promise<void> {
  await invoke("open_model_browser", { url });
}

// Studio-side control of the locked Model Browser window (the remote page never
// gets any IPC). The trusted Find Models panel uses these to close / reflect state.
export async function closeModelBrowser(): Promise<void> {
  await invoke("close_model_browser");
}

export async function isModelBrowserOpen(): Promise<boolean> {
  return invoke<boolean>("is_model_browser_open");
}

// Bring the locked Model Browser window to the front. No-op if it isn't open.
export async function focusModelBrowser(): Promise<void> {
  await invoke("focus_model_browser");
}

// Snapmaker Orca handoff. detectOrca() returns the install path (or null); the UI
// never displays that path. openInOrca() launches the verified Orca exe with the
// prepared file — a one-way handoff. Studio does not slice and does not control Orca.
export async function detectOrca(): Promise<string | null> {
  return invoke<string | null>("detect_orca");
}

export async function openInOrca(path: string): Promise<void> {
  await invoke("open_in_orca", { path });
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
          host?: string | null; filename?: string | null;
          factors?: Record<string, number> } = {},
): Promise<CostToPrice> {
  const { port, token } = await apiInfo();
  const body: Record<string, unknown> = { path, currency: opts.currency ?? "$", ...(opts.factors ?? {}) };
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

// Studio Intelligence Report: the one screen synthesising every Doctor.
export interface ReportRisk {
  doctor: string; level: "ok" | "warn" | "risk"; text: string;
  community?: { fix: string; success_pattern: string; confidence: string; sources: string[] };
}
export interface ReportEvidence { doctor: string; status: string; detail: string; }
export interface IntelligenceReport {
  available: boolean;
  studio_score?: number | null;
  print_success_score?: number | null;
  cost?: number | null;
  suggested_price?: number | null;
  margin_pct?: number | null;
  profit_per_print?: number | null;
  currency?: string;
  printer_compatibility?: "Compatible" | "Check" | "Unknown";
  risks?: ReportRisk[];
  biggest_risk?: ReportRisk | null;
  recommendations?: string[];
  next_action?: string;
  supporting?: ReportEvidence[];
  verdict?: string;
  reason?: string;
  is_demo?: boolean;
  demo_name?: string;
  expected_improvement?: { current: number; after_fixes: number; is_estimate: boolean; label: string } | null;
  comparison?: {
    issues_found: number; fixes_offered: number; prices_the_print: boolean;
    orca_line: string; studio_line: string;
  };
}
export async function demoReport(): Promise<IntelligenceReport> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/demo_report`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({}),
  });
  if (!r.ok) throw new Error(`demo_report failed (${r.status})`);
  return r.json();
}
export async function intelligenceReport(path: string, host?: string | null): Promise<IntelligenceReport> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/intelligence_report`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(host ? { path, host } : { path }),
  });
  if (!r.ok) throw new Error(`intelligence_report failed (${r.status})`);
  return r.json();
}

// Pricing Doctor: hobby / marketplace / premium selling prices.
export interface PricingTier { label: string; markup_pct: number; price: number; profit: number; margin_pct: number; why: string; }
export interface PricingDoctor {
  available: boolean; currency?: string; true_cost?: number;
  tiers?: PricingTier[]; verdict?: string; reason?: string;
}
export async function pricingDoctor(path: string, host?: string | null,
  opts: { currency?: string; factors?: Record<string, number> } = {}): Promise<PricingDoctor> {
  const { port, token } = await apiInfo();
  const body: Record<string, unknown> = { path, ...(opts.factors ?? {}) };
  if (host) body.host = host;
  if (opts.currency) body.currency = opts.currency;
  const r = await fetch(`http://127.0.0.1:${port}/pricing_doctor`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`pricing_doctor failed (${r.status})`);
  return r.json();
}

// Profit Doctor: profit per print, margin, batch, monthly, break-even.
export interface ProfitDoctor {
  available: boolean; currency?: string;
  profit_per_print?: number; margin_pct?: number; monthly_profit?: number;
  prints_per_month?: number; break_even_prints?: number | null;
  batch?: { count: number; profit: number }; verdict?: string; reason?: string;
}
export async function profitDoctor(path: string, host?: string | null,
  opts: { currency?: string; factors?: Record<string, number> } = {}): Promise<ProfitDoctor> {
  const { port, token } = await apiInfo();
  const body: Record<string, unknown> = { path, ...(opts.factors ?? {}) };
  if (host) body.host = host;
  if (opts.currency) body.currency = opts.currency;
  const r = await fetch(`http://127.0.0.1:${port}/profit_doctor`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`profit_doctor failed (${r.status})`);
  return r.json();
}

// Multi-Material Doctor: one verdict for a multicolour U1 print.
export interface MMDoctor {
  available: boolean;
  multi_material?: boolean;
  colors?: number;
  heads?: number;
  heads_known?: boolean;
  overall_level?: "ok" | "warn" | "risk";
  overall_text?: string;
  findings?: { level: "ok" | "warn" | "risk"; text: string }[];
  fixes?: string[];
  verdict?: string;
  reason?: string;
}
export async function mmDoctor(path: string, host?: string | null): Promise<MMDoctor> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/mm_doctor`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(host ? { path, host } : { path }),
  });
  if (!r.ok) throw new Error(`mm_doctor failed (${r.status})`);
  return r.json();
}

// Bed-Fit / Out-of-Bounds Doctor: does it fit the U1 bed, and if not, why + fix.
export interface BedFit {
  available: boolean;
  bed_known?: boolean;
  bed_source?: string;
  bed_mm?: { x: number; y: number; z: number };
  dims_mm?: { x: number; y: number; z: number };
  overall_level?: "ok" | "warn" | "risk";
  overall_text?: string;
  findings?: { level: "ok" | "warn" | "risk"; text: string }[];
  fixes?: string[];
  reason?: string;
}
export async function bedFit(path: string, host?: string | null): Promise<BedFit> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/bed_fit`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(host ? { path, host } : { path }),
  });
  if (!r.ok) throw new Error(`bed_fit failed (${r.status})`);
  return r.json();
}

// Print Success Prediction: pre-print "will it print?" odds from existing signals.
export interface SuccessPrediction {
  available: boolean;
  likelihood?: number;
  band?: "likely" | "uncertain" | "risky";
  factors?: string[];
  verdict?: string;
  reason?: string;
}
export async function predictSuccess(path: string, host?: string | null): Promise<SuccessPrediction> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/predict_success`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(host ? { path, host } : { path }),
  });
  if (!r.ok) throw new Error(`predict_success failed (${r.status})`);
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

// Firmware Capability Intelligence: what the U1's firmware actually exposes.
export interface FirmwareFeature { name: string; detail?: string; }
export interface PrinterFirmware {
  available: boolean;
  toolhead_count?: number | null;
  bed_mm?: { x: number; y: number; z: number } | null;
  macro_count?: number;
  extended_firmware?: boolean;
  features?: FirmwareFeature[];
  summary?: string;
  reason?: string;
}
export function printerFirmware(host: string, port = 7125): Promise<PrinterFirmware> {
  return printerPost("/printer/firmware", { host, port });
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

// ---- Printer Hub Phase B: control (every start/cancel/e-stop is confirmed in the UI) ----
export interface PrinterControlResult { ok?: boolean; action?: string; result?: string; filename?: string; path?: string; size?: number; }
export interface PrinterQueue { queue_state: string | null; jobs: { filename: string | null; id: string | null }[]; count: number; }

export function printerPause(host: string, port = 7125): Promise<PrinterControlResult> {
  return printerPost("/printer/control/pause", { host, port });
}
export function printerResume(host: string, port = 7125): Promise<PrinterControlResult> {
  return printerPost("/printer/control/resume", { host, port });
}
export function printerCancel(host: string, port = 7125): Promise<PrinterControlResult> {
  return printerPost("/printer/control/cancel", { host, port });
}
export function printerStartPrint(host: string, filename: string, port = 7125): Promise<PrinterControlResult> {
  return printerPost("/printer/control/start", { host, filename, port });
}
export function printerEmergencyStop(host: string, port = 7125): Promise<PrinterControlResult> {
  return printerPost("/printer/control/emergency_stop", { host, port });
}
export function printerJobQueue(host: string, port = 7125): Promise<PrinterQueue> {
  return printerPost("/printer/job_queue", { host, port });
}
export function printerUploadGcode(host: string, path: string, port = 7125): Promise<PrinterControlResult> {
  return printerPost("/printer/upload_gcode", { host, path, port });
}

// Native picker limited to sliced gcode, for uploading to the printer.
export async function openGcodeDialog(): Promise<string | null> {
  const picked = await open({ multiple: false, filters: [{ name: "Sliced gcode", extensions: ["gcode", "g", "gco"] }] });
  return typeof picked === "string" ? picked : null;
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
// ---- Per-Plate Filament Remapper (Commits A/B/C) ----
import type { PlateInspect, PlateDryRun, PlateExport } from "@/lib/plateRemapWizard";

async function platePost<T>(route: string, body: Record<string, unknown>): Promise<T> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}${route}`, {
    method: "POST", headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    let msg = `${route} failed (${r.status})`;
    try { const e = await r.json(); if (e?.error) msg = e.error; } catch { /* ignore */ }
    throw new Error(msg);
  }
  return r.json();
}

export function plateInspect(path: string): Promise<PlateInspect> {
  return platePost("/plate_inspect", { path });
}
export function plateDryRun(path: string, uiPlate: number, fromFilament: number, toFilament: number): Promise<PlateDryRun> {
  return platePost("/plate_dry_run", { path, ui_plate: uiPlate, from_filament: fromFilament, to_filament: toFilament });
}
export function plateExport(path: string, uiPlate: number, fromFilament: number, toFilament: number): Promise<PlateExport> {
  return platePost("/plate_export", { path, ui_plate: uiPlate, from_filament: fromFilament, to_filament: toFilament });
}

// ---- Print Quality Doctor (advisory, read-only) ----
export interface QualityEvidence { label: string; level: "ok" | "warn" | "risk"; text: string; doctor: string; }
export interface QualityResult {
  symptom: string;
  title: string;
  likely_causes: string[];
  first_checks: string[];
  orca_paths: string[];
  hardware_checks: string[];
  avoid: string[];
  evidence_needed: string[];
  disclaimer: string;
  evidence?: QualityEvidence[];        // file-specific findings (when a file is given)
  evidence_available?: boolean;
}
export interface QualityResponse { result: QualityResult | null; warnings: string[]; }
export function qualityCheck(symptom: string, path?: string): Promise<QualityResponse> {
  return platePost("/quality_check", path ? { symptom, path } : { symptom });
}

// ---- File/source ecosystem detection (read-only, advisory) ----
export interface SourceCompatibilityReport {
  schema_version: string;
  ecosystem: string;          // bambu-family | prusa | cura | generic | stl | unknown
  ecosystem_label: string;
  source_app: string | null;
  printer_model: string | null;
  is_u1: boolean;
  readable_settings: Record<string, unknown>;
  can_read: string[];
  cannot_convert: string[];
  risks: string[];
  recommended_next_step: string;
}
export function sourceCompatibility(path: string): Promise<SourceCompatibilityReport> {
  return platePost("/source_compatibility", { path });
}

// ---- First Layer Doctor (advisory, read-only) ----
export interface FirstLayerResult {
  symptom: string;
  title: string;
  likely_causes: string[];
  first_checks: string[];
  u1_checks: string[];
  slicer_checks: string[];
  avoid: string[];
  evidence_needed: string[];
  disclaimer: string;
}
export interface FirstLayerResponse { result: FirstLayerResult | null; warnings: string[]; }
export function firstLayerCheck(symptom: string): Promise<FirstLayerResponse> {
  return platePost("/first_layer_check", { symptom });
}

// ---- Scale Doctor (analysis-only preview) ----
export interface ScaleResult {
  available: boolean;
  reason?: string;
  scale_percent?: number;
  original_dimensions?: { x: number; y: number; z: number };
  scaled_dimensions?: { x: number; y: number; z: number };
  fits_build_volume?: boolean;
  estimated_material_delta?: { grams: number; basis: string };
  estimated_cost_delta?: { amount: number | null; basis: string };
  risks?: string[];
  recommendation?: "likely safe" | "caution" | "not recommended";
  explanation?: string;
}
export function scalePreview(path: string, scalePercent: number): Promise<ScaleResult> {
  return platePost("/scale_preview", { path, scale_percent: scalePercent });
}

// ---- Scale Options Ladder ----
export interface ScalePartDims {
  plate_index: number;
  name: string;
  dimensions: { x: number; y: number; z: number };
  fits_build_volume?: boolean;
}
export interface ScaleOption {
  label: string;
  scale_percent: number;
  risk_level: "low" | "medium" | "high";
  recommendation: string;
  dimensions_by_part: ScalePartDims[];
  explanation: string;
}
export interface ScaleOptionsResult {
  available: boolean;
  schema_version?: number;
  reason?: string;
  printer?: string;
  margin_mm?: number;
  build_volume?: { x: number; y: number; z: number };
  current_parts?: { plate_index: number; name: string; dimensions: { x: number; y: number; z: number } }[];
  group_scaling_recommended?: boolean;
  limiting_part?: string;
  limiting_axis?: string;
  recommended_scale_percent?: number;
  options?: ScaleOption[];
  warnings?: string[];
  next_steps?: string[];
}
export function scaleOptions(path: string, marginMm = 5, printer = "snapmaker_u1"): Promise<ScaleOptionsResult> {
  return platePost("/scale_options", { path, printer, margin_mm: marginMm });
}

// ---- Scale Doctor: prepare a scaled copy (writes a new file; original untouched) ----
export interface ScaledCopyResult {
  source_type?: string;
  output_path?: string;
  output_name?: string;
  validated_ok?: boolean;
  errors?: string[];
  scale_percent?: number;
  original_mm?: number[];   // [x, y, z]
  scaled_mm?: number[];     // [x, y, z]
  fits_u1?: boolean | null;
  blocked?: boolean;
}
export function prepareScaled(path: string, scalePercent: number): Promise<ScaledCopyResult> {
  return platePost("/prepare_scaled", { path, scale_percent: scalePercent });
}

// ---- Print Failure Troubleshooter (known-good aware) ----
export interface PrintFailureFinding {
  id: string;
  severity: string;
  title: string;
  evidence: string;
  explanation: string;
  suggested_action: string;
  safe_starting_point?: string;
}
export interface PrintFailureResult {
  available: boolean;
  schema_version?: string;
  reason?: string;
  summary?: string;
  confidence?: string;
  known_good_print?: boolean;
  known_good_context?: string;
  findings?: PrintFailureFinding[];
  troubleshooting_steps?: string[];
  compare_against_known_good?: string[];
  disclaimers?: string[];
}
export interface PrintFailureInput {
  path: string;
  symptom?: string;
  known_good_print?: boolean;
  known_good_material?: string;
  failed_material?: string;
  failure_stage?: string;
}
export function printFailureTroubleshoot(input: PrintFailureInput): Promise<PrintFailureResult> {
  return platePost("/print_failure_troubleshoot", { symptom: "fails_even_with_supports", ...input });
}

// ---- Model Discovery Hub v1 (search + link-out) ----
import type { SearchResponse, SearchFilters } from "@/lib/modelSearch";
export function modelSearch(query: string, filters: SearchFilters = {}): Promise<SearchResponse> {
  return platePost("/model_search", { query, filters });
}

// ---- Compatibility Doctor (read-only) ----
export interface CompatibilityFinding {
  id: string;
  severity: "error" | "warning" | "info";
  title: string;
  explanation: string;
  setting_path: string;
  suggested_action: string;
  evidence: string;
}
export interface CompatibilityResult {
  findings: CompatibilityFinding[];
  summary: string;
  recommendation: string;
}
export function compatibilityCheck(path: string): Promise<CompatibilityResult> {
  return platePost("/compatibility_check", { path });
}

// 3MF-only picker for the plate remap wizard (projects only — not bare STLs).
export async function open3mfDialog(): Promise<string | null> {
  const dev = devFilePath(); if (dev) return dev;
  const picked = await open({ multiple: false, filters: [{ name: "3MF project", extensions: ["3mf"] }] });
  return typeof picked === "string" ? picked : null;
}

export async function openModelDialog(): Promise<string | null> {
  const dev = devFilePath(); if (dev) return dev;
  const picked = await open({
    multiple: false,
    filters: [{ name: "3D models / projects", extensions: ["stl", "3mf"] }],
  });
  return typeof picked === "string" ? picked : null;
}

// Multi-select variant for batch conversion.
export async function openModelsDialog(): Promise<string[]> {
  const dev = devFilePath(); if (dev) return [dev];
  const picked = await open({
    multiple: true,
    filters: [{ name: "3D models / projects", extensions: ["stl", "3mf"] }],
  });
  if (Array.isArray(picked)) return picked;
  return typeof picked === "string" ? [picked] : [];
}
