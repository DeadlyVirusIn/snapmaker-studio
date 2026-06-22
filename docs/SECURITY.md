# Security model & hardening status

Snapmaker Studio is a local-first desktop app: a Tauri (Rust) shell + a webview UI
talking to a Python engine over **loopback HTTP only** (`127.0.0.1`). Nothing leaves
the machine; there is no account, cloud, or upload.

## Current protections
- **Loopback bind only** — the engine binds `127.0.0.1` (`server.py`, `ThreadingHTTPServer`); not reachable off-host.
- **Per-launch token** — a `secrets.token_hex(16)` token is generated each start, printed once as `{port, token}` on the sidecar's stdout, read by the Rust shell, and required on **every** POST (`X-Auth-Token`). Only `GET /health` is unauthenticated.
- **No-orphan lifecycle** — the sidecar is reaped on app exit via a Windows Job Object (`KILL_ON_JOB_CLOSE`) + parent-PID watch + `RunEvent::Exit`.
- **Input validation** — bad request input returns a sanitized HTTP 400; 500 bodies are generic (`internal error`), never raw tracebacks (`request_validation.py`).
- **Engine safety** — hardened lxml parser (entities/DTD/network off), GET-only outbound (printer probes), no `subprocess`/`eval`/`pickle`, parameterized SQL, provider API keys read from env server-side only, originals never mutated (verified safe-copy writers), report writes path-validated.

## Open pre-GA security blocker — Content Security Policy (NOT yet fixed)

`desktop/src-tauri/tauri.conf.json` sets `security.csp = null` (no CSP). The renderer
can obtain the sidecar token via the `get_api_info` Tauri command. Today the risk is
**limited** because the webview loads only local, bundled assets — no remote or
user-controlled HTML/script is ever loaded. But with no CSP, any script injected into
the renderer (e.g. via a future dependency or content-rendering bug) could call the
authenticated loopback API.

**Status: documented only — CSP is NOT implemented.** This must be hardened before any
**wider / signed public (GA) release**. It is acceptable for the current beta, whose
renderer is local-only.

Planned hardening (requires interactive GUI verification before merge):
- Set an explicit CSP in `tauri.conf.json`, roughly:
  - `default-src 'self'`
  - `script-src 'self'`
  - `style-src 'self' 'unsafe-inline'` (only if the app's styling needs it)
  - `img-src 'self' asset: http://asset.localhost data: blob:` (only as needed for icons/assets)
  - `connect-src 'self' http://127.0.0.1:* tauri:`
  - `object-src 'none'`, `frame-src 'none'`
- Then GUI-smoke: app launch, navigation, every sidecar API call, images/icons/theme.
- Optionally, proxy sidecar calls through Tauri commands so the token is never exposed to JS at all.

## Reporting
This is an independent open-source project (not affiliated with Snapmaker). Report
security issues via a GitHub issue marked security, or the repository contact.
