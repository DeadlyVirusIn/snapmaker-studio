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

export interface PrinterProbe {
  reachable: boolean; host: string; port: number;
  klippy_state?: string; moonraker_version?: string; error?: string;
}
export interface PrinterStatus {
  host: string; port: number; print_state: string | null; filename: string | null;
  progress: number | null;
  bed: { temperature: number | null; target: number | null };
  toolheads: { index: number; temperature: number | null; target: number | null }[];
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
