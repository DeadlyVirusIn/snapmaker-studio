import { useState, useRef, useEffect, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Search, ExternalLink, Loader2, Lock, Info, Compass, FolderOpen, Stethoscope, X, RotateCw,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import {
  modelSearch, openEmbeddedBrowser, setEmbeddedBounds, closeEmbeddedBrowser,
} from "@/api";
import { useMode } from "@/store/mode";
import { useOpenFile } from "@/hooks/useOpenFile";
import { MODEL_BROWSER_COPY } from "@/lib/modelBrowser";
import {
  filterResults, linkOutUrl, importReasonLabel, DISCLAIMER, BROWSE_PROVIDERS,
  SANCTIONED_SOURCES, type SearchFilters, type SearchResponse, type ModelSource,
} from "@/lib/modelSearch";

const FORMATS = ["STL", "3MF"];

// Model Browser: novices browse approved 3D-model sites INSIDE Studio — the site
// renders in an embedded child webview placed below the trusted Studio toolbar.
// No API keys, no scraping, no import claims; the remote page gets no IPC.
export default function FindModels() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<SearchFilters>({});
  const [resp, setResp] = useState<SearchResponse | null>(null);
  const advanced = useMode((s) => s.mode) === "advanced";
  const openFile = useOpenFile();

  // The site currently embedded in-app (null = chooser view).
  const [site, setSite] = useState<{ id: string; label: string } | null>(null);
  const viewportRef = useRef<HTMLDivElement | null>(null);

  const providerLabel = (id: string) => BROWSE_PROVIDERS.find((p) => p.id === id)?.label ?? id;

  // Reserved rect for the native webview, in window-logical (= CSS viewport) px.
  const rect = useCallback(() => {
    const el = viewportRef.current;
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { x: r.left, y: r.top, width: r.width, height: r.height };
  }, []);

  // Open (or switch) the embedded approved-site webview under the toolbar.
  async function browse(id: string) {
    const url = linkOutUrl(id, query);
    setSite({ id, label: providerLabel(id) });
    // Wait a frame so the placeholder is laid out, then position the webview.
    requestAnimationFrame(async () => {
      const r = rect();
      if (!r) return;
      try {
        await openEmbeddedBrowser(url, r.x, r.y, r.width, r.height);
      } catch {
        // Not in the desktop app (e.g. dev in a plain browser) — fall back to a tab.
        setSite(null);
        window.open(url, "_blank", "noreferrer");
      }
    });
  }

  function closeBrowser() {
    closeEmbeddedBrowser().catch(() => { /* not in desktop */ });
    setSite(null);
  }

  // Keep the native webview aligned to the placeholder on resize/scroll, and
  // always tear it down when leaving Find Models (it's a native overlay, not DOM).
  useEffect(() => {
    if (!site) return;
    const sync = () => { const r = rect(); if (r) setEmbeddedBounds(r.x, r.y, r.width, r.height).catch(() => {}); };
    window.addEventListener("resize", sync);
    window.addEventListener("scroll", sync, true);
    const id = window.setInterval(sync, 500); // catch sidebar/layout shifts
    return () => {
      window.removeEventListener("resize", sync);
      window.removeEventListener("scroll", sync, true);
      window.clearInterval(id);
    };
  }, [site, rect]);

  useEffect(() => () => { closeEmbeddedBrowser().catch(() => {}); }, []);

  const searchM = useMutation({
    mutationFn: () => modelSearch(query, { sources: filters.sources }),
    onSuccess: (d) => setResp(d),
  });
  function toggleSource(s: ModelSource) {
    setFilters((f) => { const c = new Set(f.sources ?? []); c.has(s) ? c.delete(s) : c.add(s); return { ...f, sources: [...c] }; });
  }
  function toggleFormat(fmt: string) {
    setFilters((f) => { const c = new Set(f.formats ?? []); c.has(fmt) ? c.delete(fmt) : c.add(fmt); return { ...f, formats: [...c] }; });
  }
  const shown = resp ? filterResults(resp.results, filters) : [];
  const chip = (on: boolean) => `rounded-md border px-2.5 py-1 text-xs ${on ? "border-foreground text-foreground" : "border-border text-muted-foreground"}`;

  // ---- Embedded browser workspace: toolbar + big website viewport -------------
  if (site) {
    return (
      <div className="flex h-[calc(100vh-9rem)] flex-col gap-3">
        <Card className="shrink-0"><CardContent className="space-y-2 p-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex items-center gap-1.5 text-sm font-semibold">
              <Compass className="h-4 w-4 text-primary" /> Browsing {site.label} inside Studio
            </span>
            <div className="ml-auto flex flex-wrap items-center gap-1.5">
              <Button size="sm" onClick={openFile}><FolderOpen className="h-4 w-4" /> Open downloaded file</Button>
              <Button size="sm" variant="secondary" asChild><Link to="/doctor/project"><Stethoscope className="h-4 w-4" /> Run Project Doctor</Link></Button>
              <Button size="sm" variant="secondary" onClick={closeBrowser}><X className="h-4 w-4" /> Close browser</Button>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] text-muted-foreground">Approved sites:</span>
            {BROWSE_PROVIDERS.map((p) => (
              <button key={p.id} onClick={() => browse(p.id)}
                className={`flex items-center gap-1 rounded border px-2 py-0.5 text-xs ${site.id === p.id ? "border-foreground text-foreground" : "border-border text-muted-foreground"}`}>
                {site.id === p.id ? <RotateCw className="h-3 w-3" /> : <ExternalLink className="h-3 w-3" />} {p.label}
              </button>
            ))}
          </div>
          <p className="flex items-start gap-1.5 text-[11px] text-muted-foreground">
            <Lock className="mt-0.5 h-3 w-3 shrink-0" /> {MODEL_BROWSER_COPY.trust} Download from the site, then Open downloaded file → Project Doctor.
          </p>
        </CardContent></Card>

        {/* The native approved-site webview is positioned over this region. */}
        <div ref={viewportRef} className="relative flex-1 overflow-hidden rounded-lg border border-border bg-muted/20">
          <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
            <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Loading {site.label} inside Studio…
          </div>
        </div>
      </div>
    );
  }

  // ---- Chooser view ----------------------------------------------------------
  return (
    <div className="space-y-6">
      <PageHeader icon={Compass} title="Find Models"
        subtitle="Browse approved model sites inside Studio. Download from the site, then open the STL or 3MF here and run Project Doctor." />

      <Card><CardContent className="space-y-2 p-5">
        <p className="text-sm font-medium">What are you looking for?</p>
        <div className="flex gap-2">
          <input value={query} onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. desk organizer, U1 calibration cube…"
            className="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary" />
          {advanced && (
            <Button size="sm" variant="secondary" onClick={() => searchM.mutate()} disabled={!query.trim() || searchM.isPending}>
              {searchM.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />} Search in-app
            </Button>
          )}
        </div>
        <p className="text-xs text-muted-foreground">Type a term, then pick a site below to browse it inside Studio.</p>
      </CardContent></Card>

      <Card><CardContent className="space-y-2 p-5">
        <p className="text-sm font-semibold">Browse trusted model sites — inside Studio</p>
        <p className="text-xs text-muted-foreground">{MODEL_BROWSER_COPY.flow}</p>
        <div className="flex flex-wrap gap-2 pt-1">
          {BROWSE_PROVIDERS.map((p) => (
            <Button key={p.id} size="sm" onClick={() => browse(p.id)}>
              <Compass className="h-4 w-4" /> {p.label}
            </Button>
          ))}
        </div>
        <p className="flex items-start gap-1.5 pt-1 text-[11px] text-muted-foreground">
          <Lock className="mt-0.5 h-3 w-3 shrink-0" /> {MODEL_BROWSER_COPY.trust}
        </p>
      </CardContent></Card>

      <Card><CardContent className="space-y-2 p-5">
        <p className="text-sm font-semibold">Got a downloaded file?</p>
        <p className="text-xs text-muted-foreground">Open the STL or 3MF you downloaded and Studio checks it for your U1.</p>
        <div className="flex flex-wrap gap-2 pt-1">
          <Button size="sm" onClick={openFile}><FolderOpen className="h-4 w-4" /> Open downloaded file</Button>
          <Button size="sm" variant="secondary" asChild><Link to="/doctor/project"><Stethoscope className="h-4 w-4" /> Check in Project Doctor</Link></Button>
        </div>
      </CardContent></Card>

      {advanced && (
        <>
          <Card><CardContent className="space-y-3 p-5">
            <p className="text-sm font-medium">Advanced: live in-app search</p>
            <p className="text-xs text-muted-foreground">
              Optional. Live metadata search uses each provider's official API and needs a key
              configured outside the app; most users just browse above.
            </p>
            <div className="flex flex-wrap items-center gap-1.5">
              <button className={chip(!!filters.freeOnly)} onClick={() => setFilters((f) => ({ ...f, freeOnly: !f.freeOnly }))}>Free only</button>
              <button className={chip(!!filters.commercialUse)} onClick={() => setFilters((f) => ({ ...f, commercialUse: !f.commercialUse }))}>Commercial-use</button>
              <button className={chip(!!filters.multiColor)} onClick={() => setFilters((f) => ({ ...f, multiColor: !f.multiColor }))}>Multi-color</button>
              {FORMATS.map((fmt) => (
                <button key={fmt} className={chip((filters.formats ?? []).includes(fmt))} onClick={() => toggleFormat(fmt)}>{fmt}</button>
              ))}
              <span className="mx-1 text-[11px] text-muted-foreground">source:</span>
              {SANCTIONED_SOURCES.map((s) => (
                <button key={s} className={chip((filters.sources ?? []).includes(s))} onClick={() => toggleSource(s)}>{s}</button>
              ))}
            </div>
          </CardContent></Card>

          {resp && resp.warnings.length > 0 && (
            <div className="rounded-md border border-border p-3 text-xs text-muted-foreground">
              {resp.warnings.map((w, i) => (
                <p key={i} className="flex items-start gap-1.5"><Info className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {w}</p>
              ))}
            </div>
          )}

          {resp && shown.length > 0 && (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {shown.map((r, i) => (
                <Card key={`${r.source}-${i}`}><CardContent className="space-y-2 p-4">
                  {r.thumbnail_url && <img src={r.thumbnail_url} alt="" className="h-28 w-full rounded object-cover" />}
                  <p className="truncate text-sm font-medium" title={r.title}>{r.title}</p>
                  <p className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{r.source}</span>
                    <span>{r.price_status ?? "unknown"}{r.license ? ` · ${r.license}` : ""}</span>
                  </p>
                  {r.attribution && <p className="text-[11px] text-muted-foreground">by {r.attribution}</p>}
                  <div className="flex items-center gap-2 pt-1">
                    <Button size="sm" variant="secondary" asChild>
                      <a href={r.source_url} target="_blank" rel="noreferrer"><ExternalLink className="h-4 w-4" /> Open on source site</a>
                    </Button>
                    <Button size="sm" disabled title={importReasonLabel(r.reason_import_not_allowed)}>
                      <Lock className="h-4 w-4" /> Import to Studio
                    </Button>
                  </div>
                  {!r.import_allowed && <p className="text-[11px] text-muted-foreground">{importReasonLabel(r.reason_import_not_allowed)}</p>}
                </CardContent></Card>
              ))}
            </div>
          )}
        </>
      )}

      <div className="rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
        <p>Studio opens these sites in an approved-sites-only embedded browser — it doesn't
           fetch, scrape, mirror, or re-host their models, and doesn't bypass any login or
           paywall. Navigation off the approved sites is blocked. Downloads and one-click
           import are not available; download from the site, then open the file in Studio. {DISCLAIMER}</p>
      </div>
    </div>
  );
}
