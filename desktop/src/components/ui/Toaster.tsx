import { useEffect } from "react";
import { Sparkles, X } from "lucide-react";
import { useToast } from "@/store/toast";

export function Toaster() {
  const { message, seq, hide } = useToast();

  // Auto-dismiss 2.6s after each new message (keyed by seq).
  useEffect(() => {
    if (!message) return;
    const t = setTimeout(hide, 2600);
    return () => clearTimeout(t);
  }, [seq, message, hide]);

  if (!message) return null;

  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-10 z-50 flex justify-center px-4">
      <div className="pointer-events-auto flex items-center gap-2.5 rounded-lg border border-border bg-card px-4 py-2.5 text-sm shadow-lg animate-in fade-in slide-in-from-bottom-2">
        <Sparkles className="h-4 w-4 text-primary" />
        <span>{message}</span>
        <button onClick={hide} className="ml-1 text-muted-foreground hover:text-foreground" aria-label="Dismiss">
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
