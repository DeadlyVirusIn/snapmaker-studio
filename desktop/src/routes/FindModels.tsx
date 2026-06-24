import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Search, ExternalLink, Loader2, Lock, Info, Compass, FolderOpen, Stethoscope, X, RotateCw,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import { modelSearch, openModelBrowser, closeModelBrowser } from "@/api";
import { useMode } from "@/store/mode";
import { useOpenFile } from "@/hooks/useOpenFile";
import { MODEL_BROWSER_COPY, closedPanel, panelLabel, showPanel, type BrowserPanelState } from "@/lib/modelBrowser";
import {
  filterResults, linkOutUrl, importReasonLabel, DISCLAIMER, BROWSE_PROVIDERS,
  SANCTIONED_SOURCES, type SearchFilters, type SearchResponse, type ModelSource,
} from "@/lib/modelSearch";

const FORMATS = ["STL", "3MF"];

// Model Browser direction: novices browse approved 3D model sites in the browser,
// download an STL/3MF from the site, then open it in Studio. No API keys, no
// scraping, no import claims. Live in-app API search is an Advanced-only extra.
export default function FindModels() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<SearchFilters>({});
  const [resp, setResp] = useState<SearchResponse | null>(null);
  const advanced = useMode((s) => s.mode) === "advanced";
  const openFile = useOpenFile();
  const [browser, setBrowser] = useState<BrowserPanelState>(closedPanel);

  const providerLabel = (siteId: string) =>
    BROWSE_PROVIDERS.find((p) => p.id === siteId)?.label ?? siteId;

  // Open an approved site inside Studio's locked Model Browser. The remote page is
  // isolated (no IPC); the trusted control panel below reflects and controls it.
  async function browse(siteId: string) {
    const url = linkOutUrl(siteId, query);
    try {
      await openModelBrowser(url);
      setBrowser({ open: true, site: providerLabel(siteId) });
    } catch {
      // Not in the desktop app (e.g. dev in a browser) — fall back to a normal tab.
      window.open(url, "_blank", "noreferrer");
    }
  }

  async function closeBrowser() {
    try { await closeModelBrowser(); } catch { /* not in the desktop app */ }
    setBrowser(closedPanel);
  }

  const searchM = useMutation({
    mutationFn: () => modelSearch(query, { sources: filters.sources }),
    onSuccess: (d) => setResp(d),
  });

  function toggleSource(s: ModelSource) {
    setFilters((f) => {
      const cur = new Set(f.sources ?? []);
      if (cur.has(s)) cur.delete(s); else cur.add(s);
      return { ...f, sources: [...cur] };
    });
  }
  function toggleFormat(fmt: string) {
    setFilters((f) => {
      const cur = new Set(f.formats ?? []);
      if (cur.has(fmt)) cur.delete(fmt); else cur.add(fmt);
      return { ...f, formats: [...cur] };
    });
  }

  const shown = resp ? filterResults(resp.results, filters) : [];
  const chip = (on: boolean) =>
    `rounded-md border px-2.5 py-1 text-xs ${on ? "border-foreground text-foreground" : "border-border text-muted-foreground"}`;

  return (
    <div className="space-y-6">
      <PageHeader icon={Compass} title="Find Models"
        subtitle="Browse trusted 3D model sites, download the STL or 3MF from the site, then open it in Studio to check it for your U1." />

      {/* term box — powers the browse links (and, in Advanced, live API search) */}
      <Card><CardContent className="space-y-2 p-5">
        <p className="text-sm font-medium">What are you looking for?</p>
        <div className="flex gap-2">
          <input
            value={query} onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. desk organizer, U1 calibration cube…"
            className="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
          />
          {advanced && (
            <Button size="sm" variant="secondary" onClick={() => searchM.mutate()} disabled={!query.trim() || searchM.isPending}>
              {searchM.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />} Search in-app
            </Button>
          )}
        </div>
        <p className="text-xs text-muted-foreground">Type a term, then pick a site below to browse it there.</p>
      </CardContent></Card>

      {/* PRIMARY: browse approved model sites */}
      <Card><CardContent className="space-y-2 p-5">
        <p className="text-sm font-semibold">Browse trusted model sites</p>
        <p className="text-xs text-muted-foreground">
          Opens inside Studio's Model Browser (approved sites only). Download the STL
          or 3MF there, then open it in Studio below — Studio never scrapes, imports,
          or bypasses a site's login or terms.
        </p>
        <div className="flex flex-wrap gap-2 pt-1">
          {BROWSE_PROVIDERS.map((p) => (
            <Button key={p.id} size="sm" variant="secondary" onClick={() => browse(p.id)}>
              <ExternalLink className="h-4 w-4" /> {p.label}
            </Button>
          ))}
        </div>
      </CardContent></Card>

      {/* TRUSTED control panel for the locked Model Browser window — Studio-side
          only; the remote page never gets any of these controls or any IPC. */}
      {showPanel(browser) && (
        <Card><CardContent className="space-y-3 p-5">
          <p className="flex items-center gap-2 text-sm font-semibold">
            <Compass className="h-4 w-4 text-primary" /> {panelLabel(browser)}
          </p>
          <p className="text-xs text-muted-foreground">{MODEL_BROWSER_COPY.flow}</p>
          <div className="flex flex-wrap gap-2">
            <Button size="sm" onClick={openFile}><FolderOpen className="h-4 w-4" /> Open downloaded file</Button>
            <Button size="sm" variant="secondary" asChild>
              <Link to="/doctor/project"><Stethoscope className="h-4 w-4" /> Run Project Doctor</Link>
            </Button>
            <Button size="sm" variant="secondary" onClick={closeBrowser}><X className="h-4 w-4" /> Close Model Browser</Button>
          </div>
          <div className="flex flex-wrap items-center gap-1.5">
            <span className="text-[11px] text-muted-foreground">Reopen / choose another site:</span>
            {BROWSE_PROVIDERS.map((p) => (
              <Button key={p.id} size="sm" variant="secondary" onClick={() => browse(p.id)}>
                <RotateCw className="h-3.5 w-3.5" /> {p.label}
              </Button>
            ))}
          </div>
          <p className="flex items-start gap-1.5 text-[11px] text-muted-foreground">
            <Lock className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {MODEL_BROWSER_COPY.trust}
          </p>
        </CardContent></Card>
      )}

      {/* PRIMARY: bring a downloaded file into Studio */}
      <Card><CardContent className="space-y-2 p-5">
        <p className="text-sm font-semibold">Got a downloaded file?</p>
        <p className="text-xs text-muted-foreground">Open the STL or 3MF you downloaded and Studio checks it for your U1.</p>
        <div className="flex flex-wrap gap-2 pt-1">
          <Button size="sm" onClick={openFile}>
            <FolderOpen className="h-4 w-4" /> Open downloaded file
          </Button>
          <Button size="sm" variant="secondary" asChild>
            <Link to="/doctor/project"><Stethoscope className="h-4 w-4" /> Check in Project Doctor</Link>
          </Button>
        </div>
      </CardContent></Card>

      {/* ADVANCED ONLY: optional live API search (filters, results, import) */}
      {advanced && (
        <>
          <Card><CardContent className="space-y-3 p-5">
            <p className="text-sm font-medium">Advanced: live in-app search</p>
            <p className="text-xs text-muted-foreground">
              Optional. Live metadata search uses each provider's official API and
              needs a key configured outside the app; most users just browse above.
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
                  {!r.import_allowed && (
                    <p className="text-[11px] text-muted-foreground">{importReasonLabel(r.reason_import_not_allowed)}</p>
                  )}
                </CardContent></Card>
              ))}
            </div>
          )}
        </>
      )}

      <div className="rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
        <p>Studio opens these sites in an approved-sites-only Model Browser window — it
           doesn't fetch, scrape, mirror, or re-host their models, and doesn't bypass any
           login or paywall. Navigation off the approved sites is blocked. Downloads and
           one-click import are not available; download from the site, then open the file
           in Studio. {DISCLAIMER}</p>
      </div>
    </div>
  );
}
