import { useState } from "react";
import { Download, RefreshCw, ShieldCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { checkForUpdate } from "@/api";
import type { UpdateInfo } from "@/api";

/**
 * Checking for a newer release.
 *
 * Studio is local-first, and this is the single exception: one outbound request
 * to GitHub's releases API, made only when someone presses this button. It sends
 * nothing but the request — no identifiers, no usage, no telemetry — and Studio
 * never downloads or installs anything on its own. The answer is a version number
 * and a link.
 */
export function UpdateCheck() {
  const [info, setInfo] = useState<UpdateInfo | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <Card>
      <CardContent className="space-y-3 p-5">
        <div>
          <h3 className="flex items-center gap-2 text-sm font-semibold">
            <RefreshCw className={`h-4 w-4 ${busy ? "animate-spin" : ""}`} aria-hidden="true" />
            Check for a newer version
          </h3>
          <p className="mt-0.5 text-xs text-muted-foreground">
            Studio does not check on its own and never updates itself.
          </p>
        </div>

        <p className="flex items-start gap-2 rounded-md border border-border bg-muted/20 p-2.5 text-xs text-muted-foreground">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <span>
            Pressing this makes one request to GitHub asking which release is newest.
            It sends nothing about you or your files.
          </span>
        </p>

        <Button
          disabled={busy}
          onClick={() => {
            setBusy(true);
            setError(null);
            checkForUpdate()
              .then(setInfo)
              .catch((e) => setError(String(e)))
              .finally(() => setBusy(false));
          }}
        >
          Check GitHub now
        </Button>

        {error && (
          <p className="text-xs text-risk">
            Studio could not reach GitHub. You are offline, or it is unavailable —
            nothing is wrong with your installation.
          </p>
        )}

        {info && !error && (
          info.newer ? (
            <div className="rounded-md border border-ready/40 p-2.5">
              <p className="text-sm font-medium">
                Version {info.latest} is available — you have {info.current}.
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Download it yourself and install over the top; your settings and
                library are kept.
              </p>
              <a
                className="mt-2 inline-flex items-center gap-1.5 text-xs underline"
                href={info.url}
                target="_blank"
                rel="noreferrer"
              >
                <Download className="h-3.5 w-3.5" aria-hidden="true" />
                Open the release page
              </a>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">
              You have {info.current}, which is the newest release.
            </p>
          )
        )}
      </CardContent>
    </Card>
  );
}
