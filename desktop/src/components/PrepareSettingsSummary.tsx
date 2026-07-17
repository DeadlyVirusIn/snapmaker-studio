import type { SettingsChange, SettingsSummary } from "@/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

function value(value: unknown) {
  const text = typeof value === "string" ? value : JSON.stringify(value);
  return (text ?? String(value)).slice(0, 80);
}

function Changes({ changes }: { changes: SettingsChange[] }) {
  return <ul className="space-y-1 text-xs text-muted-foreground">{changes.map((change) => <li key={change.key} className="grid grid-cols-[minmax(0,1fr)_auto_minmax(0,1fr)] gap-1"><span className="truncate font-mono">{change.key}</span><span>:</span><span className="truncate">{value(change.old)} → {value(change.new)}</span></li>)}</ul>;
}

export const STARTER_NOTICE = "This STL does not include creator slicer settings. Studio will use a U1 starter profile unless you choose another Orca profile.";

interface Props {
  summary: SettingsSummary;
  mode: "preserve" | "recommended" | "starter";
  preview?: boolean;
  onPreparePreserve?: () => void;
  onPrepareRecommended?: () => void;
}

export function PrepareSettingsSummary({ summary, mode, preview = false, onPreparePreserve, onPrepareRecommended }: Props) {
  if (mode === "starter" || !summary.source_has_creator_settings) {
    return <Card><CardContent className="p-4 text-sm text-muted-foreground">{summary.warnings[0] ?? STARTER_NOTICE}</CardContent></Card>;
  }
  return (
    <Card>
      <CardContent className="space-y-4 p-4">
        {preview && <p className="text-sm font-medium">Settings preview</p>}
        <section><h3 className="text-sm font-semibold">Kept from the original file</h3><p className="text-xs text-muted-foreground">{summary.kept_count} creator settings kept</p><p className="mt-1 text-xs text-muted-foreground">These settings are kept from the original file.</p></section>
        <section><h3 className="text-sm font-semibold">Changed for U1 compatibility</h3><p className="mb-1 text-xs text-muted-foreground">These settings changed only for U1 compatibility.</p>{summary.compat_changed.length ? <Changes changes={summary.compat_changed} /> : <p className="text-xs text-muted-foreground">None</p>}</section>
        {summary.could_not_carry.length > 0 && <section><h3 className="text-sm font-semibold">Could not carry over</h3><ul className="space-y-1 text-xs text-muted-foreground">{summary.could_not_carry.map((item) => <li key={item.key}><span className="font-mono">{item.key}</span>: {item.reason}</li>)}</ul></section>}
        {mode === "preserve" && summary.recommendations_available && <section className="space-y-2"><h3 className="text-sm font-semibold">Optional recommendations (not applied)</h3><p className="text-xs text-muted-foreground">These optional recommendations are not applied unless you choose them.</p><Changes changes={summary.recommended_changes} />{onPrepareRecommended && <Button size="sm" variant="secondary" onClick={onPrepareRecommended}>Prepare another copy with recommended settings</Button>}</section>}
        {preview && <div className="flex flex-wrap gap-2">{onPreparePreserve && <Button size="sm" onClick={onPreparePreserve}>Prepare with preserved settings</Button>}{onPrepareRecommended && <Button size="sm" variant="secondary" onClick={onPrepareRecommended}>Prepare with recommended settings</Button>}</div>}
        {summary.warnings.map((warning) => <p key={warning} className="text-xs text-muted-foreground">{warning}</p>)}
      </CardContent>
    </Card>
  );
}
