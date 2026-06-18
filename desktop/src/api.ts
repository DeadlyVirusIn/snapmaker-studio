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

export async function libraryDelete(id: number): Promise<void> {
  const { port, token } = await apiInfo();
  const r = await fetch(`http://127.0.0.1:${port}/library/delete`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Auth-Token": token },
    body: JSON.stringify({ id }),
  });
  if (!r.ok) throw new Error(`delete failed (${r.status})`);
}

// Native open dialog limited to the formats the engine accepts.
export async function openModelDialog(): Promise<string | null> {
  const picked = await open({
    multiple: false,
    filters: [{ name: "3D models / projects", extensions: ["stl", "3mf"] }],
  });
  return typeof picked === "string" ? picked : null;
}
