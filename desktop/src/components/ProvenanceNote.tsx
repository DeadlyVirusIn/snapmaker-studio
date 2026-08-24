import { CheckCircle2, HelpCircle, XCircle } from "lucide-react";
import type { Provenance, ProvenanceEvidence, ProvenanceResult } from "@/api";

/**
 * Why Studio thinks this G-code is (or is not) the slice of the open project.
 *
 * Every check on the page after this one describes a job. If the job is not the
 * one the user has in mind, those checks answer the wrong question — confidently,
 * which is worse than not answering. So the verdict is shown wherever it matters,
 * and the reasoning is one click away rather than a black box.
 *
 * The evidence is grouped the way the engine weighs it, because the grouping *is*
 * the explanation: what identifies the model, and what merely describes the setup
 * it was sliced with. "The printer and the filaments match" sounds like proof and
 * is true of every job in a workshop, and a person can see that for themselves
 * once the two kinds are not mixed together.
 *
 * Object names are never shown — the engine compares hashes of them, so there is
 * nothing here to leak a model name into a screenshot.
 */
export function verdictLabel(verdict: Provenance | undefined): string {
  switch (verdict) {
    case "confirmed":
      return "This is your project, sliced";
    case "likely":
      return "Looks like your project";
    case "no_match":
      return "A different project";
    case "ambiguous":
      return "Studio can't tell";
    default:
      return "Not enough to compare";
  }
}

export function verdictTone(verdict: Provenance | undefined): "ready" | "risk" | "muted" {
  if (verdict === "confirmed" || verdict === "likely") return "ready";
  if (verdict === "no_match") return "risk";
  return "muted";
}

function kindWord(kind: ProvenanceEvidence["kind"]): string {
  if (kind === "identity") return "identifies the model";
  if (kind === "profile") return "describes the setup";
  return "circumstantial";
}

export function ProvenanceNote({ result, compact = false }: {
  result: ProvenanceResult; compact?: boolean;
}) {
  const tone = verdictTone(result.verdict);
  const Icon = tone === "ready" ? CheckCircle2 : tone === "risk" ? XCircle : HelpCircle;
  const identity = result.evidence.filter((e) => e.kind === "identity");
  const rest = result.evidence.filter((e) => e.kind !== "identity");

  return (
    <div className={compact ? "" : "rounded-md border border-border p-2.5"}>
      <p className="flex items-center gap-1.5 text-xs">
        <Icon
          className={`h-3.5 w-3.5 shrink-0 ${
            tone === "ready" ? "text-ready" : tone === "risk" ? "text-risk" : "text-muted-foreground"
          }`}
          aria-hidden="true"
        />
        <span className="font-medium">{verdictLabel(result.verdict)}</span>
      </p>
      {result.why && <p className="mt-1 text-[11px] text-muted-foreground">{result.why}</p>}

      <details className="mt-1">
        <summary className="cursor-pointer text-[11px] text-muted-foreground hover:text-foreground">
          What Studio compared
        </summary>
        <EvidenceList
          title="Identifies the model"
          items={identity}
          empty="Nothing in either file identifies the model itself."
        />
        <EvidenceList title="Describes the setup" items={rest} />
        <p className="mt-1.5 text-[11px] text-muted-foreground">
          Studio compares fingerprints of the object names, never the names themselves.
        </p>
      </details>
    </div>
  );
}

function EvidenceList({ title, items, empty }: {
  title: string; items: ProvenanceEvidence[]; empty?: string;
}) {
  if (!items.length && !empty) return null;
  return (
    <div className="mt-1.5">
      <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{title}</p>
      {items.length === 0 ? (
        <p className="text-[11px] text-muted-foreground">{empty}</p>
      ) : (
        <ul className="mt-0.5 flex flex-col gap-0.5">
          {items.map((item) => (
            <li key={item.signal} className="text-[11px] text-muted-foreground">
              <span className={item.weight < 0 ? "text-risk" : ""}>
                {item.label ?? item.signal}
              </span>
              {" — "}
              {item.detail}
              <span className="ml-1 text-[10px] opacity-70">({kindWord(item.kind)})</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
