import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Rocket, Download, Loader2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/store/toast";
import { detectOrca, openInOrca } from "@/api";
import { ORCA_RELEASES_URL, ORCA_HANDOFF_LINE, orcaErrorMessage } from "@/lib/orca";

/**
 * One-way Snapmaker Orca handoff. Shows "Open in Snapmaker Orca" when an install
 * is detected, otherwise "Install Snapmaker Orca" (official releases). Only ever
 * appears when a prepared/safe-copy file exists. Studio never slices and never
 * controls Orca; the install path is never displayed in the UI.
 */
export function OrcaHandoff({ outputPath }: { outputPath: string }) {
  const showToast = useToast((s) => s.show);
  // undefined = still detecting, string = installed, null = not installed
  const [orca, setOrca] = useState<string | null | undefined>(undefined);
  const [opening, setOpening] = useState(false);

  useEffect(() => {
    let alive = true;
    detectOrca().then(
      (p) => { if (alive) setOrca(p); },
      () => { if (alive) setOrca(null); }, // not in Tauri / detection failed -> offer install
    );
    return () => { alive = false; };
  }, []);

  const open = async () => {
    setOpening(true);
    try {
      await openInOrca(outputPath);
      showToast("Opening your prepared file in Snapmaker Orca…");
    } catch (e) {
      if (String((e as Error)?.message ?? e).includes("orca-not-found")) setOrca(null);
      showToast(orcaErrorMessage(e));
    } finally {
      setOpening(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-1.5">
      {orca === undefined ? (
        <Button disabled>
          <Loader2 className="h-4 w-4 animate-spin" /> Checking for Snapmaker Orca…
        </Button>
      ) : orca ? (
        <Button onClick={open} disabled={opening}>
          {opening ? <Loader2 className="h-4 w-4 animate-spin" /> : <Rocket className="h-4 w-4" />}
          {opening ? "Opening…" : "Open in Snapmaker Orca"}
        </Button>
      ) : (
        <Button variant="secondary" asChild>
          <a href={ORCA_RELEASES_URL} target="_blank" rel="noreferrer">
            <Download className="h-4 w-4" /> Install Snapmaker Orca
          </a>
        </Button>
      )}
      <p className="text-xs text-muted-foreground">{ORCA_HANDOFF_LINE}</p>
      <div className="mt-1 rounded-md border border-border bg-muted/20 p-2 text-xs text-muted-foreground">
        <p>
          <span className="font-medium text-foreground">Next:</span> slice in Snapmaker Orca, export the{" "}
          <span title="The .gcode file is the printer-ready file Snapmaker Orca creates after slicing."
            className="cursor-help underline decoration-dotted">.gcode</span>{" "}
          file, then return to{" "}
          <Link to="/printers" className="inline-flex items-center gap-0.5 text-primary hover:underline">
            Printer Hub <ArrowRight className="h-3 w-3" />
          </Link>{" "}
          and upload it. (Studio doesn't slice — Snapmaker Orca does.)
        </p>
      </div>
    </div>
  );
}
