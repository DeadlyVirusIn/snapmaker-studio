import { Sun, Moon, FolderOpen, Info, Sparkles, SlidersHorizontal, Printer, ShieldCheck } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/store/theme";
import { useMode } from "@/store/mode";
import { usePrinter } from "@/store/printer";

function Row({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div>
        <p className="text-sm font-medium">{label}</p>
        {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
      </div>
      {children}
    </div>
  );
}

export default function Settings() {
  const { theme, set } = useTheme();
  const { mode, setMode } = useMode();
  const { host, setHost } = usePrinter();
  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-2xl font-semibold tracking-tight">Settings</h2>

      <Card>
        <CardContent className="divide-y divide-border p-5">
          <p className="flex items-center gap-2 pb-2 text-sm font-semibold"><Printer className="h-4 w-4" /> Printer</p>
          <Row label="Your Snapmaker U1" hint="Network name or IP. Used by the Printer Hub to show live status.">
            <input
              value={host}
              onChange={(e) => setHost(e.target.value)}
              placeholder="U1.local"
              className="h-9 w-40 rounded-md border border-border bg-card px-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-primary/50"
            />
          </Row>
          <Row label="Printer access" hint="Studio only reads status — it never uploads, starts prints, or changes settings.">
            <span className="inline-flex items-center gap-1 text-sm text-ready"><ShieldCheck className="h-4 w-4" /> Read-only</span>
          </Row>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="divide-y divide-border p-5">
          <p className="pb-2 text-sm font-semibold">Experience</p>
          <Row label="Mode" hint="Simple is friendly and guided. Advanced shows every tool and detail.">
            <div className="flex gap-1">
              <Button variant={mode === "simple" ? "primary" : "secondary"} size="sm" onClick={() => setMode("simple")}>
                <Sparkles className="h-4 w-4" /> Simple
              </Button>
              <Button variant={mode === "advanced" ? "primary" : "secondary"} size="sm" onClick={() => setMode("advanced")}>
                <SlidersHorizontal className="h-4 w-4" /> Advanced
              </Button>
            </div>
          </Row>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="divide-y divide-border p-5">
          <p className="pb-2 text-sm font-semibold">Appearance</p>
          <Row label="Theme" hint="Match the look to your environment.">
            <div className="flex gap-1">
              <Button variant={theme === "light" ? "primary" : "secondary"} size="sm" onClick={() => set("light")}>
                <Sun className="h-4 w-4" /> Light
              </Button>
              <Button variant={theme === "dark" ? "primary" : "secondary"} size="sm" onClick={() => set("dark")}>
                <Moon className="h-4 w-4" /> Dark
              </Button>
            </div>
          </Row>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="divide-y divide-border p-5">
          <p className="pb-2 text-sm font-semibold">Files</p>
          <Row label="Where U1 files are saved" hint="Converted projects are saved right next to the file you opened.">
            <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground"><FolderOpen className="h-4 w-4" /> Beside your original</span>
          </Row>
          <Row label="Keep originals" hint="Never overwrite source files.">
            <span className="text-sm text-muted-foreground">Always on</span>
          </Row>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-5">
          <div className="flex items-center gap-2 text-sm font-semibold"><Info className="h-4 w-4" /> About</div>
          <div className="mt-2 space-y-1 text-sm text-muted-foreground">
            <p>Snapmaker Studio · v0.3.0-beta.2</p>
            <p>Local-first. No account, no cloud — nothing leaves your computer.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
