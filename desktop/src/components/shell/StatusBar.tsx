export function StatusBar() {
  return (
    <footer className="flex h-7 items-center gap-4 border-t border-border bg-card px-4 text-[11px] text-muted-foreground">
      <span className="flex items-center gap-1.5">
        <span className="h-1.5 w-1.5 rounded-full bg-ready" /> Engine ready
      </span>
      <span>v0.3.0-beta.1</span>
      <span>Local-only</span>
      <span className="ml-auto">No files leave your computer</span>
    </footer>
  );
}
