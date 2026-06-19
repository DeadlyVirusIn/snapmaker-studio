import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Printer, Loader2, RotateCw, Thermometer, AlertTriangle, CheckCircle2 } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { printerDiscover, printerStatus } from "@/api";

// Read-only U1 Printer Hub (spike): discover + live status over open Moonraker.
// No upload, no print control — monitoring only.
export default function Printers() {
  const [host, setHost] = useState("U1.local");
  const [connected, setConnected] = useState<string | null>(null);

  const discover = useQuery({ queryKey: ["discover"], queryFn: () => printerDiscover(), enabled: false });
  const status = useQuery({
    queryKey: ["printer-status", connected],
    queryFn: () => printerStatus(connected as string),
    enabled: !!connected,
    refetchInterval: connected ? 3000 : false,  // live, read-only polling
  });

  return (
    <div className="max-w-2xl space-y-5">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-muted text-muted-foreground"><Printer className="h-5 w-5" /></div>
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Printers</h2>
          <p className="text-sm text-muted-foreground">Find your Snapmaker U1 on the network and watch it print. Monitoring only.</p>
        </div>
      </div>

      <Card>
        <CardContent className="space-y-3 p-5">
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex h-9 min-w-[200px] flex-1 items-center gap-2 rounded-md border border-border bg-card px-3">
              <Printer className="h-4 w-4 text-muted-foreground" />
              <input value={host} onChange={(e) => setHost(e.target.value)} placeholder="U1.local"
                className="w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground" />
            </div>
            <Button onClick={() => setConnected(host.trim())} disabled={!host.trim()}>Connect</Button>
            <Button variant="secondary" onClick={() => discover.refetch()} disabled={discover.isFetching}>
              {discover.isFetching ? <Loader2 className="h-4 w-4 animate-spin" /> : <RotateCw className="h-4 w-4" />} Scan
            </Button>
          </div>
          {discover.data && (
            <ul className="text-sm">
              {discover.data.map((p) => (
                <li key={p.host} className="flex items-center gap-2 py-1">
                  {p.reachable ? <CheckCircle2 className="h-4 w-4 text-ready" /> : <AlertTriangle className="h-4 w-4 text-muted-foreground" />}
                  <button className="underline-offset-2 hover:underline" onClick={() => { setHost(p.host); setConnected(p.host); }}>{p.host}</button>
                  <span className="text-xs text-muted-foreground">{p.reachable ? `ready (${p.klippy_state ?? "?"})` : "not found"}</span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      {connected && (
        <Card>
          <CardContent className="space-y-3 p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">{connected}</span>
              {status.isFetching && <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />}
            </div>
            {status.status === "error" && (
              <p className="flex items-center gap-2 text-sm text-muted-foreground"><AlertTriangle className="h-4 w-4" /> Couldn’t reach this printer. Check it’s on the same network.</p>
            )}
            {status.data && (
              <>
                <div className="flex items-center gap-2 text-sm">
                  <span className="rounded-full bg-muted px-2 py-0.5 text-xs font-medium uppercase tracking-wide">{status.data.print_state ?? "idle"}</span>
                  {status.data.filename && <span className="truncate text-muted-foreground">{status.data.filename}</span>}
                  {status.data.progress != null && <span className="ml-auto text-muted-foreground">{Math.round(status.data.progress * 100)}%</span>}
                </div>
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
