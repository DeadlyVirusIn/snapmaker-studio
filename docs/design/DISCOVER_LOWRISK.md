# Discover — Low-Risk Redesign (no scraping, no TOS violations)

**Date:** 2026-06-18 · **Status:** design only (no implementation)

Re-evaluates the "Discover" concept from `PLATFORM_EXPANSION.md` under hard constraints:
**no scraping · no TOS violations · no content hosting · no reverse-engineered private APIs.**
Goal unchanged: move a project from **MakerWorld / Printables / Thingiverse / Cults3D** into
Snapmaker Studio in the **fewest clicks** — but only via mechanisms we're allowed to use.

## Guiding principle
We never fetch what a site doesn't openly let us fetch. The **user's browser already has
permission** to download the file (they're logged in, they accepted the license). So the safest,
fastest path is: **let the user's own download flow do the network part; Studio handles the file
the moment it lands.** Studio becomes the *destination*, not a crawler.

---

## The 7 options — risk / effort / UX / Fund value

Effort S/M/L. Legal risk Low/Med/High.

| # | Option | Legal risk | Effort | UX (clicks) | Fund value |
|---|---|---|---|---|---|
| 1 | **Import from URL** (paste a model page link) | **Med–High** | M–L | 1 paste | High but risky |
| 2 | **Open downloaded project** (watch Downloads / drag-drop) | **Low** | S | 0–1 | High |
| 3 | **Metadata extraction** (read what's inside the file) | **Low** | S–M | 0 | High |
| 4 | **Attribution preservation** (keep creator + source) | **Low** | S | 0 | Med–High |
| 5 | **License preservation** (keep + show the license) | **Low** | S | 0 | Med–High |
| 6 | **Browser-extension** ("Send to Snapmaker Studio") | **Low–Med** | M–L | 1 click | Very High |
| 7 | **Official API integrations only** (Thingiverse, Printables) | **Low** | M | 1–2 | Med |

### 1. Import from URL
- A pasted model-page URL still requires Studio to *fetch* the file. For sites without an open
  download endpoint, that means scraping or hitting private APIs → **the thing we're avoiding.**
- **Keep only** the narrow, safe form: accept a **direct file URL the user already has** (e.g. a
  signed download link), not a model-page URL we'd have to crawl. Low value as a headline feature.
- **Verdict:** de-prioritize; do not build page-URL fetching.

### 2. Open downloaded project  ★ (the core move)
- The user downloads normally (their browser, their session, their accepted license). Studio:
  - **Drag-and-drop** the downloaded file (already works for files), **and**
  - optional **"Watch my Downloads folder"** → when a `.3mf`/`.stl` lands, show a toast:
    "New design detected — open in Studio?"
- **Legal:** Low — we touch only files the user already has on disk. No fetching.
- **UX:** ~0 clicks (toast) to 1 (drag). Fewest clicks of any compliant option.
- **Verdict:** **MVP centerpiece.**

### 3. Metadata extraction
- Read what's embedded in the downloaded file: title, creator, source app, license hints,
  colors, parts. (Bambu/Orca 3MF already carry much of this; the engine parses it.)
- Some marketplaces embed source URL / designer in the 3MF metadata; surface it when present.
- **Legal:** Low — reading a file the user owns. **Verdict:** ship with MVP (feeds Design Insights).

### 4. Attribution preservation
- When the file (or an accompanying sidecar/readme) names a creator/source, **carry it through**
  the conversion into the output and show it in the UI ("From: <creator> on <site>").
- Never strip attribution; never claim authorship. **Legal:** Low (it's pro-creator).
- **Verdict:** ship with MVP — strong ethical + Fund story.

### 5. License preservation
- Detect + retain any license info (CC variant, etc.) found in metadata/readme; display it and
  keep it in the output. Warn if a license is **No-Derivatives** before transforming.
- **Legal:** Low and *risk-reducing* (helps users respect licenses). **Verdict:** ship with MVP.

### 6. Browser extension — "Send to Snapmaker Studio"
- A small extension adds a button on a model page that **uses the site's own download**, then
  hands the downloaded file to Studio via a local handoff (native-messaging or a `snapstudio://`
  deep link). The extension triggers the normal download — it does **not** scrape or call private
  APIs.
- **Legal:** Low–Med (must follow each store's extension policy; no DOM scraping of gated content).
- **UX:** 1 click from the model page → lands in Studio. **Highest "wow," fewest clicks.**
- **Verdict:** **Phase 2** — the differentiator, after the file-handoff core is proven.

### 7. Official API integrations only
- **Thingiverse** and **Printables** have public APIs (keys, within TOS) for search/metadata and,
  where permitted, user-authorized downloads. **MakerWorld / Cults3D:** no compliant public API →
  **out of scope** until they offer one.
- **Legal:** Low (within published TOS + per-model license). **Effort:** M (auth, rate limits).
- **Verdict:** **Phase 3**, opt-in, and only the two sites with real APIs. Be honest that
  MakerWorld/Cults are "download-then-open" only.

---

## Revised architecture (design only)

A single **ingestion pipeline**; all sources feed the same downstream (Insights → Readiness →
Get-it-ready). No source-specific scraping.

```
            ┌─────────────── INGEST (any of) ───────────────┐
 drag/drop ─┤ watch Downloads → file path                    │
 extension ─┤ site's own download → handoff (deep link/NM)   │ → ImportedFile{path, source?, creator?, license?}
 direct URL ┤ user-supplied direct file link (optional)      │
 API (opt) ─┤ Thingiverse/Printables official API (Phase 3)  │
            └────────────────────────────────────────────────┘
                                  │
              metadata + attribution + license extraction
                                  │
                Design Insights → Readiness → Get it ready
                                  │
                 Library row (+ source_url, creator, license)
```

- **Engine:** `ingest.py` → `ImportedFile` (path + optional source/creator/license). `intelligence.py`
  reads embedded metadata; never network unless an explicit, compliant API path is chosen.
- **Library v2:** add `source_url`, `creator`, `license` columns (preserve + display).
- **Desktop:** optional Downloads-folder watcher (off by default, user opt-in) + a deep-link handler
  (`snapstudio://open?file=…`) for the extension.
- **Extension (separate repo):** triggers the site's normal download, then opens the result in
  Studio via the deep link / native messaging. No content scraping.

**What we explicitly do NOT build:** model-page scrapers, private/reverse-engineered API clients,
any re-hosting of models, any bypass of a site's auth or paywall.

---

## Recommended roadmap

- **v0.4 (with the product proposal):**
  - **Open downloaded project** (drag-drop is done; add opt-in Downloads watcher).
  - **Metadata + attribution + license** extraction → shown in Design Insights, preserved in output.
- **v0.5 "Discover":**
  - **Browser extension** "Send to Snapmaker Studio" (1-click handoff via the site's own download).
  - **Official APIs** (Thingiverse, Printables) — opt-in search/import within TOS.
- **Not planned:** MakerWorld/Cults integrations until they publish a compliant public API.

## Best MVP approach (fewest clicks, lowest risk)
**"It's already here."** Opt-in **Downloads-folder watcher** + **metadata/attribution/license**
extraction. The user downloads from any site as they normally do; Studio notices the new design,
shows what it is and where it's from, and offers one tap to get it ready. **Zero new legal surface,
~0–1 clicks, works for all four sites today** (because Studio never touches the site).

## Estimated effort
| Item | Effort |
|---|---|
| Downloads watcher (opt-in) + "new design" toast | ~0.5–1 wk |
| Metadata + attribution + license extraction + UI | ~1–1.5 wk |
| Library v2 columns (source/creator/license) | ~0.5 wk |
| **MVP subtotal** | **~2–3 wk** |
| Browser extension (handoff) | ~2–3 wk (separate, v0.5) |
| Official API integrations (Thingiverse + Printables) | ~2–3 wk (v0.5) |

## Innovation Fund value
Reframes Discover from a legally risky crawler into a **respectful, creator-friendly ingestion
story**: "bring a design from anywhere, keep the creator's name and license, and get it printing."
That's fundable (accessibility + interoperability + ethics) and **defensible** — no TOS exposure,
no hosting liability, fully local-first.

> Design only — no code. Approval gate before any ingestion work; the browser extension and
> official-API pieces each get their own legal check before build.
