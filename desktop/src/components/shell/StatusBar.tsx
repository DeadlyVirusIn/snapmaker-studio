import { useQuery } from "@tanstack/react-query";
import { health } from "@/api";

export function StatusBar() {
  // Reflect the real sidecar state instead of a hardcoded "ready" dot.
  const { status } = useQuery({ queryKey: ["health"], queryFn: health, refetchInterval: 10000, retry: 1 });
  const online = status === "success";
  return (
    <footer className="flex h-7 items-center gap-4 border-t border-border bg-card px-4 text-[11px] text-muted-foreground">
      <span className="flex items-center gap-1.5" title={online ? "Local engine running" : status === "pending" ? "Local engine starting" : "Local engine not responding"}>
        <span className={`h-1.5 w-1.5 rounded-full ${online ? "bg-ready" : status === "pending" ? "bg-repairable" : "bg-risk"}`} />
        {online ? "Ready" : status === "pending" ? "Starting up…" : "Reconnecting…"}
      </span>
      <span>v0.4.0-beta.1</span>
      <span className="ml-auto">Local-only · nothing leaves your computer</span>
    </footer>
  );
}
