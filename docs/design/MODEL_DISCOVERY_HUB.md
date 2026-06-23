# Model Discovery Hub — Feasibility Audit (research only, not implemented)

> **FUTURE / ASPIRATIONAL — NOT shipped in beta.10.** Any API access, auto-import,
> or download-interception ideas in this document are research only. Beta.10 ships
> an approved-site **Model Browser** with manual download/open, **no API keys**, and
> **no auto-import**. Do not read this doc as a description of current behavior.

> Status: **research/plan only. No code, no scraping, no downloads.** Decide scope
> before any implementation. Sources verified June 2026; APIs and ToS change —
> re-verify before building.

## What this is

An in-app way to find printable models, understand their source/license, import
them **only when clearly allowed**, and immediately run Studio Doctors to decide
if they'll print on a Snapmaker U1. Positioned as the **Model Discovery Hub**
("Find Models"), the Discover entry point of Discover → Diagnose → Fix → Validate
→ Print. Not a generic web search bar.

User story: *"I want a model. Studio helps me find one, checks if I'm allowed to
use it, imports it when safe, and tells me if it will print on my U1 before I
waste filament."*

## Source-by-source audit

| Source | Official search API | Direct download via API | Thumbnail allowed | License/price metadata | Auth / rate limits | Recommendation |
|---|---|---|---|---|---|---|
| **Thingiverse** | Yes — REST, `/search/{term}`, Swagger docs | Yes, gated by each thing's license | Yes (API-provided URLs) | Yes (license field; mostly CC, attribution) | App token / OAuth; rate-limited | **Include v1** (search + link-out (import later, when licensed)) |
| **MyMiniFactory** | Yes — documented API + OAuth2; free & paid | Yes for free objects via authed user; paid never | Yes (API images) | Yes (license + price; paid marketplace mix) | OAuth2 client; guidelines forbid scraping/recreating/competing | **Include v1** (metadata + link-out; import free-only, later) |
| **Cults3D** | Yes — GraphQL, search/trending/filters | **No** — files stay on Cults "for legal reasons" | Yes (photos in API) | Yes (price/license; mostly paid) | API key, HTTP Basic; ~60 req/30s, 500/day | **Include v1 metadata + link-out only** (never import) |
| **Printables** | **No official public API** (only unofficial/community) | No sanctioned path | Via site only | On site | n/a (unofficial would risk ToS) | **Link-out only** (open printables.com search; no programmatic results) |
| **Thangs** | Unconfirmed public search API (geometric search engine; no clear official docs) | Unknown | Unknown | Unknown | Unknown | **Link-out only** until an official API is confirmed |
| **MakerWorld (Bambu)** | **No public API**; ToS restricts third-party file sharing | No | No | On site | n/a | **Exclude from API search v1** (optional link-out later) |

Notes:
- "Include v1" = call the sanctioned API server-side, normalize, show results.
- "Link-out only" = a button that opens the site's own search in the browser; no
  fetching, no scraping, no result cards from us.
- "Exclude" = not surfaced as a searchable provider in v1.

## Recommended v1 product scope

Read / search / link-out first; import later.

In scope:
- Server-side metadata search across **Thingiverse, MyMiniFactory, Cults3D** only.
- Result cards: thumbnail (API-provided), title, source, license/price, tags.
- **"Open on source site"** on every result.
- Filters: free only, commercial-use allowed, STL/3MF, multi-color, source.
- **"Import to Studio"** shown only when `import_allowed` is true (initially only
  Thingiverse free/licensed; MyMiniFactory free via OAuth in a later step).
- Link-out tiles for Printables / Thangs / MakerWorld (open their own search).
- Disclaimer on the page: *"Models are provided by their source websites. Respect
  each model's license and creator terms."*

Hard rules (carried from the brief):
- No mirroring, no re-hosting, no paywall/login bypass, no scraping where
  prohibited, never present paid files as free, never commit/download third-party
  models into the repo, never reuse paid/commercial names from private validation
  fixtures, thumbnails only where the site/API permits, license/attribution always
  visible.

Out of scope for v1: Cults3D import (no file API), Printables/Thangs/MakerWorld
programmatic results, any unofficial/scraped endpoints.

## Data model

```
ModelSearchResult {
  title: string
  source: "thingiverse" | "myminifactory" | "cults3d"   // sanctioned providers only
  source_url: string                                     // canonical model page (link-out)
  thumbnail_url?: string                                 // only if provider allows display
  license?: string                                       // e.g. "CC-BY-4.0", "Standard", null if unknown
  price_status?: "free" | "paid" | "unknown"
  file_formats?: string[]                                // e.g. ["STL","3MF"]
  tags?: string[]
  attribution?: string                                   // creator/handle + required notice
  import_allowed: boolean                                // computed server-side
  reason_import_not_allowed?:
      "paid" | "no_download_api" | "license_unclear"
    | "auth_required" | "source_link_out_only"
}
```

`import_allowed` is computed, never trusted from the client. Default false; set
true only when provider + license + price all clearly permit (e.g. Thingiverse
free CC model with a download endpoint).

## Backend / API proposal

Both server-side so API keys/secrets never reach the client.

- `POST /model_search { query, filters }` → `{ results: ModelSearchResult[], providers_queried, warnings }`.
  Fans out to enabled provider adapters, normalizes, dedupes, applies filters.
  Holds keys server-side, caches responses, backs off on rate limits.
- `POST /model_import { source, source_id, dest_dir }` → `{ path }`, **only** for
  permitted sources/items (re-checks `import_allowed` server-side). Downloads to a
  user-chosen directory (never the repo), then the UI auto-runs Project Doctor on
  the path. Refuses paid / no-download-API / unclear-license items with a reason.

Provider adapters are isolated modules with a strict whitelist; anything not on
the sanctioned list cannot be queried (no-scrape guard).

## UI placement

- Sidebar: **Find Models** in the primary group, near Projects / top of the
  Discover area (it's the entry to the flow). Route `/find-models`.
- Search page: search bar; filter row (free only · commercial-use · STL/3MF ·
  multi-color · source); result cards (thumbnail, title, source, license/price,
  "Open on source site", "Import to Studio" when allowed); persistent disclaimer.
- After a permitted import: auto-run Project Doctor and show fits-U1 yes/no,
  supports-likely, multi-material/color warning, estimated material/cost,
  recommended next action.

## Required tests

- Adapter normalization from **recorded fixtures** (no live network in CI) →
  correct `ModelSearchResult` per provider.
- `import_allowed` gating: paid → false `reason: "paid"`; Cults3D → false
  `reason: "no_download_api"`; unclear license → false.
- Paid detection never yields a download path; "Import" button hidden when not
  allowed.
- License + attribution always mapped into the result and rendered.
- Link-out URL builder produces canonical source URLs; link-out-only providers
  never produce result cards.
- No-scrape guard: querying a non-whitelisted provider is rejected.
- UI filter logic (free-only, commercial-use, format, source) is pure-testable.

## Legal / IP risk list

- ToS variance per site; scraping prohibited on several (Printables, MakerWorld)
  → never scrape; use sanctioned APIs or link-out only.
- Thumbnail rights: display only provider-supplied images per their terms; no
  mirroring/re-hosting/caching beyond what's allowed.
- License accuracy: CC variants and attribution requirements must be shown
  correctly; wrong license display is a real risk → show raw license + attribution.
- Paid/commercial models: never download, never imply free; respect marketplace
  rules (Cults3D/MyMiniFactory).
- Credentials: API keys/OAuth secrets server-side only; user OAuth for any
  per-user downloads (MyMiniFactory).
- Rate limits/fair use (e.g. Cults3D 500/day) → cache + backoff; don't rebuild a
  competitor index (explicitly disallowed by MyMiniFactory guidelines).
- Liability: keep the "provided by source websites, respect each license"
  disclaimer visible.
- This audit is engineering guidance, not legal advice; have terms reviewed before
  shipping import for any source.

## Recommended implementation order

1. **beta.3 UX/nav patch release** (already validated) — ship first.
2. **Compatibility Doctor** — read-only detection of documented U1 3MF errors;
   biggest beginner-confidence win; spec already in docs.
3. **Model Discovery Hub v1 — read/search/link-out** (Thingiverse +
   MyMiniFactory + Cults3D metadata, link-out tiles for the rest). No import.
4. **Import step** — Thingiverse free/licensed, then MyMiniFactory free via OAuth;
   auto-run Project Doctor on import.
5. **Scale Doctor / code signing** — parallel/later; signing gated on cert
   procurement.

## Exact implementation prompt (if approved) — v1 read/search/link-out only

> SNAPMAKER STUDIO — MODEL DISCOVERY HUB v1 (search + link-out, no import)
>
> Implement the Model Discovery Hub v1 per docs/design/MODEL_DISCOVERY_HUB.md.
> Scope: metadata search + link-out only. No import/download in this step.
>
> Do not scrape. Do not download or commit any third-party model files. Do not
> embed API secrets in the client. Use only sanctioned APIs: Thingiverse,
> MyMiniFactory, Cults3D. Printables/Thangs/MakerWorld are link-out tiles only.
> Do not change the 3MF writer. Do not start Scale/Compatibility Doctor.
>
> Backend: add `POST /model_search { query, filters }` returning
> `ModelSearchResult[]` (schema in the design doc); server-side keys; provider
> adapters behind a strict whitelist; cache + rate-limit backoff. No
> `/model_import` yet (stub `import_allowed`/`reason_import_not_allowed` only).
> Ship adapter unit tests against recorded fixtures (no live network in CI).
>
> Frontend: add "Find Models" sidebar entry + `/find-models` route; search bar;
> filters (free only, commercial-use, STL/3MF, multi-color, source); result cards
> (thumbnail when allowed, title, source, license/price, "Open on source site",
> and a disabled "Import to Studio" with the not-allowed reason); persistent
> disclaimer. Pure-logic tests for filters + link-out URL building + import-gating.
>
> Run frontend vitest + tsc + build; backend pytest. Do not tag/release. Report
> files changed, tests, and what remains for the import step.
