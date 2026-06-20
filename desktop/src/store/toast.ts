import { create } from "zustand";

interface ToastState {
  message: string | null;
  seq: number;
  show: (message: string) => void;
  hide: () => void;
}

// Minimal in-memory toast. `seq` lets the Toaster reset its auto-dismiss
// timer whenever a new message fires.
export const useToast = create<ToastState>((set, get) => ({
  message: null,
  seq: 0,
  show: (message) => set({ message, seq: get().seq + 1 }),
  hide: () => set({ message: null }),
}));
