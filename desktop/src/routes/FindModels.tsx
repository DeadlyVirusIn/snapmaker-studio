import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Search, ExternalLink, Loader2, Lock, Info, Compass } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import { modelSearch } from "@/api";
import {
  filterResults, linkOutUrl, importReasonLabel, DISCLAIMER, LINK_OUT_PROVIDERS,
  SANCTIONED_SOURCES, type SearchFilters, type SearchResponse, type ModelSource,
} from "@/lib/modelSearch";

const FORMATS = ["STL", "3MF"];

export default function FindModels() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<SearchFilters>({});
  const [resp, setResp] = useState<SearchResponse | null>(null);

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
        subtitle="Search 3D model sites, check the license, then diagnose for your U1." />

      {/* search */}
      <Card><CardContent className="space-y-3 p-5">
        <div className="flex gap-2">
          <input
            value={query} onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && query.trim()) searchM.mutate(); }}
            placeholder="Search for a model…"
            className="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
          />
          <Button size="sm" onClick={() => searchM.mutate()} disabled={!query.trim() || searchM.isPending}>
            {searchM.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />} Search
          </Button>
        </div>
        {/* filters */}
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

      {/* warnings (e.g. provider disabled — no API key) */}
      {resp && resp.warnings.length > 0 && (
        <div className="rounded-md border border-border p-3 text-xs text-muted-foreground">
          {resp.warnings.map((w, i) => (
            <p key={i} className="flex items-start gap-1.5"><Info className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {w}</p>
          ))}
        </div>
      )}

      {/* results */}
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
      {resp && shown.length === 0 && (
        <div className="rounded-md border border-border p-3 text-sm">
          <p className="font-medium">Connect provider API keys to enable live search</p>
          <p className="mt-1 text-muted-foreground">
            Live metadata search uses each provider's official API (Thingiverse,
            MyMiniFactory, Cults3D) and needs an API key configured server-side.
            Until then, use the link-out sites below to search on the source site.
          </p>
        </div>
      )}

      {/* link-out tiles */}
      <Card><CardContent className="space-y-2 p-5">
        <p className="text-sm font-semibold">Search on other sites (link-out only)</p>
        <p className="text-xs text-muted-foreground">
          Printables, Thangs and MakerWorld open in their own search — Studio does not
          fetch, scrape, mirror or re-host their results.
        </p>
        <div className="flex flex-wrap gap-2 pt-1">
          {LINK_OUT_PROVIDERS.map((p) => (
            <Button key={p.id} size="sm" variant="secondary" asChild disabled={!query.trim()}>
              <a href={query.trim() ? linkOutUrl(p.id, query) : undefined} target="_blank" rel="noreferrer">
                <ExternalLink className="h-4 w-4" /> {p.label}
              </a>
            </Button>
          ))}
        </div>
      </CardContent></Card>

      <div className="rounded-md bg-muted/40 p-3 text-xs text-muted-foreground">
        <p>API keys are stored locally and used server-side — they never ship in the app bundle.
           Studio does not mirror or re-host models. Downloads/imports are not available yet
           (v1 is search + link-out). {DISCLAIMER}</p>
      </div>
    </div>
  );
}
