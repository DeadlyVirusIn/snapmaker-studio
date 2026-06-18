import { Sun, Moon, FolderOpen, Info } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/store/theme";
import { comingSoon } from "@/store/toast";

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
  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-2xl font-semibold tracking-tight">Settings</h2>

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
          <Row label="Default output folder" hint="Where converted U1 projects are saved.">
            <Button variant="secondary" size="sm" onClick={() => comingSoon("Choose output folder")}>
              <FolderOpen className="h-4 w-4" /> Choose…
            </Button>
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
            <p>Snapmaker Studio · v0.3.0-beta.1</p>
            <p>Local-first. No account, no cloud — nothing leaves your computer.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
