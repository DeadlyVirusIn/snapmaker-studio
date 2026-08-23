import { useEffect, useState } from "react";
import { History, Loader2, Undo2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { fixHistory, fixOriginal } from "@/api";
import type { FixEntry, FixOriginal } from "@/api";
import { useSession } from "@/store/session";
import { useToast } from "@/store/toast";
import {
  LEDGER_NOTE,
  LEDGER_TITLE,
  changeLine,
  entrySubtitle,
  returnState,
  visibleEntries,
} from "@/lib/fixLedger";

/**
 * "Changes Studio made" — and the way back.
 *
 * Studio's loop is Diagnose → Explain → Fix → Validate → Undo, and the last step
 * used to mean "go and find your original file". Every Studio-generated file now
 * has a record: what was done, what triggered it, each change with its old and
 * new value, and whether the result validated.
 *
 * Returning to the original does not reverse the prepared copy. The original was
 * never written to, so this points the workflow back at a file that has been
 * sitting there untouched — which is both safer and easier to explain.
 */
export function FixLedgerCard({ source, output }: { source: string; output?: string }) {
  const showToast = useToast((s) => s.show);
  const openFile = useSession((s) => s.setFile);
  const [entries, setEntries] = useState<FixEntry[] | null>(null);
  const [original, setOriginal] = useState<FixOriginal | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let alive = true;
    setEntries(null);
    setFailed(false);
    fixHistory(source).then(
      (r) => { if (alive) setEntries(r.entries); },
      () => { if (alive) setFailed(true); },
    );
    return () => { alive = false; };
  }, [source]);

  useEffect(() => {
    let alive = true;
    setOriginal(null);
    if (!output) return;
    fixOriginal(output).then(
      (r) => { if (alive) setOriginal(r); },
      () => { if (alive) setOriginal(null); },
    );
    return () => { alive = false; };
  }, [output]);

  if (failed) return null;

  const list = visibleEntries(entries ?? undefined);
  if (entries && list.length === 0) return null;

  const back = returnState(original);

  return (
    <Card className="text-left">
      <CardContent className="space-y-3 p-5">
        <h3 className="flex items-center gap-2 text-sm font-semibold">
          {entries ? (
            <History className="h-4 w-4 text-primary" aria-hidden="true" />
          ) : (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          )}
          {LEDGER_TITLE}
        </h3>

        <ol className="space-y-2">
          {list.map((entry, index) => (
            <li key={`${entry.output_name}-${entry.timestamp}`}
                className="rounded-md border border-border p-2.5">
              <p className="text-sm font-medium">
                {index + 1}. {entry.title}
              </p>
              <p className="text-[11px] text-muted-foreground">{entrySubtitle(entry)}</p>

              {entry.findings.length > 0 && (
                <p className="mt-1 text-xs text-muted-foreground">
                  Because: {entry.findings.map((f) => f.title).filter(Boolean).join("; ")}
                </p>
              )}

              {entry.changes.length > 0 && (
                <details className="mt-1">
                  <summary className="cursor-pointer text-[11px] text-muted-foreground hover:text-foreground">
                    Before and after
                  </summary>
                  <ul className="mt-1 space-y-0.5">
                    {entry.changes.slice(0, 20).map((change, i) => (
                      <li key={`${change.key}-${i}`} className="text-[11px] text-muted-foreground">
                        <span className="break-all">{changeLine(change)}</span>
                        {change.reason && <span> — {change.reason}</span>}
                      </li>
                    ))}
                    {entry.changes.length > 20 && (
                      <li className="text-[11px] text-muted-foreground">
                        …and {entry.changes.length - 20} more
                      </li>
                    )}
                  </ul>
                </details>
              )}
            </li>
          ))}
        </ol>

        {output && (
          <div className="space-y-1">
            <Button
              size="sm"
              variant="secondary"
              disabled={!back.enabled}
              onClick={() => {
                if (!original?.source_path) return;
                openFile(original.source_path);
                showToast(`Back to ${original.source_name} — your original, untouched.`);
              }}
            >
              <Undo2 className="h-3.5 w-3.5" /> {back.label}
            </Button>
            {back.explanation && (
              <p className="text-[11px] text-muted-foreground">{back.explanation}</p>
            )}
          </div>
        )}

        <p className="text-[11px] text-muted-foreground">{LEDGER_NOTE}</p>
      </CardContent>
    </Card>
  );
}
