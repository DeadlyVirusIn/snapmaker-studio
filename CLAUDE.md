# Snapmaker Studio — project guidance

Snapmaker Studio is the local-first **pre-print intelligence layer** for the Snapmaker U1.
Independent open-source project — not affiliated with or endorsed by Snapmaker.

## What it is

Reads a 3D model's real geometry, runs read-only "Doctors" that explain likely print risks
in plain language, prepares a U1 profile copy (review in Orca before slicing) without
modifying the original, hands that copy to Snapmaker Orca to slice, and monitors / sends
to the U1 via Printer Hub.

## Hard rules (do not break these in code, copy, or docs)

- **Studio does not slice** — Snapmaker Orca does. One-way handoff only.
- **Studio never takes autonomous control.** Printer Hub provides local, user-confirmed
  actions (monitor, send, pause, resume, cancel); it never auto-starts a print.
- **Local-first.** No cloud, no account, nothing uploaded.
- **Originals are never modified** — preparing a model always writes a new copy.
- **Advisory, not guarantees.** Never claim "100% print success" or a guaranteed print.
- **No secrets** in the repo (tokens, keys, credentials). **No private data** (real IPs,
  hostnames, local paths, usernames, or private/copyrighted model names) in tracked files
  or screenshots — anonymize proof data.
- **Release safety: never force-kill `snapmaker-orca`, printer, slicer, or user GUI
  processes without explicit approval from the maintainer.** Only terminate processes you
  started yourself (track the PID); check a process's start time / owner before
  touching anything else.

## Positioning & priorities

Positioning: **"The Intelligence Layer for Open 3D Printing."**
Priorities: Project Doctor, Printer Doctor, Cost Doctor, beginner clarity, judge-ready polish.
UI work must be verified with real screenshots (anonymized per hard rules) — never claim UI works unseen.

## Commands (verified against manifests 2026-07-05)

```bash
# desktop/ (Tauri 2 + React 18 + Vite 5 + TS)
npm run dev              # vite dev server
npm run build            # tsc && vite build
npm run test             # vitest run
npm run build:sidecar    # pwsh ./scripts/build-sidecar.ps1
npm run release:windows  # build:sidecar && tauri build

# backend/ (Python >=3.13, pytest, CLI: u1convert)
pytest                   # testpaths: tests
```

Run `npm run test` (desktop) and `pytest` (backend) before declaring any change done.

## Layout

- `desktop/` — Tauri + React app (UI, Printer Hub, Doctors).
- `backend/` — Python engine + local service (`snapstudio_core`, `snapstudio_api`).
- `docs/` — public docs, judge/submission package, verification records.

Current release: see the GitHub Releases page (latest is the submitted beta).
