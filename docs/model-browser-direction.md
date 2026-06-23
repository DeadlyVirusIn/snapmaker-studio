# Model Discovery → "Model Browser" direction

Product decision: Model Discovery is an **approved-site browser**, not an
API-key search. Beginners browse trusted 3D-model sites, download an STL/3MF from
the site, then open it in Studio. No API keys in the beginner flow, no scraping,
no import/download claims that aren't implemented.

> Independent open-source project — not affiliated with or endorsed by Snapmaker.

## Why

API-key setup confuses novices and most model sites don't offer an official
search API anyway. Browsing the real sites — where licenses, previews, and
download buttons already live — is simpler and respects each site's terms.

## Beginner experience (shipped)

Find Models now leads with:
- "Browse trusted model sites" — link-out buttons that open the site (with your
  search term) in the browser.
- "Got a downloaded file?" — Open downloaded file → Project Doctor.
- Plain copy: browse the site, download there, open in Studio.

Live in-app API search, filters, and the disabled "Import to Studio" control are
**Advanced-only** and clearly optional. No secret/API-key fields in the UI.

## Approved sites (allowlist)

Printables, Thingiverse, MyMiniFactory, Cults3D, Thangs, MakerWorld.

These are the only domains the Model Browser should ever navigate to. Anything
outside the allowlist opens in the user's external browser (or is blocked).

## Architecture (Tauri — confirmed)

The desktop app is **Tauri v2** (`desktop/src-tauri`, `tauri.conf.json`,
`tauri-plugin-dialog`). A future in-app Model Browser should be a **locked,
low-permission WebviewWindow**, separate from the main app webview:

- Navigation allowlist limited to the approved domains above; off-allowlist
  links open in the OS browser (or are denied), never inside the app window.
- No Node/Tauri API exposure to that webview (no `withGlobalTauri`, no IPC).
- Minimal filesystem/download permissions; the main app keeps its own.
- No injection that bypasses login, paywalls, or site restrictions.

## Download behavior

- **v1 (now):** manual. User downloads from the site; Studio's "Open downloaded
  file" picks the STL/3MF and routes it to Project Doctor on explicit action.
- **v2 (later, optional):** disclosed download interception — ask where to save
  (or a clearly-labeled Studio downloads folder), show progress, never silently
  fetch restricted/private content.

## Guardrails

- No scraping, mirroring, or re-hosting of models.
- No bypassing site terms, login, or paywalls.
- No "one-click download" or "import to Studio" copy unless actually implemented.
- API/provider keys (if ever added) live behind Advanced only, server-side, never
  in the frontend or app bundle.

## Status

**v1 shipped — the in-app Model Browser is live.** In Find Models, "Browse trusted
model sites" opens a dedicated, isolated Tauri WebviewWindow (label `model-browser`)
restricted to the approved domains. The allowlist is enforced in Rust
(`open_model_browser` validates the URL is https + on-allowlist; `on_navigation`
blocks any later off-allowlist top-level navigation). The browser window is granted
no capabilities, so remote pages have no Tauri IPC. In a plain browser (dev) it
falls back to a normal tab.

Download stays **manual** in v1: browse and download on the site, then "Open
downloaded file" → Project Doctor. Download interception is deferred to v2 — it is
not reliable cross-platform via WebView2/Tauri today. Third-party login redirects
(e.g. signing in with Google) navigate off-allowlist and are blocked in-app; sign
in on the site's own domain, or use those sites signed-out for browsing.
