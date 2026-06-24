// Printer Hub Phase B — pure control-gating logic (no I/O), so the safety rules are
// unit-testable. The UI uses these to decide which buttons show and which actions
// require an explicit confirmation before the backend relays them to the printer.

export type PrintState =
  | "standby" | "printing" | "paused" | "complete" | "cancelled" | "error" | "unknown";

export type ControlAction = "start" | "pause" | "resume" | "cancel" | "emergency_stop";

// Actions that move the machine in a way that needs an explicit user confirmation.
// Start + cancel + emergency-stop always confirm; pause/resume are reversible and safe.
const CONFIRM: Record<ControlAction, boolean> = {
  start: true, cancel: true, emergency_stop: true, pause: false, resume: false,
};

export function needsConfirm(action: ControlAction): boolean {
  return CONFIRM[action];
}

const IDLE: PrintState[] = ["standby", "complete", "cancelled", "error", "unknown"];

/** Which control actions are valid right now. Offline → none (controls are blocked). */
export function availableActions(state: PrintState, online: boolean): ControlAction[] {
  if (!online) return [];
  const out: ControlAction[] = [];
  if (IDLE.includes(state)) out.push("start");
  if (state === "printing") out.push("pause", "cancel");
  if (state === "paused") out.push("resume", "cancel");
  // Emergency stop is available whenever the printer is reachable.
  out.push("emergency_stop");
  return out;
}

export function canStart(state: PrintState, online: boolean): boolean {
  return availableActions(state, online).includes("start");
}

/** Confirmation copy shown before a machine-moving action. No false guarantees. */
export function confirmCopy(action: ControlAction, filename?: string): { title: string; body: string; danger: boolean } {
  switch (action) {
    case "start":
      return {
        title: `Start printing ${filename ?? "this file"}?`,
        body: "Only start a print if the U1 is clear, loaded, and ready. Studio does not check the bed for you.",
        danger: false,
      };
    case "cancel":
      return {
        title: "Cancel this print?",
        body: "This stops the job on the printer. You can't resume a cancelled print.",
        danger: true,
      };
    case "emergency_stop":
      return {
        title: "EMERGENCY STOP",
        body: "Emergency stop halts motion/heaters and may require a firmware restart before printing again.",
        danger: true,
      };
    default:
      return { title: "", body: "", danger: false };
  }
}

/** Normalize a Moonraker print_stats.state into our enum. */
export function toPrintState(s: string | null | undefined): PrintState {
  const v = (s ?? "").toLowerCase();
  const known: readonly string[] = ["standby", "printing", "paused", "complete", "cancelled", "error"];
  return known.includes(v) ? (v as PrintState) : "unknown";
}
