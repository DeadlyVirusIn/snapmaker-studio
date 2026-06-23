// Pure logic + copy for the Model Discovery Hub (v1: search + link-out only).
// No JSX so filters, link-out URLs, and import-gating display are unit-testable.
// Source of truth: docs/design/MODEL_DISCOVERY_HUB.md.

export type ModelSource = "thingiverse" | "myminifactory" | "cults3d";

export interface ModelSearchResult {
  title: string;
  source: ModelSource;
  source_url: string;
  thumbnail_url?: string | null;
  license?: string | null;
  price_status?: "free" | "paid" | "unknown";
  file_formats?: string[];
  tags?: string[];
  attribution?: string | null;
  import_allowed: boolean;
  reason_import_not_allowed?: string;
}

export interface SearchResponse {
  results: ModelSearchResult[];
  providers_queried: string[];
  warnings: string[];
}

export interface SearchFilters {
  freeOnly?: boolean;
  commercialUse?: boolean;
  formats?: string[];          // e.g. ["STL","3MF"]
  multiColor?: boolean;
  sources?: ModelSource[];
}

export const SANCTIONED_SOURCES: ModelSource[] = ["thingiverse", "myminifactory", "cults3d"];

// Link-out-only providers: we never render normalized cards from them, only a
// button that opens their own search page.
export const LINK_OUT_PROVIDERS = [
  { id: "printables", label: "Printables" },
  { id: "thangs", label: "Thangs" },
  { id: "makerworld", label: "MakerWorld" },
] as const;

export const DISCLAIMER =
  "Models are provided by their source websites. Respect each model's license and creator terms.";

// Model Browser direction: the approved-site list a novice browses (link-out).
// Every entry has a home page and a search URL — Studio only ever opens these in
// the browser; it never scrapes, imports, or bypasses a site's terms.
export const BROWSE_PROVIDERS = [
  { id: "printables", label: "Printables", home: "https://www.printables.com" },
  { id: "thingiverse", label: "Thingiverse", home: "https://www.thingiverse.com" },
  { id: "myminifactory", label: "MyMiniFactory", home: "https://www.myminifactory.com" },
  { id: "cults3d", label: "Cults3D", home: "https://cults3d.com" },
  { id: "thangs", label: "Thangs", home: "https://thangs.com" },
  { id: "makerworld", label: "MakerWorld", home: "https://makerworld.com" },
] as const;

export function siteHomeUrl(source: string): string {
  return BROWSE_PROVIDERS.find((p) => p.id === source)?.home ?? "";
}

// Mirror of the Rust allowlist (desktop/src-tauri/src/main.rs). This is a
// frontend convenience check only — Rust is the real security boundary that
// blocks off-allowlist navigation in the in-app Model Browser.
export const APPROVED_MODEL_DOMAINS = [
  "printables.com", "thingiverse.com", "myminifactory.com",
  "cults3d.com", "thangs.com", "makerworld.com",
] as const;

export function isApprovedModelUrl(url: string): boolean {
  try {
    const u = new URL(url);
    if (u.protocol !== "https:") return false;
    const h = u.hostname.toLowerCase();
    return APPROVED_MODEL_DOMAINS.some((d) => h === d || h.endsWith(`.${d}`));
  } catch {
    return false;
  }
}

export function linkOutUrl(source: string, query: string): string {
  const q = encodeURIComponent(query || "");
  if (!q) return siteHomeUrl(source);
  switch (source) {
    case "printables": return `https://www.printables.com/search/models?q=${q}`;
    case "thingiverse": return `https://www.thingiverse.com/search?q=${q}&type=things`;
    case "myminifactory": return `https://www.myminifactory.com/search?query=${q}`;
    case "cults3d": return `https://cults3d.com/en/search?q=${q}`;
    case "thangs": return `https://thangs.com/search/${q}`;
    case "makerworld": return `https://makerworld.com/en/search/models?keyword=${q}`;
    default: return "";
  }
}

/** Plain-English label for why import is disabled (v1 disables all import). */
export function importReasonLabel(reason?: string): string {
  switch (reason) {
    case "paid": return "Paid model — open on the source site";
    case "no_download_api": return "No download API — open on the source site";
    case "license_unclear": return "License unclear — open on the source site";
    case "auth_required": return "Sign-in required on the source site";
    case "source_link_out_only":
    default: return "Import coming later — open on the source site";
  }
}

function isCommercialLicense(license?: string | null): boolean {
  if (!license) return false;
  const l = license.toLowerCase();
  // CC-BY (without NC) and explicit commercial terms allow commercial use.
  if (l.includes("nc") || l.includes("noncommercial") || l.includes("non-commercial")) return false;
  return l.includes("commercial") || l.includes("cc-by") || l.includes("cc by") || l.includes("standard");
}

/** Pure client-side filtering of normalized results. */
export function filterResults(results: ModelSearchResult[], filters: SearchFilters): ModelSearchResult[] {
  return results.filter((r) => {
    if (filters.freeOnly && r.price_status !== "free") return false;
    if (filters.commercialUse && !isCommercialLicense(r.license)) return false;
    if (filters.multiColor && !(r.tags ?? []).some((t) => /multi.?color|multicolour|amms?|mmu/i.test(t))) return false;
    if (filters.formats && filters.formats.length) {
      const fmts = (r.file_formats ?? []).map((f) => f.toUpperCase());
      if (!filters.formats.some((f) => fmts.includes(f.toUpperCase()))) return false;
    }
    if (filters.sources && filters.sources.length && !filters.sources.includes(r.source)) return false;
    return true;
  });
}
