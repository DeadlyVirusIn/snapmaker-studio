import { Search, Sun, Moon, FolderOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/store/theme";
import { comingSoon } from "@/store/toast";
import { useOpenFile } from "@/hooks/useOpenFile";

export function TopBar({ title }: { title: string }) {
  const { theme, toggle } = useTheme();
  const openFile = useOpenFile();
  return (
    <header className="flex h-14 items-center gap-3 border-b border-border bg-background px-4">
      <h1 className="text-sm font-medium text-muted-foreground">{title}</h1>
      <div className="ml-auto flex items-center gap-2">
        <button onClick={() => comingSoon("Search")} className="flex h-9 items-center gap-2 rounded-md border border-border bg-card px-3 text-sm text-muted-foreground hover:bg-muted">
          <Search className="h-4 w-4" />
          <span className="hidden sm:inline">Search…</span>
          <kbd className="hidden sm:inline rounded bg-muted px-1.5 text-[10px]">⌘K</kbd>
        </button>
        <Button variant="secondary" size="sm" onClick={openFile}>
          <FolderOpen className="h-4 w-4" /> Open
        </Button>
        <Button variant="ghost" size="icon" onClick={toggle} aria-label="Toggle theme">
          {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </div>
    </header>
  );
}
