import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Printer, Loader2, RotateCw, Thermometer, AlertTriangle, CheckCircle2,
  ShieldCheck, Wifi, Activity,
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/layout";
import { printerDiscover, printerStatus } from "@/api";
import { usePrinter } from "@/store/printer";

// Read-only U1 Printer Hub: discover + live status over the U1's open Moonraker.
// No upload, no print control — monitoring only.
export default function Printers() {
  const savedHost = usePrinter((s) => s.host);
  const setSavedHost = usePrinter((s) => s.setHost);
  const [host, setHost] = useState(savedHost);
  const [connected, setConnected] = useState<string | null>(null);

  const connect = (h: string) => { const v = h.trim(); if (!v) return; setSavedHost(v); setConnected(v); };

  const discover = useQuery({ queryKey: ["discover"], queryFn: () => printerDiscover(), enabled: false });
  const status = useQuery({
    queryKey: ["printer-status", connected],
    queryFn: () => printerStatus(connected as string),
    enabled: !!connected,
    refetchInterval: connected ? 3000 : false,  // live, read-only polling
  });
  const state = status.data?.print_state;
  const isPrinting = state === "printing";

  return (
    <div className="mx-auto max-w-2xl space-y-5">
      <PageHeader
        icon={Printer}
        title="Printer Hub"
        subtitle="See your Snapmaker U1’s live status — temperatures, progress, and what it’s printing — right next to your designs."
        badge={
          <span className="inline-flex items-center gap-1 rounded-full border border-ready/40 bg-ready/10 px-2 py-0.5 text-xs font-medium text-ready">
            <ShieldCheck className="h-3.5 w-3.5" /> Read-only
          </span>
        }
      />

      <Card>
        <CardContent className="space-y-3 p-5">
          <p className="text-sm font-medium">Connect to your U1</p>
          <p className="text-xs text-muted-foreground">
            Your U1 shows up on your home network as <code className="rounded bg-muted px-1">U1.local</code>. Enter that (or its IP address) and connect — Studio only reads status, it never changes your printer.
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex h-9 min-w-[200px] flex-1 items-center gap-2 rounded-md border border-border bg-card px-3">
              <Wifi className="h-4 w-4 text-muted-foreground" />
              <input value={host} onChange={(e) => setHost(e.target.value)} onKeyDown={(e) => e.key === "Enter" && connect(host)} placeholder="U1.local"
                className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground" />
            </div>
            <Button onClick={() => connect(host)} disabled={!host.trim()}>Connect</Button>
            <Button variant="secondary" onClick={() => discover.refetch()} disabled={discover.isFetching}>
              {discover.isFetching ? <Loader2 className="h-4 w-4 animate-spin" /> : <RotateCw className="h-4 w-4" />} Scan network
            </Button>
          </div>
          {discover.data && (
            <ul className="text-sm">
              {discover.data.map((p) => (
                <li key={p.host} className="flex items-center gap-2 py-1">
                  {p.reachable ? <CheckCircle2 className="h-4 w-4 text-ready" /> : <AlertTriangle className="h-4 w-4 text-muted-foreground" />}
                  <button className="underline-offset-2 hover:underline" onClick={() => { setHost(p.host); connect(p.host); }}>{p.host}</button>
                  <span className="text-xs text-muted-foreground">{p.reachable ? `found — ${p.klippy_state ?? "ready"}` : "no printer here"}</span>
                </li>
              ))}
              {discover.data.every((p) => !p.reachable) && (
                <li className="pt-1 text-xs text-muted-foreground">No U1 found. Make sure it’s powered on and on the same Wi-Fi, then try its IP address.</li>
              )}
            </ul>
          )}
        </CardContent>
      </Card>

      {!connected && !discover.data && (
        <p className="text-center text-xs text-muted-foreground">Tip: leave this open while you print — it refreshes every few seconds.</p>
      )}

      {connected && (
        <Card>
          <CardContent className="space-y-4 p-5">
            <div className="flex items-center justify-between">
              <span className="flex items-center gap-2 text-sm font-semibold"><Activity className="h-4 w-4 text-primary" /> {connected}</span>
              {status.isFetching && <span className="flex items-center gap-1 text-xs text-muted-foreground"><Loader2 className="h-3.5 w-3.5 animate-spin" /> live</span>}
            </div>
            {status.status === "error" && (
              <p className="flex items-center gap-2 text-sm text-muted-foreground"><AlertTriangle className="h-4 w-4" /> Couldn’t reach this printer. Check it’s powered on and on the same network.</p>
            )}
            {status.data && (
              <>
                <div className="flex items-center gap-2 text-sm">
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide ${isPrinting ? "bg-primary/15 text-primary" : "bg-muted text-muted-foreground"}`}>{state ?? "idle"}</span>
                  {status.data.filename && <span className="truncate text-muted-foreground">{status.data.filename}</span>}
                  {status.data.progress != null && <span className="ml-auto font-medium">{Math.round(status.data.progress * 100)}%</span>}
                </div>
                {status.data.progress != null && (
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                    <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${Math.round((status.data.progress ?? 0) * 100)}%` }} />
                  </div>
                )}
                <div className="grid grid-cols-2 gap-2 text-sm sm:grid-cols-3">
                  <div className="rounded-md border border-border p-2"><p className="flex items-center gap-1 text-xs text-muted-foreground"><Thermometer className="h-3 w-3" /> Bed</p><p>{status.data.bed.temperature ?? "—"}° / {status.data.bed.target ?? "—"}°</p></div>
                  {status.data.toolheads.map((t) => (
                    <div key={t.index} className="rounded-md border border-border p-2"><p className="flex items-center gap-1 text-xs text-muted-foreground"><Thermometer className="h-3 w-3" /> Tool {t.index + 1}</p><p>{t.temperature ?? "—"}° / {t.target ?? "—"}°</p></div>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">Live, read-only — Studio never changes your printer.</p>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
