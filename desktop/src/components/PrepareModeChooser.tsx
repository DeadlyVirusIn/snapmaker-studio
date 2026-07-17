import type { PrepareMode } from "@/api";
import { Card, CardContent } from "@/components/ui/card";

interface Props {
  mode: PrepareMode;
  onModeChange: (mode: PrepareMode) => void;
  onCustom: () => void;
  previewing?: boolean;
}

export function PrepareModeChooser({ mode, onModeChange, onCustom, previewing = false }: Props) {
  return (
    <Card>
      <CardContent className="space-y-3 p-4">
        <div>
          <h3 className="text-sm font-semibold">Preparation mode</h3>
          <p className="mt-1 text-xs text-muted-foreground">Studio will make a U1 profile copy; review in Orca before slicing.</p>
        </div>
        <label className="flex cursor-pointer items-start gap-2 rounded-md border p-3">
          <input type="radio" name="prepare-mode" checked={mode === "preserve"} onChange={() => onModeChange("preserve")} />
          <span><span className="block text-sm font-medium">Preserve creator settings</span><span className="block text-xs text-muted-foreground">Keep the creator&apos;s slicer settings where possible. Studio only changes the minimum U1 project wrapper fields needed for Snapmaker Orca.</span></span>
        </label>
        <label className="flex cursor-pointer items-start gap-2 rounded-md border p-3">
          <input type="radio" name="prepare-mode" checked={mode === "recommended"} onChange={() => onModeChange("recommended")} />
          <span><span className="block text-sm font-medium">Apply Studio recommended U1 settings</span><span className="block text-xs text-muted-foreground">Use Studio&apos;s recommended U1 starter settings. This can change speed, temperature, retraction, supports, cooling, and other print behavior.</span></span>
        </label>
        <div className="flex items-center justify-between rounded-md border p-3">
          <span><span className="block text-sm font-medium">Custom</span><span className="block text-xs text-muted-foreground">Review settings before preparing.</span></span>
          <button type="button" className="text-sm font-medium text-primary hover:underline" onClick={onCustom} disabled={previewing}>{previewing ? "Reviewing…" : "Review settings"}</button>
        </div>
      </CardContent>
    </Card>
  );
}
