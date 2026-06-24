import { useState } from "react";
import { Play, Pause, X, Upload, OctagonAlert, Loader2, AlertTriangle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  printerPause, printerResume, printerCancel, printerStartPrint, printerEmergencyStop,
  printerUploadGcode, openGcodeDialog,
} from "@/api";
import {
  availableActions, needsConfirm, confirmCopy, type PrintState, type ControlAction,
} from "@/lib/printerControl";

// Printer Hub Phase B — safe, user-controlled actions. Every start / cancel /
// emergency-stop is confirmed in-app before it reaches the printer. Studio does not
// auto-start anything. Pause/resume are reversible and run immediately.
export function PrinterControls({
  host, printState, online, onChanged,
}: {
  host: string | null;
  printState: PrintState;
  online: boolean;
  onChanged: () => void;
}) {
  const [confirm, setConfirm] = useState<{ action: ControlAction; filename?: string } | null>(null);
  const [busy, setBusy] = useState<ControlAction | "upload" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploaded, setUploaded] = useState<string | null>(null); // last gcode uploaded → offer to start

  if (!host) return null;
  const actions = availableActions(printState, online);

  async function call(fn: () => Promise<unknown>, tag: ControlAction | "upload") {
    setError(null); setBusy(tag);
    try { await fn(); onChanged(); }
    catch (e) { setError(e instanceof Error ? e.message : "the printer didn't accept that — check it's on and reachable"); }
    finally { setBusy(null); setConfirm(null); }
  }

  function run(action: ControlAction, filename?: string) {
    if (needsConfirm(action)) { setConfirm({ action, filename }); return; }
    if (action === "pause") return call(() => printerPause(host!), "pause");
    if (action === "resume") return call(() => printerResume(host!), "resume");
  }

  function doConfirmed() {
    if (!confirm) return;
    const { action, filename } = confirm;
    if (action === "cancel") return call(() => printerCancel(host!), "cancel");
    if (action === "emergency_stop") return call(() => printerEmergencyStop(host!), "emergency_stop");
    if (action === "start") return call(() => printerStartPrint(host!, filename ?? ""), "start");
  }

  async function pickAndUpload() {
    const path = await openGcodeDialog();
    if (!path) return;
    setError(null); setBusy("upload");
    try {
      const r = await printerUploadGcode(host!, path);
      setUploaded(r.filename ?? null);
      onChanged();
    } catch (e) {
      setError(e instanceof Error ? e.message : "upload failed — check the printer is reachable");
    } finally { setBusy(null); }
  }

  const spin = (t: ControlAction | "upload") => busy === t ? <Loader2 className="h-4 w-4 animate-spin" /> : null;

  return (
    <Card>
      <CardContent className="space-y-3 p-5">
        <p className="text-sm font-semibold">Printer controls</p>
        {!online ? (
          <p className="flex items-center gap-2 text-xs text-muted-foreground">
            <AlertTriangle className="h-4 w-4" /> Controls are off until the printer is connected and reachable.
          </p>
        ) : (
          <>
            <div className="flex flex-wrap gap-2">
              {actions.includes("pause") && (
                <Button size="sm" variant="secondary" disabled={!!busy} onClick={() => run("pause")}>
                  {spin("pause") ?? <Pause className="h-4 w-4" />} Pause
                </Button>
              )}
              {actions.includes("resume") && (
                <Button size="sm" disabled={!!busy} onClick={() => run("resume")}>
                  {spin("resume") ?? <Play className="h-4 w-4" />} Resume
                </Button>
              )}
              {actions.includes("cancel") && (
                <Button size="sm" variant="danger" disabled={!!busy} onClick={() => run("cancel")}>
                  <X className="h-4 w-4" /> Cancel print
                </Button>
              )}
              {actions.includes("start") && (
                <Button size="sm" variant="secondary" disabled={!!busy} onClick={pickAndUpload}>
                  {spin("upload") ?? <Upload className="h-4 w-4" />} Upload sliced gcode
                </Button>
              )}
            </div>

            {/* Close the loop: after uploading exported gcode, offer to start it (confirmed). */}
            {uploaded && actions.includes("start") && (
              <div className="flex flex-wrap items-center gap-2 rounded-md border border-border p-2 text-xs">
                <span className="text-muted-foreground">Uploaded <span className="font-medium text-foreground">{uploaded}</span>.</span>
                <Button size="sm" disabled={!!busy} onClick={() => run("start", uploaded)}>
                  <Play className="h-4 w-4" /> Start this print
                </Button>
              </div>
            )}

            <p className="flex items-start gap-1.5 text-[11px] text-muted-foreground">
              <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0" />
              Only start a print if the U1 is clear, loaded, and ready. Studio sends the command but does not check the bed for you.
            </p>

            <div className="mt-2 rounded-md border border-risk/40 bg-risk/5 p-2">
              <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-risk">Emergency stop</p>
              <p className="mb-2 text-[11px] text-muted-foreground">
                Halts motion/heaters and may require a firmware restart before printing again.
              </p>
              <Button size="sm" variant="danger" disabled={!!busy} onClick={() => run("emergency_stop")}>
                {spin("emergency_stop") ?? <OctagonAlert className="h-4 w-4" />} Emergency stop
              </Button>
            </div>
          </>
        )}

        {error && (
          <p className="flex items-start gap-1.5 text-xs text-risk">
            <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {error}
          </p>
        )}

        {confirm && (
          <ConfirmDialog
            {...confirmCopy(confirm.action, confirm.filename)}
            busy={!!busy}
            onCancel={() => setConfirm(null)}
            onConfirm={doConfirmed}
          />
        )}
      </CardContent>
    </Card>
  );
}

function ConfirmDialog({
  title, body, danger, busy, onCancel, onConfirm,
}: {
  title: string; body: string; danger: boolean; busy: boolean;
  onCancel: () => void; onConfirm: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-sm rounded-lg border border-border bg-background p-5 shadow-xl">
        <p className={`text-sm font-semibold ${danger ? "text-risk" : ""}`}>{title}</p>
        <p className="mt-2 text-xs text-muted-foreground">{body}</p>
        <div className="mt-4 flex justify-end gap-2">
          <Button size="sm" variant="secondary" disabled={busy} onClick={onCancel}>Cancel</Button>
          <Button size="sm" variant={danger ? "danger" : "primary"} disabled={busy} onClick={onConfirm}>
            {busy && <Loader2 className="h-4 w-4 animate-spin" />} {danger ? "Yes, do it" : "Confirm"}
          </Button>
        </div>
      </div>
    </div>
  );
}
