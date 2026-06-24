// Trusted Studio-side control surface for the locked Model Browser window.
// The remote approved-site page stays in an isolated, no-IPC Tauri window; every
// control lives here in trusted Studio UI. No scraping, no auto-import, no API keys.

export const MODEL_BROWSER_COPY = {
  flow: "Browse in the Studio Model Browser. Download the STL/3MF from the site. Then open it here and run Project Doctor.",
  openTitle: "Model Browser is open",
  closedHint: "Pick a site above to open it in the Studio Model Browser.",
  trust:
    "Approved sites only, in a locked Studio-owned window. Studio never scrapes, " +
    "imports, or bypasses a site's login or terms — and no API keys are needed.",
} as const;

export interface BrowserPanelState {
  open: boolean;
  site: string | null; // human label of the site currently open in-app
}

export const closedPanel: BrowserPanelState = { open: false, site: null };

/** Heading for the control panel, reflecting the live window state. */
export function panelLabel(s: BrowserPanelState): string {
  return s.open && s.site
    ? `Model Browser is open — browsing ${s.site}`
    : "Model Browser is closed";
}

/** Show the trusted control panel only once a site has been opened in-app. */
export function showPanel(s: BrowserPanelState): boolean {
  return s.open;
}
