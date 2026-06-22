# Production-readiness triage (audit-hardening sprint)

Each remaining audit issue mapped to an action class.

## Fix now (safe, scoped)
- **CORS `*` on loopback** (`server.py:70`) → tighten to local origins, keep token-gated POST.
- **No SQLite schema version / migration** (`library.py`) → add `PRAGMA user_version` + migration scaffold (v1).
- **No local crash/error visibility** → opt-in local diagnostic log with redaction + size cap.
- **TS↔Python contract drift** → fixture-based contract guard for key endpoints.
- **Stale-sidecar if bare `tauri build` bypassed** → docs reference only `release:windows`/`release.yml`; add a release-build guard hint.
- **Test gaps** → corrupt/malformed input, concurrency, no-write assertions, known-good no-blame.
- **Minor forward-compat nits** → schema_version in TS types, printer/symptom params, speed-evidence edge, drop `path:"none"` sentinel.

## Document / pre-GA blocker (no risky change)
- **CSP disabled + renderer token exposure** (`tauri.conf.json:16`) → keep documented in `SECURITY.md`/`RELEASE_CHECKLIST.md`; implement only when the GUI can be interactively smoke-tested. NOT claimed fixed.
- **Plate Remap regex XML parser** (`plate_remap.py`) → writer untouched; add read-only equivalence tests only. Full lxml writer stays deferred (needs byte-equivalence proof).

## External blocker (needs purchase/account)
- **Windows code signing** — requires a code-signing certificate. Tracked in `windows-code-signing.md`.

## Deferred with reason
- **Plate Remap lxml *writer*** — reserialization could change `model_settings.config` bytes; needs Orca-compat equivalence proof before touching the verified writer.
- **Plate Remap 3D preview** — colour/part fallback shipped; full 3D is a feature, not hardening.
